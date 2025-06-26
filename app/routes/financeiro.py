from flask import Blueprint, render_template, request, session,redirect,url_for, jsonify, current_app, flash
from ..models.database import query_db
from datetime import datetime
import re
import sqlite3
import csv
import io
from flask import Response, request

from app.utils import login_required, acesso


##defs para validação de calculo do acordo
def calcular_total(valores_mensalidades, desconto):
    valor_total = sum(valores_mensalidades)
    valor_com_desconto = valor_total * ((100 - desconto) / 100)
    return round(valor_total, 2), round(valor_com_desconto, 2)

def calcular_parcelas(valor_com_desconto, parcelas):
    if parcelas > 8:
        return {"error": "Quantidade de parcelas inválida (máximo: 8)"}
    valor_parcela = valor_com_desconto / parcelas
    return {"valor_parcela": round(valor_parcela, 2)}


finan_bp = Blueprint('finan', __name__)

@finan_bp.route('/')

def home():

    return render_template('financeiro/home_f.html')


##rota para inserir dados de pagamento no banco
@finan_bp.route('/pix', methods=['GET','POST'])
@acesso('financeiro', 'cobranca', 'cadastro')
def pix():
    id_usuario=session.get('user_id')
    nome_usuario= session.get('user_nome')
    
    print(id_usuario, nome_usuario)
    if request.method=='POST':
        ncontrato= request.form['ncontrato']
        nresponsavel= request.form['nresponsavel']
        valor=request.form['valor']
        data_pagamento= request.form['data_pagamento']
        metodo_pg=request.form['metodo_pg']
        descricao=request.form['descricao']
        status=request.form['status']
        data_cadastro= datetime.now().strftime('%Y-%m-%d')
        data_vencimento= request.form['data_vencimento']
        tipo_lancamento= request.form['tipo_lancamento']

        print(f"id {id_usuario}, contrato {ncontrato}, nome{nresponsavel}, valor {valor}, data {data_pagamento},metodo {metodo_pg}, {descricao}, sataus{status},{nome_usuario}")

    

        

        conn=sqlite3.connect(current_app.config['DATABASE'])
        cur=conn.cursor()
        print(f"id {id_usuario}, contrato {ncontrato}, nome{nresponsavel}, valor {valor}, data {data_pagamento},metodo {metodo_pg}, {descricao}, sataus{status},{nome_usuario}")
        cur.execute(
            "INSERT INTO pagamentos (id_usuario, ncontrato, nresponsavel, valor, data_pagamento, metodo_pagamento, descricao, status,nusuario, data_vencimento, tipo_lancamento,data_cadastro) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )",
            (id_usuario, ncontrato, nresponsavel, valor, data_pagamento,metodo_pg, descricao, status,nome_usuario,data_vencimento, tipo_lancamento,data_cadastro)
            )
        print(f"id {id_usuario}, contrato {ncontrato}, nome{nresponsavel}, valor {valor}, data {data_pagamento},metodo {metodo_pg}, {descricao}, sataus{status},{nome_usuario},{data_cadastro}, {tipo_lancamento}")

        conn.commit()
        conn.close()

        flash('dados cadastrados.')
        return redirect(url_for('finan.return_'))

    return render_template('financeiro/pix.html')


@finan_bp.route('/tab_pix', methods=['GET', 'POST'])
@acesso('financeiro', 'cadastro', 'cobranca')
def tab():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    tipo_usuario = session.get('tipo_usuario')
    data_inicial = request.args.get('data_inicial', '').strip()
    data_fim = request.args.get('data_fim', '').strip()
    metodo_pagamento = request.args.get('metodo_pagamento', '').strip()
    status = request.args.get('status', '').strip()
    tipo_lancamento = request.args.get('tipo_lancamento', '').strip()
    
    print(f"Parâmetros recebidos na URL: {request.args}")  # Depuração
    
    cur = conn.cursor()
    pagamentos = []  # <- garante que a variável exista


    if tipo_usuario == '':
        return redirect(url_for('finan.definir'))

    else:
        try:
            query = "SELECT * FROM pagamentos WHERE 1=1"
            params = []

            if data_inicial and data_fim:
                query += " AND data_pagamento BETWEEN ? AND ?"
                params.extend([data_inicial, data_fim])
            if metodo_pagamento:
                query += " AND metodo_pagamento = ?"
                params.append(metodo_pagamento)

            if status:
                query += " AND status = ?"
                params.append(status)

            if tipo_lancamento:
                query+= " AND tipo_lancamento = ?"
                params.append(tipo_lancamento)

            cur.execute(query, params)
            pagamentos = cur.fetchall()
            print(f"pagamentos:{query, params}")
            cur.close()
            
  # Formatar datas para dd/MM/yyyy
            pagamentos_formatados = []
            for p in pagamentos:
                p = list(p)
                # Supondo que data_pagamento está na posição 5 e data_vencimento na 10 (ajuste se necessário)
                try:
                    if p[5]:
                        p[5] = datetime.strptime(p[5], "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    pass
                try:
                    if p[10]:
                        p[10] = datetime.strptime(p[10], "%Y-%m-%d").strftime("%d/%m/%Y")
                except Exception:
                    pass
                pagamentos_formatados.append(p)

            return render_template('financeiro/tab_pix.html', pagamentos=pagamentos_formatados)

        except Exception as e:
            print(f"Erro ao buscar pagamentos: {e}")
        finally:
            cur.close()
            conn.close()



    

@finan_bp.route('/definir_tabela', methods=['GET','POST'])
def definir():
    conn=sqlite3.connect(current_app.config['DATABASE'])    
    cur=conn.cursor()


    if request.method == 'POST':
        data_inicial= request.form.get('data_inicio')           
        
        data_fim= request.form.get('data_fim')
        metodo_pagamento = request.form.get('metodo_pagamento')
        status= request.form.get('status')
        tipo_lancamento= request.form.get('tipo_lancamento')
    
        return redirect(url_for('finan.tab', data_inicial=data_inicial, data_fim=data_fim, metodo_pagamento=metodo_pagamento, status=status, tipo_lancamento=tipo_lancamento))

    return render_template('financeiro/definir.html')
@finan_bp.route('/calculo_acordo', methods=['GET','POST'])
def calculo_acordo():
    if request.method == 'POST':
        try:
            # Captura os dados do formulário
            em_aberto = int(request.form.get('em_aberto'))
            valores_mensalidades = [float(x) for x in request.form.getlist('valores_mensalidades')]
            desconto = float(request.form.get('desconto', 0))
            parcelas = int(request.form.get('parcelas', 1))

            # Verifica se os dados estão corretos
            if em_aberto != len(valores_mensalidades):
                return render_template('financeiro/calcula.html', error="Quantidade de mensalidades não corresponde aos valores fornecidos.", 
                                       em_aberto=em_aberto, valores_mensalidades=valores_mensalidades, desconto=desconto, parcelas=parcelas)
            
            # Calcula total e parcelas
            valor_total, valor_com_desconto = calcular_total(valores_mensalidades, desconto)
            resultado_parcelas = calcular_parcelas(valor_com_desconto, parcelas)

            if "error" in resultado_parcelas:
                return render_template('financeiro/calcula.html', error=resultado_parcelas["error"], 
                                       em_aberto=em_aberto, valores_mensalidades=valores_mensalidades, desconto=desconto, parcelas=parcelas)

            # Renderiza os resultados
            return render_template(
                'financeiro/calcula.html',
                valor_total=valor_total,
                valor_com_desconto=valor_com_desconto,
                parcelas=parcelas,
                valor_parcela=resultado_parcelas["valor_parcela"],
                em_aberto=em_aberto,
                valores_mensalidades=valores_mensalidades,
                desconto=desconto
            )
        except Exception as e:
            return render_template('financeiro/calcula.html', error="Erro no processamento: " + str(e))
    
    # GET: Renderiza o formulário vazio
    return render_template('financeiro/calcula.html')

@finan_bp.route('/alt_page/<int:pagamento_id>', methods= ['GET', 'POST'])
@acesso('financeiro')
def alt_page(pagamento_id):
    pagamento_status = request.args.get('status', '').strip()
    print(f"Status recebido na rota alt_page: {pagamento_status}")  # Depuração

    print(pagamento_id)
    conn = sqlite3.connect(current_app.config['DATABASE'])
    try:
        if request.method == 'POST':
            novo_status = request.form['status']
            cur = conn.cursor()
            cur.execute("UPDATE pagamentos SET status = ? WHERE id = ?", (novo_status, pagamento_id))
            conn.commit()
            print("Status atualizado com sucesso!")
            return redirect(url_for('finan.tab', status=pagamento_status))
        # Obter os dados do pagamento
        cur = conn.cursor()
        cur.execute("SELECT * FROM pagamentos WHERE id = ?", (pagamento_id,))
        pagamento = cur.fetchone()
        cur.close()

        if not pagamento:
            flash("Pagamento não encontrado!", "error")
            return redirect(url_for('finan.tab'))

        return render_template('financeiro/alt_page.html', pagamento=pagamento, status=pagamento_status)
    except Exception as e:
        flash(f"Erro ao editar pagamento: {e}", "error")
        return redirect(url_for('finan.tab', status=pagamento_status ))
    finally:
        conn.close()

@finan_bp.route('/return')
def return_():
    return render_template('financeiro/return.html')

@finan_bp.route('/csv')
@acesso('financeiro')

def exportar_csv():
    conn= sqlite3.connect(current_app.config['DATABASE'])
    try:
        cur= conn.cursor()
        
        #obtem o status do filtro.
        status_filtro = request.args.get('status', '').strip() or 'todos'
        print(f"Parâmetros recebidos na URL: {request.args}")  # Depuração
        print(f"Status recebido para exportação: {status_filtro}")  # Depuração

        if status_filtro == 'todos' or status_filtro == '':
            cur.execute("SELECT * FROM pagamentos")

        else:
            cur.execute("SELECT * FROM pagamentos WHERE status = ?", (status_filtro,))
        
        pagamentos = cur.fetchall()
        cur.close()

        output= io.StringIO()
        writer = csv.writer(output)

        #cabeçalho do csv
        writer.writerow(['ID', 'ID_USR', 'Contrato', 'Responsável', 'Valor', 'Data Pagamento', 'Método', 'Descrição', 'Status', 'Atendente'])

        for pagamento in pagamentos:
            writer.writerow(pagamento)

        response = Response(output.getvalue(), mimetype="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=pagamentos.csv"
        return response
    except Exception as e:
        print(f"Erro ao exportar CSV: {e}", "error")
        return redirect(url_for('finan.tab'))

    finally:
        conn.close()


@finan_bp.route('/alter')
def alter():
    tipo_usuario= session.get('tipo_usuario')

    if tipo_usuario == 'financeiro':
        return redirect(url_for('finan.definir'))
    
    else:
        return redirect(url_for('finan.tab'))
    
pass

@finan_bp.route('/download_csv')
def download_csv():
    pass