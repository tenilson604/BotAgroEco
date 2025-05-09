from flask import Flask, request, render_template_string
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import csv
import os
import requests

app = Flask(__name__)

# API de clima (puedes cambiarla si deseas usar otra gratuita)
WEATHER_API_KEY = "ed86283dbdf64b4c9e045325250905"  # <- pega tu clave aquí

# Diccionario de respuestas rápidas
respuestas = {
    "hola": "¡Hola! Soy BotAgroEco. Pregúntame sobre siembra, fertilización o clima.",
    "¿qué puedo sembrar en abril?": "En abril puedes sembrar maíz, tomate o pimientos.",
    "adiós": "¡Hasta luego! 🌱",
    "gracias": "¡De nada! Aquí estoy si necesitas más ayuda."
}

def obtener_clima(ciudad):
    url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={ciudad}&lang=es"
    try:
        r = requests.get(url)
        data = r.json()
        temp = data["current"]["temp_c"]
        condicion = data["current"]["condition"]["text"]
        return f"En {ciudad} hay {temp}°C y {condicion.lower()}."
    except:
        return "No pude obtener el clima. Intenta con otra ciudad."

@app.route("/bot", methods=["POST"])
def bot():
    mensaje = request.values.get("Body", "").lower()
    numero = request.values.get("From", "")
    fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Guardar en CSV
    archivo_csv = "historial_preguntas.csv"
    nuevo = not os.path.exists(archivo_csv)
    with open(archivo_csv, "a", newline="", encoding="utf-8") as archivo:
        writer = csv.writer(archivo)
        if nuevo:
            writer.writerow(["fecha", "numero", "mensaje"])
        writer.writerow([fecha, numero, mensaje])

    # Buscar respuesta
    respuesta = respuestas.get(mensaje)
    if not respuesta:
        if "clima en" in mensaje:
            ciudad = mensaje.replace("clima en", "").strip()
            respuesta = obtener_clima(ciudad)
        else:
            respuesta = "Lo siento, no entendí tu mensaje. Pregúntame sobre siembra, clima o fertilización."

    # Responder
    resp = MessagingResponse()
    resp.message(respuesta)
    return str(resp)

@app.route("/historial", methods=["GET"])
def ver_historial():
    archivo_csv = "historial_preguntas.csv"
    if not os.path.exists(archivo_csv):
        return "No hay historial aún."

    with open(archivo_csv, encoding="utf-8") as archivo:
        filas = list(csv.reader(archivo))[1:]  # omitimos encabezado

    html = """
    <html>
    <head><title>Historial de BotAgroEco</title></head>
    <body>
    <h2>📊 Historial de preguntas</h2>
    <table border="1">
      <tr><th>Fecha</th><th>Número</th><th>Mensaje</th></tr>
      {% for fila in filas %}
        <tr><td>{{ fila[0] }}</td><td>{{ fila[1] }}</td><td>{{ fila[2] }}</td></tr>
      {% endfor %}
    </table>
    </body>
    </html>
    """
    return render_template_string(html, filas=filas)

if __name__ == "__main__":
    app.run(debug=False)
