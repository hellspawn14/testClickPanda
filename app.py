import os
from flask import Flask, request, jsonify, render_template, abort, make_response
import hashlib
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import update, func
from datetime import date, datetime
import codecs
import json
import jwt
import csv

app = Flask(__name__)

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "mis_correos.db"))
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
app.config['SECRET_KEY'] = 'jwt-click-panda-str'
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.String(255), primary_key = True)
    user_email = db.Column(db.String(255))
    user_password = db.Column(db.String(255))
    user_name = db.Column(db.String(255))

    def __init__(self, user_email, user_password, user_name):
        self.user_id = hashlib.md5(user_email.encode()).hexdigest()
        self.user_email = user_email
        self.user_password = hashlib.sha256(user_password.encode()).hexdigest()
        self.user_name = user_name

    def encode_auth_token(self, user_id):
        try:
            payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    #id_campaign = db.Column('id', db.Integer, primary_key = True)
    id_campaign = db.Column(db.String(255), primary_key = True)
    id_user = db.Column(db.String(255))
    subject = db.Column(db.String(255))
    number_of_recipients = db.Column(db.Integer)
    status = db.Column(db.Integer)
    date_last_modified = db.Column(db.DateTime())
    date_created = db.Column(db.DateTime())

    def __init__(self, id_user, subject, number_of_recipients):
        self.id_campaign = datetime.timestamp(datetime.now()) #str(datetime.now())
        self.id_user = id_user
        self.subject = subject 
        self.number_of_recipients = number_of_recipients
        self.status = 1
        self.date_last_modified = datetime.now() #date.today()
        self.date_created = datetime.now() #date.today()

    def delete_campaign(self):
        self.status = 0    
        self.date_last_modified = datetime.now()

@app.route("/registrar_usuario", methods = ['POST'])
def registrar_usuario():
    content = request.get_json()

    user_name = content.get('user_name').strip()
    user_email = content.get('user_email').strip()
    user_password = content.get('user_password').strip()
    
    if user_name is None or user_name == '' or user_email is None or user_email == ''or user_password is None or user_name == '': 
        #abort(400)
        return jsonify({ 'message': 'Hay campos en blanco' }), 400
    else: 
        existing_user = User.query.filter_by(user_email = user_email).first()
        if existing_user is not None: 
            #abort(400) 
            return jsonify({ 'message': 'Usuario ' + user_email + ' ya existe en el sistema' }), 400

        else: 
            new_user = User(user_email, user_password, user_name)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({ 'message': 'Usuario ' + new_user.user_email + ' registrado de forma exitosa' }), 201
    
@app.route("/iniciar_sesion", methods = ['POST'])
def iniciar_sesion():
    content = request.get_json()

    user_email = content.get('user_email')
    # la contraseña siempre debe ser recibida de forma encriptada antes de enviar la solicitud por el post
    user_password = content.get('user_password')

    login_user = User.query.filter_by(user_email = user_email).first()
    if login_user is None or login_user.user_password != user_password: 
        return jsonify({ 'message': 'Usuario/contraseña incorrectos' }), 500
    
    else: 
        auth_token = login_user.encode_auth_token(login_user.user_id)
        response = {
            'status' : 'success', 
            'message' : 'Sesión iniciada', 
            'auth_token' : login_user.decode_auth_token(auth_token)
        }
        return jsonify(response), 201

@app.route("/obtener_historial", methods = ['POST'])
def obtener_historial():
    content = request.get_json()
    user_email = content.get('user_email')

    current_user = User.query.filter_by(user_email = user_email).first()
    if current_user is None: 
        return jsonify({ 'message': 'Usuario no encontrado' }), 500
    else: 
        id_user = current_user.user_id
        user_history = Campaign.query.filter_by(id_user = id_user).order_by(Campaign.date_created.desc()).all()
        result_set = []
        for element in user_history: 
            result_set.append({
                'user' : user_email, 
                'id_campaign': element.id_campaign, 
                'subject': element.subject, 
                'number_of_recipients': element.number_of_recipients, 
                'status': element.status, 
                'date_last_modified': element.date_last_modified.strftime("%Y/%m/%d %H:%M:%S"), 
                'date_created': element.date_created.strftime("%Y/%m/%d %H:%M:%S")
            })
        
        # user_history_parsed = json.loads(result_set)
        # open a file for writing
        csv_file = open('file.csv', 'w')
        # create the csv writer object
        csvwriter = csv.writer(csv_file)
        count = 0
        for r in result_set:
            if count == 0:
                    header = r.keys()
                    csvwriter.writerow(header)
                    count += 1
            csvwriter.writerow(r.values())

        csv_file.close()
        file_data = codecs.open('file.csv', 'rb').read()
        response = make_response()
        response.data = file_data
        return response, 201


@app.route("/obtener_num_correos", methods = ['POST'])
def obtener_num_correos():
    content = request.get_json()
    user_email = content.get('user_email')

    current_user = User.query.filter_by(user_email = user_email).first()
    if current_user is None: 
        return jsonify({ 'message': 'Usuario no encontrado' }), 500
    else: 
        id_user = current_user.user_id
        user_active_campaigns = 0
        user_camps = Campaign.query.filter_by(id_user = id_user, status = 1).all()
        for element in user_camps: 
            user_active_campaigns += element.number_of_recipients
        return jsonify({ 'user_active_campaigns': user_active_campaigns }), 200

@app.route("/exportar_excel", methods = ['POST'])
def exportar_excel():
    return 'Exportar documento a excel'

@app.route("/create_new_campaign", methods = ['POST'])
def create_new_campaign():
    content = request.get_json()
    user_email = content.get('user_email')
    campain_user = User.query.filter_by(user_email = user_email).first()
    subject = content.get('subject')
    number_of_recipients = int(content.get('number_of_recipients'))

    if campain_user is None: 
        return jsonify({ 'message': 'El usuario no existe' }), 500
    elif number_of_recipients < 0:
        return jsonify({ 'message': 'Una campaña debe tener al menos un receptor' }), 500
    else: 
        new_campaign = Campaign(campain_user.user_id, subject, number_of_recipients)
        db.session.add(new_campaign)
        db.session.commit()
        return jsonify({ 'message': 'Campania creada', 'id_campaign': new_campaign.id_campaign }), 201

@app.route("/delete_campaign", methods = ['POST'])
def delete_campaign():
    content = request.get_json()
    id_campaign = content.get('id_campaign')
    current_campaign = Campaign.query.filter_by(id_campaign = id_campaign).first() 
    if current_campaign is None: 
        return jsonify({ 'message': 'La campania no existe' }), 500
    else: 
        Campaign.query.filter_by(id_campaign = id_campaign).update({'status': 0})
        Campaign.query.filter_by(id_campaign = id_campaign).update({'date_last_modified': datetime.now()})
        current_campaign = Campaign.query.filter_by(id_campaign = id_campaign).first()
        db.session.commit()
        
        return jsonify({ 'message': 'Status campania modificado', 'change_status' : current_campaign.status }), 200

@app.route("/")
def landing_message():
    return 'This is sample application'

if __name__ == '__main__': 
    db.drop_all()
    db.create_all()
    app.run(debug = True)


