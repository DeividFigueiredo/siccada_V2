from flask import Flask, Blueprint, request, render_template, redirect, send_file, url_for,session, current_app, flash, send_from_directory
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from PyPDF2 import PdfMerger
#from pdf2image import convert_from_path
from app.utils import acesso, hierarquia
from ..models.database import query_db
import sqlite3
import re
import glob

cad_bp = Blueprint('cad', __name__)



@cad_bp.route('/')
def home():
    return render_template('cadastro/home.html')

@cad_bp.route('/doc')
@acesso('cadastro')
def doc_home():
    return render_template('cadastro/doc_home.html')

@cad_bp.route('cnt-acompanhamento')
@acesso('vendas', 'cadastro', 'administrativo','financeiro')
@hierarquia('supervisor','agente','vendedor')

def acompanhar_cnt():
    
    
    conn= sqlite3.connect(current_app.config['DATABASE'])
    cur= conn.cursor()
    resp = request.args.get('resp')
    tipo_usuario = session.get('tipo_usuario')
    lista= request.args.get('lista')
    filtro = request.args.get('filtro')
    print(filtro)
    venda_inicial = request.args.get('venda_inicial')
    venda_final = request.args.get('venda_final')
    print(f"venda_inicial: {venda_inicial}, venda_final: {venda_final}")
    


    print(resp)
    if resp:
        cur.execute("SELECT * FROM venda WHERE corretor_resp = ?", (resp,))
        result = cur.fetchall()
        print(f"result: {result}")
        return render_template('cadastro/acompanhar_cnt.html', result=result, resp=resp)
        
    
    elif lista == 'todos':
            print(f'exibiindo para: {lista}')
            if filtro =='sim':
                return render_template('cadastro/definir.html')
            
    elif venda_final and venda_inicial:      
        venda_convert_init= datetime.strptime(venda_inicial, '%Y-%m-%d').date()
        venda_convert_final= datetime.strptime(venda_final, '%Y-%m-%d').date()
        venda_inicial = venda_convert_init.strftime('%d/%m/%Y')
        venda_final = venda_convert_final.strftime('%d/%m/%Y')
        print(f"Venda inicial: {venda_inicial}, Venda final: {venda_final}")
        cur.execute("SELECT * FROM venda WHERE data_venda BETWEEN ? AND ?", (venda_inicial, venda_final))
        result = cur.fetchall()
        print(f"result: {result}")
        return render_template('cadastro/contratos_finalizados.html', result=result, resp=resp)
           
               

    elif resp is None:
        if tipo_usuario == 'vendas':
            print(f"Tipo de usuário: {tipo_usuario}")
            query = "SELECT * FROM venda WHERE status <>'contrato finalizado'"
            result = query_db(query)
            return render_template('cadastro/acompanhar_cnt.html', result=result, resp=resp)
        elif tipo_usuario == 'cadastro':
            print(f"Tipo de usuário: {tipo_usuario}")
            query = "SELECT * FROM venda WHERE status = 'Enviado ao cadastro' OR status = 'enviado para Declaração de Saúde' OR status = 'entrevista online enviada'" 
            result = query_db(query)
            if result is None:
               return render_template('cadastro/sem_registro.html ', result=result, resp=resp)
            return render_template('cadastro/acompanhar_cnt.html', result=result, resp=resp)
        elif tipo_usuario == 'financeiro':
            print(f"Tipo de usuário: {tipo_usuario}")
            query = "SELECT * FROM venda WHERE status ='enviado para financeiro' OR status = 'boleto emitido'"
            result = query_db(query)
            return render_template('cadastro/acompanhar_cnt.html', result=result, resp=resp)
        elif tipo_usuario == 'administrativo':
            print(f"Tipo de usuário: {tipo_usuario}")
            query = "SELECT * FROM venda WHERE status ='enviado para entrevista' OR status = 'analise de declaração'OR status= 'entrevista agendada'"
            result = query_db(query)

            return render_template('cadastro/acompanhar_cnt.html', result=result, resp=resp)
        
@cad_bp.route('/detalhes_cnt', methods=['POST', 'GET'])
@acesso('vendas', 'cadastro', 'administrativo','financeiro')
@hierarquia('supervisor', 'agente', 'vendedor')
def detalhes_cnt():
    id = request.args.get('proposta')
    print(f"ID recebido: {id}")

    if id is None:
        return "ID não fornecido", 400

    try:
        id = int(id)
    except ValueError:
        return "ID inválido", 400

    conn = sqlite3.connect(current_app.config['DATABASE'])
    cur = conn.cursor()

    # Buscar os detalhes da venda
    cur.execute("SELECT * FROM venda WHERE numero_proposta = ?", (id,))
    venda = cur.fetchone()

    if venda is None:
        cur.close()
        conn.close()
        return "Registro não encontrado", 404

    # Buscar os responsáveis relacionados à venda
    cur.execute("SELECT * FROM responsavel WHERE proposta_id = ?", (id,))
    responsaveis = cur.fetchall()

    # Buscar os titulares relacionados à venda
    cur.execute("SELECT * FROM titulares WHERE proposta_id = ?", (id,))
    titulares = cur.fetchall()

    # Buscar os dependentes relacionados à venda
    cur.execute("SELECT * FROM dependentes WHERE proposta_id = ?", (id,))
    dependentes = cur.fetchall()

    cur.close()
    conn.close()

    # Renderizar o template com os dados
    return render_template(
        'cadastro/detalhes_cnt.html',
        venda=venda,
        responsaveis=responsaveis,
        titulares=titulares,
        dependentes=dependentes
    )

@cad_bp.route('/alterar_proposta', methods=['POST', 'GET'])
@acesso('vendas', 'cadastro', 'administrativo', 'financeiro')
@hierarquia('supervisor','agente','vendedor')
def alterar_proposta():
    proposta= request.args.get('proposta')
    
    
    return render_template('cadastro/alterar_proposta.html', proposta=proposta)
    
@cad_bp.route('/alterar_registro', methods=['POST', 'GET'])

@acesso('vendas', 'cadastro', 'administrativo', 'financeiro')
@hierarquia('supervisor','agente')
def atualizar_cnt():
    contrato = request.args.get('contrato')  # Para GET
    proposta = request.args.get('proposta')
    id = request.args.get('id')
    tipo_usuario = session.get('tipo_usuario')
    last_resp= request.args.get('last_resp')
    status = request.args.get('status')

    if status == 'contrato finalizado':
        flash('Contrato já finalizado. Não é possível alterar.', 'error')
        return redirect(url_for('cad.detalhes_cnt', id=id, proposta=proposta, contrato=contrato,tipo_usuario=tipo_usuario))

    print(id, proposta,tipo_usuario)
    
    if  not contrato:
        return redirect(url_for('cad.adicionar_cnt', id=id,proposta=proposta,contrato=contrato,tipo_usuario=tipo_usuario,area=last_resp))

    print(f"Contrato: {contrato}, Proposta: {proposta}, ID: {id}")
  
    print(tipo_usuario)
    
    return render_template('cadastro/alterar_cnt.html',id=id,contrato=contrato, proposta=proposta, area=tipo_usuario,last_resp=last_resp)
    


@cad_bp.route('/adicionar_cnt', methods=['GET','POST'])
@acesso('cadastro')
@hierarquia('supervisor','agente')
def adicionar_cnt():
    id =request.args.get('id')
    id = int(id)
    proposta = request.args.get('proposta')
    print(id, proposta)


    
    if request.method == 'POST':
        contrato=request.form.get('contrato')

        conn = sqlite3.connect(current_app.config['DATABASE'])
        cur = conn.cursor()
        cur.execute("UPDATE venda SET status = ? WHERE id = ?", (contrato, id))
        cur.execute("UPDATE venda SET status = 'enviado para Declaração de Saúde WHERE id = ?" ,(id))
        conn.commit()
        cur.close()
        conn.close()
        return url_for('cad.alterar_registro')

    return render_template('cadastro/adicionar_cnt.html',id=id, proposta=proposta)


@cad_bp.route('render_doc_get', methods=['POST', 'GET'])
@acesso('vendas', 'cadastro')
@hierarquia('supervisor','agente','vendedor')

def render_page_doc():
    proposta = request.args.get('proposta')
    print(f"Proposta recebida: {proposta}")
    return render_template('cadastro/adicionar_documento.html', proposta=proposta)

@cad_bp.route('adicionar_doc', methods=['POST', 'GET'])
@acesso('vendas', 'cadastro')
@hierarquia('supervisor','agente','vendedor')
def adicionar_doc():
    classe_usuario = session.get('classe_usuario')
    print(f"Tipo de usuário: {classe_usuario}")
    if classe_usuario == 'vendedor':
        resp = session.get('user_nome')
    import os
    from werkzeug.utils import secure_filename
    from flask import request, redirect, url_for, flash, render_template
    ALLOWED_EXTENSIONS = {'rar', 'zip'}
    proposta = request.args.get('proposta')
    print(f"Proposta recebida: {proposta}")

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if request.method == 'POST':
        if 'arquivos' not in request.files:
            flash('Nenhum arquivo selecionado.')
            return redirect(request.url)
        arquivos = request.files.getlist('arquivos')
        # Salva na pasta static/Documentos_contrato de forma dinâmica
        base_folder = os.path.join(os.getcwd(), 'static', 'Documento_propostas' )
        base_folder = os.path.abspath(base_folder)
        if not proposta:
            flash('Proposta não informada.')
            return redirect(request.url)
        proposta_folder = os.path.join(base_folder, str(proposta))
        os.makedirs(proposta_folder, exist_ok=True)
        for arquivo in arquivos:
            if arquivo and allowed_file(arquivo.filename):
                ext = arquivo.filename.rsplit('.', 1)[1].lower()
                filename = f"proposta {proposta}.{ext}"
                arquivo.save(os.path.join(proposta_folder, filename))
            else:
                flash('Tipo de arquivo não permitido.')
                return redirect(request.url)
        flash('Arquivos enviados com sucesso!')
        return redirect(url_for('auth.redir_atent'))
    return redirect(url_for('auth.redir_atent'))

@cad_bp.route('gravar_alteracao', methods=['POST'])
@acesso('vendas', 'cadastro', 'administrativo', 'financeiro')
@hierarquia('supervisor','agente','vendedor')

def gravar_alteracao():

    id= request.args.get('id')
    print(f"ID recebido: {id}")
    info = request.form.get('info') #nome da coluna a ser atualizada
    tipo_usuario = session.get('tipo_usuario')
    print(f"Tipo de usuário: {tipo_usuario}")
    
    status= request.form.get('status') #valor a ser atualizado
    

    if id is None:
        return "ID não fornecido", 400

    try:
        id = int(id)
    except ValueError:
        return "ID inválido", 400

    if request.method == 'POST':
        situacao = request.form.get('situacao')
        id=int(id)
        print(f"Situação recebida: {situacao}")

        conn = sqlite3.connect(current_app.config['DATABASE'])
        cur = conn.cursor()
        cur.execute(f"UPDATE venda SET {info} = ? WHERE id = ?", (status, id))
        cur.execute("UPDATE venda SET last_resp = ? WHERE id = ?", (tipo_usuario, id))

        conn.commit()
        cur.close()
        conn.close()
        flash('Alteração realizada com sucesso!', 'success')

        return redirect(url_for('cad.acompanhar_cnt'))

@cad_bp.route('/alterar_infos_prpopsta', methods=['POST', 'GET'])
@acesso('vendas', 'cadastro', 'administrativo')
@hierarquia('supervisor','agente','vendedor')
def alterar_infos_proposta():
    proposta = request.args.get('proposta')
    print(f"Proposta recebida: {proposta}")
    tp_alt = request.args.get('tp_alt')
    print(tp_alt)
    if not proposta:
        flash('Proposta não informada.','error')
        return redirect(url_for('cad.detalhes_cnt', proposta=proposta))
    
    if tp_alt =='venda':
        try:
            dados = query_db ("SELECT * FROM venda WHERE numero_proposta = ?", (proposta,), one=True)
            if not dados:
                flash('Proposta não encontrada.','error')
                return redirect(url_for('cad.detalhes_cnt',proposta=proposta))
        except sqlite3.Error as e:
            flash(f'Erro ao consultar a proposta: {e}', 'error')
            return redirect(url_for('cad.detalhes_cnt',proposta=proposta))
        

        
    

@cad_bp.route('/documentos_contrato/<proposta>')
def documento_contrato(proposta):
    import os
    from flask import send_from_directory, abort
    base_folder = os.path.join(os.getcwd(), 'static', 'Documento_propostas' )
    base_folder = os.path.abspath(base_folder)
    proposta_folder = os.path.join(base_folder, str(proposta))
    if not os.path.exists(proposta_folder):
        return abort(404, description='Pasta da proposta não encontrada.')
    arquivos = os.listdir(proposta_folder)
    if not arquivos:
        return abort(404, description='Nenhum arquivo encontrado para esta proposta.')
    # Sempre pega o primeiro arquivo da pasta
    filename = arquivos[0]
    print(f"Proposta recebida: {proposta}, Nome do arquivo: {filename}")
    return send_from_directory(proposta_folder, filename, as_attachment=True)
