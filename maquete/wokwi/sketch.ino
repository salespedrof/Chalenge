/*
  Elevate · Maquete ao vivo (MAQ-01)
  ESP32 lê os 6 sensores da mini escada e envia 1 leitura por segundo:
    - por Wi-Fi, num broker MQTT (o site assina o mesmo tópico por WebSocket);
    - pelo cabo USB, na serial (o site lê pelo Chrome/Edge com Web Serial).
  As duas saídas usam o mesmo JSON:
    {"id":"MAQ-01","vib":1.82,"temp":48.3,"corr":21.4,"tens":379.6,"vel":0.500,"oleo":78.0}

  O ESP32 só envia dados. O site não manda comandos para a maquete (RN-07):
  o motor liga e desliga pelo botão físico da própria maquete.

  SIMULACAO_WOKWI = 1  -> potenciômetros no lugar dos sensores (projeto Wokwi)
  SIMULACAO_WOKWI = 0  -> maquete real (MPU6050, DS18B20, INA219, sensor de velocidade)

  Bibliotecas (Gerenciador de Bibliotecas da Arduino IDE):
    PubSubClient (Nick O'Leary), OneWire, DallasTemperature
    Só para a maquete real: Adafruit MPU6050, Adafruit INA219, Adafruit Unified Sensor
*/
#define SIMULACAO_WOKWI 1

#include <WiFi.h>
#include <PubSubClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#if !SIMULACAO_WOKWI
  #include <Wire.h>
  #include <Adafruit_MPU6050.h>
  #include <Adafruit_INA219.h>
#endif

/* ---------------- configuração ---------------- */
const char* WIFI_SSID  = SIMULACAO_WOKWI ? "Wokwi-GUEST" : "NOME_DA_REDE";
const char* WIFI_SENHA = SIMULACAO_WOKWI ? ""            : "SENHA_DA_REDE";
const char* MQTT_HOST  = "broker.hivemq.com";   // broker público; o site usa wss://broker.hivemq.com:8884/mqtt
const int   MQTT_PORTA = 1883;
const char* TOPICO     = "fiap/elevate/566910/maq01"; // precisa ser igual ao campo "Tópico" do site
const char* ID_ESCADA  = "MAQ-01";

/* ---------------- pinos ---------------- */
const int PINO_DS18B20 = 4;    // temperatura do motor (com resistor de 4,7 kΩ para 3,3 V)
const int PINO_BOTAO   = 14;   // liga/para a esteira (botão para GND)
const int PINO_LED     = 2;    // LED da placa: pisca a cada envio
#if SIMULACAO_WOKWI
  const int POT_VIB = 34, POT_CORR = 35, POT_TENS = 32, POT_VEL = 33, POT_OLEO = 36;
#else
  // I2C: SDA 21, SCL 22 (MPU6050 0x68 e INA219 0x40 no mesmo barramento)
  const int PINO_VEL   = 27;   // sensor óptico TCRT5000 ou hall: 1 pulso por marca na polia
  const int PINO_OLEO  = 34;   // potenciômetro que representa o nível do reservatório
  const int MOTOR_PWM  = 25;   // ENA do driver L298N
  const int MOTOR_IN1  = 26;
  const int MOTOR_IN2  = 33;
#endif

/* ---------------- calibração da maquete ----------------
   A maquete é pequena; estes fatores convertem as medidas dela para a escala
   de uma escada real, para usar os mesmos limites do painel.
   Ajuste com a maquete rodando normal: o site deve mostrar ~1,8 mm/s, ~48 °C,
   ~21 A, ~380 V e 0,50 m/s. */
const float VIB_GANHO      = 6.0;   // RMS da aceleração (m/s²) -> mm/s equivalente
const float TEMP_BASE      = 48.0;  // temperatura equivalente com o motor frio
const float TEMP_GANHO     = 3.0;   // cada 1 °C real acima do ambiente vale 3 °C na escala da escada
const float MA_NOMINAL     = 180.0; // corrente do motor da maquete rodando livre (mA)
const float V_NOMINAL      = 12.0;  // tensão nominal da fonte da maquete (V)
const float PULSOS_NOMINAL = 6.0;   // pulsos por segundo com a esteira na velocidade normal
const int   PWM_MOTOR      = 170;   // velocidade normal do motor (0 a 255)

/* ---------------- estado ---------------- */
WiFiClient rede;
PubSubClient mqtt(rede);
OneWire oneWire(PINO_DS18B20);
DallasTemperature ds(&oneWire);
#if !SIMULACAO_WOKWI
  Adafruit_MPU6050 mpu;
  Adafruit_INA219 ina;
#endif

volatile unsigned long pulsos = 0;
bool rodando = true;
float tempAmbiente = NAN, tempUltima = NAN;
double somaA = 0, somaA2 = 0; unsigned long nA = 0;   // janela de vibração de 1 s
unsigned long tEnvio = 0, tAmostra = 0, tWifi = 0, tBotao = 0;

void IRAM_ATTR contaPulso(){ pulsos++; }

float lePot(int pino, float min, float max){ return min + (max - min) * analogRead(pino) / 4095.0; }

void aplicaMotor(){
#if !SIMULACAO_WOKWI
  digitalWrite(MOTOR_IN1, rodando ? HIGH : LOW);
  digitalWrite(MOTOR_IN2, LOW);
  analogWrite(MOTOR_PWM, rodando ? PWM_MOTOR : 0);
#endif
}

void conectaWifi(){
  if(WiFi.status() == WL_CONNECTED || millis() - tWifi < 5000) return;
  tWifi = millis();
  WiFi.begin(WIFI_SSID, WIFI_SENHA);
}

void conectaMqtt(){
  if(WiFi.status() != WL_CONNECTED || mqtt.connected()) return;
  static unsigned long tTentativa = 0;
  if(millis() - tTentativa < 3000) return;
  tTentativa = millis();
  String id = "esp32-elevate-" + String((uint32_t)ESP.getEfuseMac(), HEX);
  mqtt.connect(id.c_str());
}

void setup(){
  Serial.begin(115200);
  pinMode(PINO_LED, OUTPUT);
  pinMode(PINO_BOTAO, INPUT_PULLUP);
  ds.begin(); ds.setWaitForConversion(false); ds.requestTemperatures();
#if !SIMULACAO_WOKWI
  Wire.begin(21, 22);
  if(!mpu.begin()) Serial.println("# MPU6050 nao encontrado");
  mpu.setAccelerometerRange(MPU6050_RANGE_4_G);
  mpu.setFilterBandwidth(MPU6050_BAND_94_HZ);
  if(!ina.begin()) Serial.println("# INA219 nao encontrado");
  pinMode(PINO_VEL, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PINO_VEL), contaPulso, FALLING);
  pinMode(MOTOR_IN1, OUTPUT); pinMode(MOTOR_IN2, OUTPUT); pinMode(MOTOR_PWM, OUTPUT);
  aplicaMotor();
#endif
  WiFi.mode(WIFI_STA);
  mqtt.setServer(MQTT_HOST, MQTT_PORTA);
  conectaWifi();
  Serial.println("# Elevate MAQ-01 iniciada");
}

void loop(){
  conectaWifi(); conectaMqtt(); mqtt.loop();
  unsigned long agora = millis();

  // botão local: liga/para a esteira (o site nunca comanda)
  if(digitalRead(PINO_BOTAO) == LOW && agora - tBotao > 400){ tBotao = agora; rodando = !rodando; aplicaMotor(); }

  // vibração: amostra a 200 Hz e calcula o RMS no envio
#if !SIMULACAO_WOKWI
  if(agora - tAmostra >= 5){
    tAmostra = agora;
    sensors_event_t a, g, t; mpu.getEvent(&a, &g, &t);
    double m = sqrt(a.acceleration.x*a.acceleration.x + a.acceleration.y*a.acceleration.y + a.acceleration.z*a.acceleration.z);
    somaA += m; somaA2 += m*m; nA++;
  }
#endif

  if(agora - tEnvio < 1000) return;
  float dt = (agora - tEnvio) / 1000.0; tEnvio = agora;

  // temperatura (DS18B20, leitura sem bloquear)
  float tc = ds.getTempCByIndex(0); ds.requestTemperatures();
  if(tc > -100 && tc < 125){ tempUltima = tc; if(isnan(tempAmbiente)) tempAmbiente = tc; }

  float vib, corr, tens, vel, oleo, temp;
#if SIMULACAO_WOKWI
  vib  = lePot(POT_VIB, 0.5, 10.0);
  corr = lePot(POT_CORR, 0, 45);
  tens = lePot(POT_TENS, 320, 440);
  vel  = rodando ? lePot(POT_VEL, 0.40, 0.60) : 0;
  oleo = lePot(POT_OLEO, 0, 100);
  temp = isnan(tempUltima) ? NAN : tempUltima;          // no Wokwi o DS18B20 já mostra a temperatura direto
  if(!rodando){ corr = 0.4; vib = 0.1; }
#else
  double media = nA ? somaA / nA : 0, var = nA ? somaA2 / nA - media*media : 0;
  vib = sqrt(var > 0 ? var : 0) * VIB_GANHO; somaA = somaA2 = 0; nA = 0;
  noInterrupts(); unsigned long p = pulsos; pulsos = 0; interrupts();
  vel  = (p / dt) / PULSOS_NOMINAL * 0.50;
  corr = ina.getCurrent_mA() / MA_NOMINAL * 21.0;
  tens = (ina.getBusVoltage_V() + ina.getShuntVoltage_mV() / 1000.0) / V_NOMINAL * 380.0;
  oleo = lePot(PINO_OLEO, 0, 100);
  temp = isnan(tempUltima) ? NAN : TEMP_BASE + (tempUltima - tempAmbiente) * TEMP_GANHO;
#endif

  char json[200], tTxt[12];
  if(isnan(temp)) strcpy(tTxt, "null"); else dtostrf(temp, 0, 1, tTxt);
  snprintf(json, sizeof(json), "{\"id\":\"%s\",\"vib\":%.2f,\"temp\":%s,\"corr\":%.1f,\"tens\":%.1f,\"vel\":%.3f,\"oleo\":%.1f}",
           ID_ESCADA, vib, tTxt, corr, tens, vel, oleo);

  Serial.println(json);                       // cabo USB (Web Serial)
  if(mqtt.connected()) mqtt.publish(TOPICO, json);   // Wi-Fi (MQTT)
  digitalWrite(PINO_LED, !digitalRead(PINO_LED));
}
