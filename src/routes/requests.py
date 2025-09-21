import traceback
from flask import Blueprint, jsonify, request
from src.models.request import Request, db
from datetime import datetime

requests_bp = Blueprint('requests', __name__)

# Rota para obter todas as solicitações (sem alterações)
@requests_bp.route('/requests', methods=['GET'])
def get_all_requests():
    try:
        requests_list = Request.query.order_by(Request.timestamp.desc()).all()
        return jsonify([req.to_dict() for req in requests_list])
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Erro interno ao buscar solicitações.', 'error': str(e)}), 500

# Rota para criar uma nova solicitação (COM ALTERAÇÃO)
@requests_bp.route('/requests', methods=['POST'])
def create_request():
    """Cria uma nova solicitação"""
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
            # =============================================
            # CAMPO DE OBSERVAÇÃO ADICIONADO
            # =============================================
            observacao=data.get('observacao', ''),
            tempo_atendimento=data.get('tempo_atendimento') 
        )
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Solicitação criada com sucesso', 'data': new_request.to_dict()}), 201

    except Exception as e:
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno ao criar solicitação.', 'error': str(e), 'traceback': traceback.format_exc()}), 500

# Rota para atualizar uma solicitação (sem alterações)
@requests_bp.route('/requests/<emp_id>', methods=['PUT'])
def update_request_status(emp_id):
    """Atualiza o status e/ou observação de uma solicitação"""
    try:
        req_to_update = Request.query.get(emp_id)
        if not req_to_update:
            return jsonify({'success': False, 'message': 'Solicitação não encontrada'}), 404

        data = request.get_json()
        
        new_status = data.get('status')
        if new_status and new_status != req_to_update.status:
            req_to_update.status = new_status
            if new_status == 'em-andamento' and not req_to_update.inicio_atendimento:
                req_to_update.inicio_atendimento = datetime.utcnow()
            elif new_status == 'concluido':
                req_to_update.conclusao_atendimento = datetime.utcnow()

        # A observação agora vem do formulário, então a lógica de adicionar observação aqui foi simplificada.
        # Poderíamos ainda permitir que o operador adicione mais observações se quiséssemos.
        if 'observacao' in data:
            # Concatena a nova observação com a existente, se houver.
            nova_obs = data.get('observacao')
            if req_to_update.observacao:
                req_to_update.observacao += f"\n[OPERADOR]: {nova_obs}"
            else:
                req_to_update.observacao = f"[OPERADOR]: {nova_obs}"

        db.session.commit()
        return jsonify({'success': True, 'message': 'Solicitação atualizada com sucesso', 'data': req_to_update.to_dict()})

    except Exception as e:
        print(traceback.format_exc())
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erro interno ao atualizar solicitação.', 'error': str(e), 'traceback': traceback.format_exc()}), 500

# Rota de estatísticas (sem alterações)
@requests_bp.route('/requests/stats', methods=['GET'])
def get_request_stats():
    """Retorna as estatísticas das solicitações"""
    try:
        stats = {
            'pendente': Request.query.filter_by(status='pendente').count(),
            'em_andamento': Request.query.filter_by(status='em-andamento').count(),
            'concluido': Request.query.filter_by(status='concluido').count()
        }
        return jsonify(stats)
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'success': False, 'message': 'Erro interno ao buscar estatísticas.', 'error': str(e)}), 500