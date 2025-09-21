import os
import traceback
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import uuid

# --- Configuração do App e DB ---
app = Flask(__name__)
CORS(app)

db_path = os.path.join('/tmp', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelo do Banco de Dados ---
class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(10), unique=True, nullable=False, default=lambda: f"EMP{str(uuid.uuid4().int)[:4].zfill(4)}")
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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# --- Função para Criar as Tabelas ---
@app.before_request
def create_tables():
    app.app_context().push()
    db.create_all()

# --- Rotas da API ---
@app.route('/api/requests', methods=['GET'])
def get_all_requests():
    try:
        requests_list = Request.query.order_by(Request.timestamp.desc()).all()
        return jsonify([req.to_dict() for req in requests_list])
    except Exception:
        return jsonify({'success': False, 'message': 'Erro interno ao buscar solicitações.'}), 500

@app.route('/api/requests', methods=['POST'])
def create_request():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Nenhum dado enviado'}), 400

        new_request = Request(
            solicitante=data.get('solicitante'),
            area_solicitante=data.get('area_solicitante'),
            tipo_operacao=data.get('tipo_operacao'),
            codigo_item=data.get('codigo_item'),
            localizacao=data.get('localizacao', ''),
            observacao=data.get('observacao', ''),
            tempo_atendimento=data.get('tempo_atendimento')
        )
        db.session.add(new_request)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Solicitação criada com sucesso', 'data': new_request.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno ao criar solicitação.', 'error': str(e), 'traceback': traceback.format_exc()}), 500

@app.route('/api/requests/<emp_id>', methods=['PUT'])
def update_request_status(emp_id):
    try:
        req_to_update = Request.query.filter_by(emp_id=emp_id).first()
        if not req_to_update:
            return jsonify({'success': False, 'message': 'Solicitação não encontrada'}), 404
        data = request.get_json()
        new_status = data.get('status')
        if new_status:
            req_to_update.status = new_status
            if new_status == 'em-andamento' and not req_to_update.inicio_atendimento:
                req_to_update.inicio_atendimento = datetime.utcnow()
            elif new_status == 'concluido':
                req_to_update.conclusao_atendimento = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True, 'data': req_to_update.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno ao atualizar solicitação.', 'error': str(e)}), 500

@app.route('/api/requests/stats', methods=['GET'])
def get_request_stats():
    try:
        stats = {
            'pendente': Request.query.filter_by(status='pendente').count(),
            'em_andamento': Request.query.filter_by(status='em-andamento').count(),
            'concluido': Request.query.filter_by(status='concluido').count()
        }
        return jsonify(stats)
    except Exception:
        return jsonify({'success': False, 'message': 'Erro interno ao buscar estatísticas.'}), 500