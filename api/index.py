import os
import traceback
from flask import Flask, jsonify, request, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

app = Flask(__name__)

db_path = os.path.join('/tmp', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    header['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    header['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

@app.route('/api/<path:path>', methods=['OPTIONS'])
def options(path):
    return make_response()

class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(10), unique=True, nullable=False, default=lambda: f"EMP{str(uuid.uuid4().int)[-4:].zfill(4)}")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    solicitante = db.Column(db.String(100), nullable=False)
    area_solicitante = db.Column(db.String(100), nullable=False)
    tipo_operacao = db.Column(db.String(50), nullable=False)
    codigo_item = db.Column(db.String(50), nullable=False)
    localizacao = db.Column(db.String(100), nullable=True, default='')
    observacao = db.Column(db.String(300), nullable=True, default='')
    tempo_atendimento = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(20), default='pendente')
    inicio_atendimento = db.Column(db.DateTime, nullable=True)
    conclusao_atendimento = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        for key, value in d.items():
            if isinstance(value, datetime):
                d[key] = value.isoformat()
        return d

@app.before_request
def create_tables():
    if request.method == 'OPTIONS':
        return
    app.app_context().push()
    db.create_all()

@app.route('/api/requests', methods=['GET'])
def get_all_requests():
    requests_list = Request.query.order_by(Request.timestamp.desc()).all()
    return jsonify([req.to_dict() for req in requests_list])

@app.route('/api/requests', methods=['POST'])
def create_request():
    data = request.get_json()
    new_request = Request(
        solicitante=data.get('solicitante'), area_solicitante=data.get('area_solicitante'),
        tipo_operacao=data.get('tipo_operacao'), codigo_item=data.get('codigo_item'),
        localizacao=data.get('localizacao', ''), observacao=data.get('observacao', ''),
        tempo_atendimento=data.get('tempo_atendimento')
    )
    db.session.add(new_request)
    db.session.commit()
    return jsonify({'success': True, 'data': new_request.to_dict()}), 201

@app.route('/api/requests/<emp_id>', methods=['PUT'])
def update_request_status(emp_id):
    req_to_update = Request.query.filter_by(emp_id=emp_id).first_or_404()
    data = request.get_json()
    if 'status' in data:
        req_to_update.status = data['status']
        if data['status'] == 'em-andamento': req_to_update.inicio_atendimento = datetime.utcnow()
        elif data['status'] == 'concluido': req_to_update.conclusao_atendimento = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True, 'data': req_to_update.to_dict()})

@app.route('/api/requests/stats', methods=['GET'])
def get_request_stats():
    stats = {
        'pendente': Request.query.filter_by(status='pendente').count(),
        'em_andamento': Request.query.filter_by(status='em-andamento').count(),
        'concluido': Request.query.filter_by(status='concluido').count()
    }
    return jsonify(stats)