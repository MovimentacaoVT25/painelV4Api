import os
import sys
# DON'T CHANGE THIS !!!
# Adiciona o diretório raiz do projeto ao path para importações corretas
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.request import db
from src.routes.requests import requests_bp

# Configuração do App Flask
app = Flask(__name__, static_folder='static')
CORS(app) # Habilita CORS para a API

# ==========================================================
# INÍCIO DA CORREÇÃO: Lógica do Banco de Dados para Vercel
# ==========================================================

# Verifica se está no ambiente Vercel para definir o caminho do DB
if os.environ.get('VERCEL'):
    # No Vercel, o único local gravável é o diretório /tmp
    db_path = os.path.join('/tmp', 'app.db')
else:
    # No ambiente local, cria o DB na pasta 'database'
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
# ==========================================================
# FIM DA CORREÇÃO
# ==========================================================

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Registra os blueprints (rotas da API)
app.register_blueprint(requests_bp, url_prefix='/api')

# Cria as tabelas do banco de dados dentro do contexto da aplicação
with app.app_context():
    db.create_all()

# Rota para servir os arquivos estáticos (index.html, painel.html, etc.)
# Esta rota não é mais necessária se o vercel.json estiver configurado corretamente,
# mas é mantida para funcionamento local.
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        # Tenta servir 'painel.html' como padrão se 'index.html' não existir
        index_path = os.path.join(app.static_folder, 'painel.html')
        if os.path.exists(index_path):
            return send_from_directory(app.static_folder, 'painel.html')
        else:
            return "Página não encontrada.", 404

# Executa o servidor para desenvolvimento local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)