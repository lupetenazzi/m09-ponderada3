import time
import random
import network
import urequests
import json

WIFI_SSID = "SSID"
WIFI_PASSWORD = "Senha"
BACKEND_URL = "http://localhost:8080/telemetry"
DEVICE_ID = "pico-w-01"

historico = []

def ler_sensor_digital():
    leituras = [random.choice([0, 1]) for _ in range(3)]
    valor = 1 if sum(leituras) >= 2 else 0
    return float(valor)

def ler_sensor_analogico():
    valor = round(random.uniform(20.0, 35.0), 2)
    historico.append(valor)
    if len(historico) > 5:
        historico.pop(0)
    return round(sum(historico) / len(historico), 2)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando ao Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        for _ in range(10):
            if wlan.isconnected():
                break
            print("Aguardando conexao...")
            time.sleep(1)
    if wlan.isconnected():
        print("Wi-Fi conectado! IP:", wlan.ifconfig()[0])
    else:
        print("Falha na conexao Wi-Fi")
    return wlan

def enviar_telemetria(sensor_type, value_type, value, tentativas=3):
    payload = {
        "device_id": DEVICE_ID,
        "timestamp": "2024-01-01T12:00:00Z",
        "sensor_type": sensor_type,
        "value_type": value_type,
        "value": int(value) if value_type == "discrete" else value
    }
    for tentativa in range(1, tentativas + 1):
        try:
            res = urequests.post(
                BACKEND_URL,
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )
            print(f"Enviado [{res.status_code}]: {sensor_type} = {value}")
            res.close()
            return True
        except Exception as e:
            print(f"Tentativa {tentativa} falhou: {e}")
            time.sleep(2)
    print("Falha ao enviar apos todas as tentativas")
    return False

wlan = conectar_wifi()

while True:
    if not wlan.isconnected():
        print("Wi-Fi caiu, reconectando...")
        wlan = conectar_wifi()

    digital = ler_sensor_digital()
    analogico = ler_sensor_analogico()

    print(f"Digital: {digital} | Temperatura (media): {analogico} C")

    enviar_telemetria("presence", "discrete", digital)
    enviar_telemetria("temperature", "analog", analogico)

    time.sleep(2)