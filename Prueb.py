from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import unicodedata
import string

app = Flask(__name__)

# Cargar respuestas desde archivo JSON
with open("respuestas.json", "r", encoding="utf-8") as f:
    RESPUESTAS = json.load(f)

def normalizar(texto):
    texto = texto.lower().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    texto = texto.translate(str.maketrans("", "", string.punctuation))
    return texto

@app.route("/bot", methods=["POST"])
def bot():
    mensaje_entrante = request.values.get("Body", "").strip()
    mensaje_normalizado = normalizar(mensaje_entrante)

    # Intentar coincidencia exacta
    if mensaje_normalizado in RESPUESTAS:
        respuesta = RESPUESTAS[mensaje_normalizado]
    else:
        # Buscar coincidencias parciales
        respuesta = None
        for clave in RESPUESTAS:
            if normalizar(clave) in mensaje_normalizado:
                respuesta = RESPUESTAS[clave]
                break

        if not respuesta:
            respuesta = "Lo siento, no tengo una respuesta para eso."

    respuesta_twilio = MessagingResponse()
    respuesta_twilio.message(respuesta)
    return str(respuesta_twilio)

if __name__ == "__main__":
    app.run(debug=True)
