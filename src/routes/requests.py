from flask import Blueprint, request, jsonify
from datetime import datetime
from src.models.request import Request, db
import json

requests_bp = Blueprint('requests', __name__)

@requests_bp.route('/requests', methods=['GET'])
def get_requests():
    """Retorna todas as solicitações - compatível com o formato atual do painel"""
    try:
        # Filtros opcionais
        status_filter = request.args.get('status')
        area_filter = request.args.get('area')
        date_filter = request.args.get('date')
        
        query = Request.query
        
        if status_filter and status_filter != 'todos':
            query = query.filter(Request.status == status_filter)
            
        if area_filter and area_filter != 'todos':
            query = query.filter(Request.area_solicitante == area_filter)
            
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                query = query.filter(db.func.date(Request.timestamp) == filter_date)
            except ValueError:
                pass
        
        # Ordenar por timestamp decrescente (mais recentes primeiro)
        requests = query.order_by(Request.timestamp.desc()).all()
        
        # Converter para formato compatível com o painel atual
        result = [req.to_dict() for req in requests]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@requests_bp.route('/requests/<emp_id>', methods=['PUT'])
def update_request(emp_id):
    """Atualiza uma solicitação específica"""
    try:
        req = Request.query.filter_by(emp_id=emp_id).first()
        if not req:
            return jsonify({'error': 'Solicitação não encontrada'}), 404
        
        data = request.get_json()
        
        # Atualizar status
        if 'status' in data:
            old_status = req.status
            new_status = data['status'].lower()
            req.status = new_status
            
            # Atualizar timestamps baseado na mudança de status
            if old_status == 'pendente' and new_status == 'em-andamento':
                req.inicio_atendimento = datetime.utcnow()
            elif new_status == 'concluido' and not req.conclusao_atendimento:
                req.conclusao_atendimento = datetime.utcnow()
                if not req.inicio_atendimento:
                    req.inicio_atendimento = datetime.utcnow()
        
        # Atualizar observação
        if 'observacao' in data:
            req.observacao = data['observacao']
        
        req.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Solicitação atualizada com sucesso',
            'data': req.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@requests_bp.route('/requests', methods=['POST'])
def create_request():
    """Cria uma nova solicitação (vinda do formulário)"""
    try:
        data = request.get_json()
        
        # Gerar próximo ID EMP
        last_request = Request.query.order_by(Request.id.desc()).first()
        if last_request and last_request.emp_id.startswith('EMP'):
            try:
                last_num = int(last_request.emp_id[3:])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        new_emp_id = f'EMP{new_num:04d}'
        
        # Criar nova solicitação
        new_request = Request(
            emp_id=new_emp_id,
            timestamp=datetime.utcnow(),
            solicitante=data.get('solicitante', ''),
            area_solicitante=data.get('area_solicitante', ''),
            tipo_operacao=data.get('tipo_operacao', ''),
            codigo_item=data.get('codigo_item', ''),
            localizacao=data.get('localizacao', ''),
            status='pendente'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Solicitação criada com sucesso',
            'data': new_request.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@requests_bp.route('/requests/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas para os contadores do painel"""
    try:
        pendentes = Request.query.filter_by(status='pendente').count()
        em_andamento = Request.query.filter_by(status='em-andamento').count()
        concluidos = Request.query.filter_by(status='concluido').count()
        
        return jsonify({
            'pendentes': pendentes,
            'em_andamento': em_andamento,
            'concluidos': concluidos,
            'total': pendentes + em_andamento + concluidos
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@requests_bp.route('/requests/areas', methods=['GET'])
def get_areas():
    """Retorna lista de áreas únicas para o filtro"""
    try:
        areas = db.session.query(Request.area_solicitante).distinct().all()
        area_list = [area[0] for area in areas if area[0]]
        return jsonify(area_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@requests_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })
