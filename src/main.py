	import os
from flask import Flask
from flask_cors import CORS
# Correção: Imports relativos que funcionam no Vercel
from models.request import db
from routes.requests import requests_bp

app = Flask(__name__)
CORS(app)

# Lógica do Banco de Dados para Vercel
if os.environ.get('VERCEL'):
    db_path = os.path.join('/tmp', 'app.db')
else:
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database')
    os.makedirs(db_dir, exist_ok=True)
    db_path = os.path.join(db_dir, 'app.db')

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Função para criar tabelas antes de cada requisição
@app.before_request
def create_tables():
    app.app_context().push()
    db.create_all()

# Registra as rotas da API
app.register_blueprint(requests_bp, url_prefix='/api')

# A rota para servir arquivos estáticos não é mais necessária aqui,
# o vercel.json já cuida disso.

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)