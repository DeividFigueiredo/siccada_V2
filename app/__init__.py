from flask import Flask, session, redirect, url_for, flash, request
from .routes.auth import auth_bp
from .routes.vendas import vendas_bp
from .routes.pdf import pdf_bp
from .routes.home import home_bp
from .routes.generic import generic_bp
from .routes.financeiro import finan_bp
from .routes.cadastro import cad_bp
from .routes.doc_gen import docgen_bp

from datetime import timedelta
import os

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.config['DATABASE'] = 'MHV_DB.db'
    app.secret_key = 'chave super-secreta'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=50)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Limite de 10MB para upload

    # Registro dos Blueprints
    app.register_blueprint(auth_bp,url_prefix='/auth')
    app.register_blueprint(vendas_bp,url_prefix='/vendas')
    app.register_blueprint(pdf_bp,url_prefix='/pdfgen')
    app.register_blueprint(home_bp,url_prefix='/home')
    app.register_blueprint(generic_bp, url_prefix='/generic')
    app.register_blueprint(finan_bp,url_prefix= '/finan')
    app.register_blueprint(cad_bp,url_prefix='/cad')
    app.register_blueprint(docgen_bp, url_prefix='/docgen')

    # Verifique se a pasta de upload existe
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    @app.before_request
    def before_request():
        # Define a duração da sessão como permanente
        rotas_publicas = ['auth.login', 'auth.cadastrar', 'static']  # Adicione outras rotas públicas aqui
        if 'user_id' not in session and request.endpoint not in rotas_publicas:
            flash('Sua sessão expirou. Faça login novamente.')
            return redirect(url_for('auth.login'))


    return app
