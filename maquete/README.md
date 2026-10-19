# Maquete ao vivo (MAQ-01)

Mini escada rolante com ESP32 para a demonstração à banca da Motiva. O ESP32 lê 6 sensores e envia **1 leitura por segundo**. No site, a escada aparece na aba **Ao vivo** e num card **MAQ-01** no topo do Painel. O gêmeo digital (3D ou 2D) gira quando a esteira gira e para quando ela para. O status, o diagnóstico e a fila seguem as mesmas regras das 197 escadas.

```
 sensores ──> ESP32 ──Wi-Fi──> broker MQTT ──WebSocket──> site (aba Ao vivo)
                 └──────────── cabo USB (Web Serial) ─────> site
```

As 197 escadas simuladas continuam no painel. A maquete não entra nos totais delas.

## Três jeitos de testar

| Jeito | Precisa de | Quando usar |
| --- | --- | --- |
| **Simulador do site** | Nada | Ensaiar a apresentação ou como plano B. Na aba Ao vivo, escolha *Simulador*, toque em *Conectar* e use os botões de falha. |
| **Wokwi** | Navegador | Testar o firmware e a conexão MQTT antes de comprar peças. Veja a seção "Wokwi". |
| **Maquete real** | As peças da lista | Dia da banca. |

Também dá para testar o caminho MQTT sem ESP32, publicando dados falsos no broker:

```
pip install paho-mqtt
python teste/publicar_teste.py rolamento
```

## Formato da leitura

O mesmo JSON vai pelo Wi-Fi e pelo cabo USB:

```json
{"id":"MAQ-01","vib":1.82,"temp":48.3,"corr":21.4,"tens":379.6,"vel":0.500,"oleo":78.0}
```

| Campo | Variável | Unidade (escala de escada real) |
| --- | --- | --- |
| `vib` | Vibração | mm/s |
| `temp` | Temperatura do motor | °C |
| `corr` | Corrente | A |
| `tens` | Tensão | V |
| `vel` | Velocidade dos degraus | m/s |
| `oleo` | Nível de óleo | % |

## Conexão com o site

**Wi-Fi (MQTT):**
- O ESP32 publica em `broker.hivemq.com`, porta 1883, tópico `fiap/elevate/566910/maq01`.
- O site assina o mesmo tópico em `wss://broker.hivemq.com:8884/mqtt`. Esses campos já vêm preenchidos na aba Ao vivo.
- Se mudar o tópico no firmware, mude também no site.

**Cabo USB:**
- Ligue o ESP32 no computador.
- Na aba Ao vivo, escolha *Cabo USB*, toque em *Conectar* e escolha a porta.
- Funciona no Chrome ou no Edge do computador. Não precisa de internet.

**Regras e reconexão:**
- O site só lê os dados. Nenhum comando vai para a maquete (RN-07): o motor liga e para pelo botão da própria maquete.
- O site lembra a última fonte usada e reconecta sozinho ao abrir. O cabo USB só reconecta se a porta já tiver sido autorizada.

## Regras aplicadas a cada segundo

- **Status** (RN-01): os limites são os mesmos das 197 escadas.
  - Velocidade 0 vira CRÍTICO "Parada".
  - 5 s sem leitura vira CRÍTICO "Sem resposta do sensor".
- **Confirmação** (RN-02): um valor crítico só vira CRÍTICO se as 3 leituras anteriores também estiverem alteradas. Antes disso, aparece como "Leitura suspeita".
- **Tendência:** regressão das últimas 20 leituras. O site avisa "ALERTA em cerca de X s" antes do alarme.
- **Fila** (RN-03, RN-04): em ALERTA ou CRÍTICO, a maquete entra na fila com a pontuação da regra, como escada do grupo crítica.

## Lista de materiais

| Item | Para quê |
| --- | --- |
| ESP32 DevKit (38 pinos) | Lê os sensores e envia os dados |
| Acelerômetro MPU6050 | Vibração |
| Sensor DS18B20 (encapsulado) + resistor de 4,7 kΩ | Temperatura do motor |
| Módulo INA219 | Corrente e tensão do motor |
| Sensor óptico TCRT5000 ou sensor hall + ímã | Velocidade (pulsos da polia) |
| Potenciômetro de 10 kΩ | Nível de óleo do reservatório |
| Motor DC com redução (TT amarelo ou JGA25-370) | Move a esteira |
| Driver L298N (ou TB6612) | Aciona o motor |
| Fonte de 12 V e regulador LM2596 (12 V para 5 V) | Alimentação |
| Botão | Liga e para a esteira |
| MDF cortado a laser ou LEGO, correia ou esteira, degraus colados | Estrutura |

O custo estimado fica entre R$ 250 e R$ 400. Confira os preços antes de comprar.

## Ligações (maquete real)

| Peça | Pino do ESP32 |
| --- | --- |
| MPU6050 e INA219 (I2C) | SDA 21, SCL 22, 3V3, GND |
| DS18B20 (dados) | 4, com 4,7 kΩ para 3V3 |
| Sensor de velocidade | 27 |
| Potenciômetro do óleo | 34 |
| L298N: ENA, IN1, IN2 | 25, 26, 33 |
| Botão (para GND) | 14 |

**Corrente do motor:**
- O INA219 fica em série com a alimentação do motor: fonte 12 V → VIN+ → VIN− → L298N.
- O GND precisa ser comum entre o ESP32, a fonte e o driver.

## Firmware

**Pasta:** `firmware/elevate_maquete/`.

1. Na Arduino IDE, instale a placa **esp32** (Espressif).
2. Instale as bibliotecas:
   - PubSubClient
   - OneWire
   - DallasTemperature
   - Adafruit MPU6050
   - Adafruit INA219
   - Adafruit Unified Sensor
3. No topo do arquivo:
   - `SIMULACAO_WOKWI 0` para a maquete real (`1` é o modo Wokwi, com potenciômetros);
   - preencha `WIFI_SSID` e `WIFI_SENHA`.
4. Grave na placa "ESP32 Dev Module".

O código foi compilado com o core ESP32 2.0.17 nos dois modos, sem erros. Ainda não foi testado numa placa física.

## Calibração (maquete real)

A maquete é pequena. O firmware converte as medidas dela para a escala de uma escada real, para usar os mesmos limites do painel.

Com a esteira rodando normal, abra o Monitor Serial e ajuste no topo do código:

| Constante | O que ajustar |
| --- | --- |
| `PULSOS_NOMINAL` | Pulsos por segundo na velocidade normal. O site deve mostrar 0,50 m/s. |
| `MA_NOMINAL` | Corrente do motor rodando livre, em mA. O site deve mostrar ~21 A. |
| `V_NOMINAL` | Tensão da fonte. O site deve mostrar ~380 V. |
| `VIB_GANHO` | O site deve mostrar ~1,8 mm/s parado no lugar. Um peso fora do centro na polia deve passar de 4,5. |
| `TEMP_GANHO` | Cada 1 °C real acima do ambiente vale 3 °C na escala. Secador a ~15 cm deve passar de 80 °C. |

## Roteiro para a banca

| Ação na maquete | O que aparece no site |
| --- | --- |
| Ligar a maquete | BOM. Degraus girando no 3D a 0,50 m/s. |
| Prender um peso fora do centro na polia | Vibração sobe. Tendência, depois ALERTA "Desgaste de rolamento". |
| Frear a esteira com o dedo | Corrente sobe e velocidade cai. ALERTA e depois CRÍTICO "Atrito". A maquete entra na fila. |
| Secador de cabelo no motor | Temperatura sobe. "Superaquecimento do motor". |
| Girar o potenciômetro do óleo | ALERTA e depois CRÍTICO "Vazamento de óleo". O reservatório esvazia no 3D. |
| Apertar o botão de parada | CRÍTICO "Parada". O 3D para na hora. |
| Tirar o cabo do ESP32 | Em 5 s: CRÍTICO "Sem resposta do sensor". |

Leve o simulador como plano B. Se o Wi-Fi do local falhar, use o cabo USB. Se a maquete falhar, use o Simulador.

## Wokwi

1. Abra https://wokwi.com/projects/new/esp32.
2. Substitua o `sketch.ino` e o `diagram.json` pelos arquivos da pasta `wokwi/`.
3. Crie o arquivo `libraries.txt` com o conteúdo da pasta.
4. Clique em ▶. O Wokwi conecta no Wi-Fi `Wokwi-GUEST` e publica no broker público.

Os 5 potenciômetros representam, da esquerda para a direita:
- vibração
- corrente
- tensão
- velocidade
- nível de óleo

Os outros controles:
- **Temperatura:** clique no DS18B20 para mudar o valor.
- **Botão vermelho:** para e liga a esteira.

No site, use a aba Ao vivo, Wi-Fi (MQTT) e Conectar.
