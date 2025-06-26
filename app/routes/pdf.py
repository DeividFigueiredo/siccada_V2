from flask import Flask, Blueprint, request, render_template, redirect, send_file, url_for
import os
from app.routes.doc_gen import limpar_pasta_saida
from app.utils import acesso
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
#from pdf2image import convert_from_path
import sqlite3
import re
import glob

app = Flask(__name__)

# Caminho base do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
FRONT_FOLDER = os.path.join(BASE_DIR, 'static', 'frontal-card')
DATABASE = os.path.join(BASE_DIR, 'MHV_DB.db')


# Configurações do aplicativo
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Limite de 10MB para upload

# Certifica-se de que os diretórios necessários existem
for folder in [UPLOAD_FOLDER, FRONT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def allowed_file(filename):
    """Verifica se o arquivo é permitido."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def combine_pdfs(front_pdf, back_pdf, output_pdf):
    """Combina as páginas dos PDFs (frontal e traseira) em um único PDF."""
    try:
        merger = PdfMerger()
        merger.append(front_pdf)  # Adiciona a página da frente
        merger.append(back_pdf)   # Adiciona a página de trás
        merger.write(output_pdf)
        merger.close()
    except Exception as e:
        raise RuntimeError(f"Erro ao combinar PDFs: {e}")

pdf_bp = Blueprint('pdfgen', __name__)

@pdf_bp.route('/criar_card', methods=['GET', 'POST'])
@acesso('cadastro', 'cobranca','administrativo')

def create_card():
        return render_template("cadastro/create_card.html")

@pdf_bp.route('/upload', methods=['POST'])
def upload_files():
    """Rota para fazer upload do arquivo PDF traseiro e combinar com a arte frontal."""
    if 'back_pdf' not in request.files:
        return 'Arquivo traseiro não foi enviado.', 400

    back_file = request.files['back_pdf']

    # Verifica se o diretório frontal existe
    front_files = glob.glob(os.path.join(FRONT_FOLDER, '*.pdf'))
    if not front_files:
        return 'Nenhuma arte frontal encontrada no diretório especificado.', 404

    # Seleciona o primeiro arquivo encontrado
    front_path = front_files[0]

    if back_file and allowed_file(back_file.filename):
        try:
            # Salvar o arquivo traseiro
            back_filename = secure_filename(back_file.filename)
            back_path = os.path.join(app.config['UPLOAD_FOLDER'], back_filename)
            back_file.save(back_path)

            # Gerar o PDF combinado
            output_pdf = os.path.join(app.config['UPLOAD_FOLDER'], 'digital_id-MHVIDA.pdf')
            combine_pdfs(front_path, back_path, output_pdf)

            # Redirecionar para renderizar o PDF
            return redirect(url_for('pdfgen.download_pdf', pdf_path=output_pdf))
        except Exception as e:
            return f"Erro ao processar os arquivos: {e}", 500

    return 'Arquivo inválido. Certifique-se de enviar um arquivo PDF traseiro.', 400

@pdf_bp.route('/download_pdf')
def download_pdf():
    """Permite o download do PDF gerado."""
    pdf_path = os.path.abspath(request.args.get('pdf_path'))
    if not os.path.exists(pdf_path):
        return 'O arquivo PDF especificado não foi encontrado.', 404

    return send_file(pdf_path, as_attachment=True)




if __name__ == '__main__':
    app.register_blueprint(pdf_bp)
    app.run(debug=True)
