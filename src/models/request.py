from src.models.user import db
from datetime import datetime
import json

class Request(db.Model):
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), unique=True, nullable=False)  # EMP001, EMP002, etc.
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    solicitante = db.Column(db.String(100), nullable=False)
    area_solicitante = db.Column(db.String(100), nullable=False)
    tipo_operacao = db.Column(db.String(50), nullable=False)  # Entrega ou Guarda
    codigo_item = db.Column(db.String(50), nullable=False)
    localizacao = db.Column(db.String(200))
    status = db.Column(db.String(20), nullable=False, default='pendente')  # pendente, em-andamento, concluido
    observacao = db.Column(db.Text)
    inicio_atendimento = db.Column(db.DateTime)
    conclusao_atendimento = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Converte o objeto para dicionário compatível com o formato atual do painel"""
        return {
            'id': self.emp_id,
            'timestamp': self.timestamp.strftime('%d/%m/%Y %H:%M:%S') if self.timestamp else '',
            'solicitante': self.solicitante,
            'area': self.area_solicitante,
            'operacao': self.tipo_operacao,
            'item': self.codigo_item,
            'localizacao': self.localizacao or '',
            'status': self.status,
            'observacao': self.observacao or '',
            'inicio': self.inicio_atendimento.strftime('%d/%m/%Y, %H:%M:%S') if self.inicio_atendimento else '',
            'conclusao': self.conclusao_atendimento.strftime('%d/%m/%Y, %H:%M:%S') if self.conclusao_atendimento else ''
        }
    
    def to_sheets_format(self):
        """Converte para formato compatível com Google Sheets"""
        return {
            'Carimbo de data/hora': self.timestamp.strftime('%d/%m/%Y %H:%M:%S') if self.timestamp else '',
            'Solicitante': self.solicitante,
            'Área Solicitante': self.area_solicitante,
            'Tipo de Operação': self.tipo_operacao,
            'Código do Item': self.codigo_item,
            'Localização (opcional)': self.localizacao or '',
            'ID': self.emp_id,
            'Status': self.status,
            'Observação': self.observacao or '',
            'Início Atendimento': self.inicio_atendimento.strftime('%d/%m/%Y %H:%M:%S') if self.inicio_atendimento else '',
            'Conclusão Atendimento': self.conclusao_atendimento.strftime('%d/%m/%Y %H:%M:%S') if self.conclusao_atendimento else ''
        }
    
    @staticmethod
    def from_sheets_data(data):
        """Cria uma instância a partir de dados do Google Sheets"""
        return Request(
            emp_id=data.get('ID', ''),
            timestamp=datetime.strptime(data.get('Carimbo de data/hora', ''), '%d/%m/%Y %H:%M:%S') if data.get('Carimbo de data/hora') else datetime.utcnow(),
            solicitante=data.get('Solicitante', ''),
            area_solicitante=data.get('Área Solicitante', ''),
            tipo_operacao=data.get('Tipo de Operação', ''),
            codigo_item=data.get('Código do Item', ''),
            localizacao=data.get('Localização (opcional)', ''),
            status=data.get('Status', 'pendente').lower(),
            observacao=data.get('Observação', ''),
            inicio_atendimento=datetime.strptime(data.get('Início Atendimento', ''), '%d/%m/%Y %H:%M:%S') if data.get('Início Atendimento') else None,
            conclusao_atendimento=datetime.strptime(data.get('Conclusão Atendimento', ''), '%d/%m/%Y %H:%M:%S') if data.get('Conclusão Atendimento') else None
        )
    
    def __repr__(self):
        return f'<Request {self.emp_id}: {self.solicitante} - {self.status}>'
