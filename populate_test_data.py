#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de teste
baseados na estrutura atual da planilha
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from src.main import app
from src.models.request import Request, db

def populate_test_data():
    """Popula o banco com dados de teste similares aos da planilha atual"""
    
    with app.app_context():
        # Limpar dados existentes
        Request.query.delete()
        db.session.commit()
        
        # Dados de teste baseados na estrutura observada
        test_requests = [
            {
                'emp_id': 'EMP2151',
                'timestamp': datetime(2025, 9, 20, 14, 7, 29),
                'solicitante': 'Injeção',
                'area_solicitante': '🏭Injeção de Alumínio',
                'tipo_operacao': '🟠Entrega',
                'codigo_item': '14.100.7010',
                'localizacao': '',
                'status': 'concluido',
                'observacao': '2000 para rebarbar',
                'inicio_atendimento': datetime(2025, 9, 20, 14, 20, 12),
                'conclusao_atendimento': datetime(2025, 9, 20, 15, 14, 6)
            },
            {
                'emp_id': 'EMP2150',
                'timestamp': datetime(2025, 9, 20, 14, 6, 14),
                'solicitante': 'Injeção',
                'area_solicitante': '🏭Injeção de Alumínio',
                'tipo_operacao': '🟠Entrega',
                'codigo_item': '14.100.3028',
                'localizacao': '',
                'status': 'concluido',
                'observacao': '2800 para rebarbar',
                'inicio_atendimento': datetime(2025, 9, 20, 14, 55, 14),
                'conclusao_atendimento': datetime(2025, 9, 20, 15, 14, 12)
            },
            {
                'emp_id': 'EMP2149',
                'timestamp': datetime(2025, 9, 20, 14, 5, 24),
                'solicitante': 'Teste Operador',
                'area_solicitante': '⚙️Usinagem',
                'tipo_operacao': '🔵Guarda',
                'codigo_item': '15.200.4050',
                'localizacao': 'Estante A-15',
                'status': 'pendente',
                'observacao': '',
                'inicio_atendimento': None,
                'conclusao_atendimento': None
            },
            {
                'emp_id': 'EMP2148',
                'timestamp': datetime(2025, 9, 20, 13, 45, 10),
                'solicitante': 'João Silva',
                'area_solicitante': '⭐Qualidade',
                'tipo_operacao': '🟠Entrega',
                'codigo_item': '16.300.2010',
                'localizacao': '',
                'status': 'em-andamento',
                'observacao': 'Peças para inspeção urgente',
                'inicio_atendimento': datetime(2025, 9, 20, 14, 0, 0),
                'conclusao_atendimento': None
            },
            {
                'emp_id': 'EMP2147',
                'timestamp': datetime(2025, 9, 20, 13, 30, 5),
                'solicitante': 'Maria Santos',
                'area_solicitante': '🔧Manutenção INJ',
                'tipo_operacao': '🔵Guarda',
                'codigo_item': '17.400.1020',
                'localizacao': 'Almoxarifado Central',
                'status': 'pendente',
                'observacao': '',
                'inicio_atendimento': None,
                'conclusao_atendimento': None
            }
        ]
        
        # Adicionar dados de teste
        for data in test_requests:
            request_obj = Request(**data)
            db.session.add(request_obj)
        
        db.session.commit()
        
        print(f"✅ Adicionados {len(test_requests)} registros de teste ao banco de dados")
        
        # Mostrar estatísticas
        pendentes = Request.query.filter_by(status='pendente').count()
        em_andamento = Request.query.filter_by(status='em-andamento').count()
        concluidos = Request.query.filter_by(status='concluido').count()
        
        print(f"📊 Estatísticas:")
        print(f"   Pendentes: {pendentes}")
        print(f"   Em Andamento: {em_andamento}")
        print(f"   Concluídos: {concluidos}")
        print(f"   Total: {pendentes + em_andamento + concluidos}")

if __name__ == '__main__':
    populate_test_data()
