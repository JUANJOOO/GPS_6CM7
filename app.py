import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from math import radians, cos, sin, asin, sqrt
from twilio.rest import Client

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ruta.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class PuntoRuta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)

class PuntoAB(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(1), nullable=False)  # 'A' o 'B'
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agregar_punto_ruta', methods=['POST'])
def agregar_punto_ruta():
    data = request.get_json()
    nuevo_punto = PuntoRuta(latitud=data['latitud'], longitud=data['longitud'])
    db.session.add(nuevo_punto)
    db.session.commit()
    return jsonify({"message": "Punto de ruta agregado"}), 200

@app.route('/establecer_punto_ab', methods=['POST'])
def establecer_punto_ab():
    data = request.get_json()
    print("Datos recibidos:", data)
    data = request.get_json()
    punto_a = data.get('puntoA')
    punto_b = data.get('puntoB')

    if punto_a:
        nuevo_punto_a = PuntoAB(tipo='A', latitud=punto_a['latitud'], longitud=punto_a['longitud'])
        db.session.add(nuevo_punto_a)
    
    if punto_b:
        nuevo_punto_b = PuntoAB(tipo='B', latitud=punto_b['latitud'], longitud=punto_b['longitud'])
        db.session.add(nuevo_punto_b)

    db.session.commit()
    return jsonify({"message": "Puntos A y B establecidos"}), 200

@app.route('/ultima_ubicacion', methods=['GET'])
def ultima_ubicacion():
    ultimo_punto = PuntoRuta.query.order_by(PuntoRuta.id.desc()).first()
    if ultimo_punto:
        return jsonify({'latitud': ultimo_punto.latitud, 'longitud': ultimo_punto.longitud})
    return jsonify({'error': 'No hay datos disponibles'}), 404

@app.route('/verificar_desviacion', methods=['POST'])
def verificar_desviacion():
    punto_a = PuntoAB.query.filter_by(tipo='A').first()
    punto_b = PuntoAB.query.filter_by(tipo='B').first()

    if not punto_a or not punto_b:
        return jsonify({'error': 'Puntos A o B no definidos'}), 400

    data = request.get_json()
    latitud_actual = data.get('latitud')
    longitud_actual = data.get('longitud')

    distancia_a = distancia_haversine(latitud_actual, longitud_actual, punto_a.latitud, punto_a.longitud)
    distancia_b = distancia_haversine(latitud_actual, longitud_actual, punto_b.latitud, punto_b.longitud)

    if distancia_a > 0.1 and distancia_b > 0.1:
        enviar_alerta_whatsapp("Alerta: Se ha detectado una desviación de la ruta.")
        return jsonify({"alerta": "Desviación detectada"}), 200

    return jsonify({"status": "En ruta"}), 200

def enviar_alerta_whatsapp(mensaje):
    account_sid = os.getenv('AC3c5a224ae0a197d859948058b7a72109')
    auth_token = os.getenv('a7cba1b7fb097c980ff95eab320f1e6b')
    cliente = Client(account_sid, auth_token)
    mensaje = cliente.messages.create(
        body=mensaje,
        from_='whatsapp:+14155238886',  # Número de WhatsApp de Twilio Sandbox
        to='whatsapp:+7711893706'
    )
    print(mensaje.sid)

def distancia_haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radio de la Tierra en kilómetros
    return c * r

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
