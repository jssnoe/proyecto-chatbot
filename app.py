from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import json
import http.client

app = Flask(__name__)

# config de la BD SQLITE   
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db =SQLAlchemy(app)

# modelo de la tabla
class Log(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    fecha_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

#crear tabla si no existe
with app.app_context():
    db.create_all()

    # prueba1 = Log(texto='Mensaje de prueba 1')
    # prueba2 = Log(texto='Mensaje de prueba 2')

    # db.session.add(prueba1)
    # db.session.add(prueba2)
    # db.session.commit()

    #ordena los registros por fecha y hora
def ordenar(registros):
    return sorted(registros, key=lambda x: x.fecha_hora, reverse=True)

@app.route('/')
def index():
    #obtener todos los registros de la base de datos 
    registros = Log.query.all()
    registros_ordenados = ordenar(registros)
    return render_template('index.html', registros=registros_ordenados)

mensaje_log=[]

#funcion para agregar y guardar mensajes en la BD
def agregar_mensajes_log(texto):
    mensaje_log.append(texto)

    #guardar mensaje en la BD
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#TOKEN DE VERIFICACIÓN
TOKEN = "ANDERCODE"

@app.route('/webhook', methods=['GET','POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if challenge and token == TOKEN:
        return challenge
    else:
        return jsonify({'error': 'Token invalido'}), 401

#recibe mensajes
def recibir_mensajes(req):
    try: 
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']
        
        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages['type']
                if tipo == "interactive":
                    return 0
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]

                    agregar_mensajes_log(json.dumps(text))
                    agregar_mensajes_log(json.dumps(numero))
                    enviar_mensajes(text, numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})
     
def enviar_mensajes(texto, number):
    texto = texto.lower()
    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "¡Hola! 👋 soy CHIS tu asesor virtual.📍 ¿Necesitas información? Encuéntrala en https://mentetec.com/  ✅ Estas son algunas cosas que puedo responder. 📤La información deberá ser ingresada manualmente: \n1️⃣ - Información de Pagos \n2️⃣ - Soporte \n3️⃣ - Dirección"
            }
        }
    elif "1" in texto:
          data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Prueba 1"
            }
        }
    elif "2" in texto:
          data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Prueba 2"
            }
        }
    elif "3" in texto:
          data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            "type": "location",
            "location": {
                "latitude": "-4.018031",
                "longitude": "-79.211453",
                "name": "Daniel Alvarez",
                "address": "Francisco de Miranda",
            }
        }
    else:
          data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": number,
            
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "¡Hola! 👋"
            }
        }
          #convertir a json
    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAG677DZAxLABO2RZAd0b7cGuEBvwv34jUOZB2ZATUz9Gg51wq2xxYgMatdB1HRykuUIbMi4CemP8WriUROFoNwy3H0ZCunZB2jYCrDsAUv6x64E4VOQqZBOMmp6Pj884PPtZCUYFWxh7SQ4ZCU0mRPIOeAXEGObOgbSRBuYk2WTqPr4W5mEaS82sJ06FKbRTzEsnZAgNntGmD7DY3jaGU"
    }
    
    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v19.0/352332097955313/messages", data, headers)
        response = connection.getresponse()
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))

    finally:
        connection.close()

# agregar_mensaje_log(json.dumps("Test1"))
if __name__ =='__main__':

    app.run(host='0.0.0.0',port=8080,debug=True)
        # app.run(debug=True)