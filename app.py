from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import json

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


def recibir_mensajes(req):
    try: 
        req = request.get_json()
        entry =req['entry'][0]
        changes = entry['change'][0]
        value = changes['value']
        objeto_mensaje = value['messages']
        
        agregar_mensajes_log(objeto_mensaje)
        
        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED'})
     

# agregar_mensaje_log(json.dumps("Test1"))
if __name__ =='__main__':

    app.run(host='0.0.0.0',port=80,debug=True)
        # app.run(debug=True)