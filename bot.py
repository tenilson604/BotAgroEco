from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import unicodedata
import string
import requests

app = Flask(__name__)

# Cargar respuestas desde archivo JSON
with open("respuestas.json", "r", encoding="utf-8") as f:
    RESPUESTAS = json.load(f)

# Cargar cultivos desde archivo JSON
with open("cultivos.json", "r", encoding="utf-8") as f:
    CULTIVOS = json.load(f)

def normalizar(texto):
    texto = texto.lower().strip()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = texto.translate(str.maketrans("", "", string.punctuation))
    return texto

# Función para obtener el clima actual de una ciudad
def obtener_clima(ciudad):
    api_key = "22da5f638d960e211d0d1939430fa498"  # Reemplaza con tu API Key de OpenWeatherMap
    url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={api_key}&units=metric&lang=es"
    try:
        respuesta = requests.get(url)
        datos = respuesta.json()
        if respuesta.status_code == 200:
            temp = datos["main"]["temp"]
            descripcion = datos["weather"][0]["description"]
            return f"El clima en {ciudad.title()} es {descripcion} con {temp}°C."
        else:
            return f"No pude obtener el clima de {ciudad.title()}."
    except Exception as e:
        return "Ocurrió un error al consultar el clima."

@app.route("/bot", methods=["POST"])
def bot():
    mensaje_entrante = request.values.get("Body", "").strip()
    mensaje_normalizado = normalizar(mensaje_entrante)

    respuesta = None

    # Coincidencia exacta en respuestas.json
    if mensaje_normalizado in RESPUESTAS:
        respuesta = RESPUESTAS[mensaje_normalizado]

    # Consultar cultivos.json
    elif mensaje_normalizado.startswith("que sembrar en"):
        mes = mensaje_normalizado.replace("que sembrar en", "").strip()
        mes = normalizar(mes)
        if mes in CULTIVOS:
            lista = ', '.join(CULTIVOS[mes])
            respuesta = f"En {mes} puedes sembrar: {lista}."
        else:
            respuesta = f"No tengo datos de cultivos para {mes}."

    # Consultar clima
    elif mensaje_normalizado.startswith("clima en"):
        ciudad = mensaje_normalizado.replace("clima en", "").strip()
        respuesta = obtener_clima(ciudad)

    # Respuesta por defecto
    if not respuesta:
        respuesta = "Lo siento, no tengo una respuesta para eso."

    respuesta_twilio = MessagingResponse()
    respuesta_twilio.message(respuesta)
    return str(respuesta_twilio)

if __name__ == "__main__":
    app.run(debug=True)
