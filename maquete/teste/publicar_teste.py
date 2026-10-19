"""Testa o site sem a maquete: publica leituras falsas no mesmo broker e tópico do ESP32.

Uso:
    pip install paho-mqtt
    python publicar_teste.py               # escada normal
    python publicar_teste.py rolamento     # vibração subindo até CRÍTICO
    (outras falhas: aquecimento, freio, oleo, parada)

No site: aba "Ao vivo" > Wi-Fi (MQTT) > Conectar.
"""
import json, random, sys, time
import paho.mqtt.client as mqtt

BROKER, PORTA = "broker.hivemq.com", 1883
TOPICO = "fiap/elevate/566910/maq01"          # igual ao firmware e ao campo "Tópico" do site
falha = sys.argv[1] if len(sys.argv) > 1 else "normal"

cli = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=f"elevate-teste-{random.randint(0, 99999)}")
cli.connect(BROKER, PORTA)
cli.loop_start()
print(f"Publicando em {BROKER} / {TOPICO} (falha: {falha}). Ctrl+C para parar.")
s = 0
try:
    while True:
        s += 1
        g = random.gauss
        d = {"id": "MAQ-01", "vib": 1.8 + g(0, .12), "temp": 48 + g(0, .3), "corr": 21 + g(0, .4),
             "tens": 380 + g(0, 1.5), "vel": 0.5 + g(0, .002), "oleo": 78 + g(0, .2)}
        if falha == "rolamento":   d["vib"] = min(9.5, 1.8 + 0.12 * s) + g(0, .15)
        if falha == "aquecimento": d["temp"] = min(104, 48 + 1.2 * s)
        if falha == "freio":       d["corr"] = min(41, 21 + 0.55 * s); d["vel"] = max(0.462, 0.5 - 0.0005 * s)
        if falha == "oleo":        d["oleo"] = max(8, 78 - 1.3 * s)
        if falha == "parada":      d.update(vel=0, corr=0.4, vib=0.1)
        msg = json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in d.items()})
        cli.publish(TOPICO, msg)
        print(msg)
        time.sleep(1)
except KeyboardInterrupt:
    pass
