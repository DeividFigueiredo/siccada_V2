from flask import Blueprint, render_template, request, session,redirect,url_for
from ..models.database import query_db, salvar_venda
import re
from app.utils import login_required, acesso, hierarquia
from datetime import datetime
import sqlite3
from flask import current_app


def listar_vendedor():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE classe_usuario = 'vendedor'")
    vendedores = cur.fetchall()
    cur.close()
    conn.close()
    return vendedores

vendas_bp = Blueprint('vendas', __name__)


def formatar_cpf(cpf):
    cpf= re.sub(r'\D','',cpf)
    if len(cpf) != 11:
        return None
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


@vendas_bp.route('/')
def home():

    return render_template('vendas/home.html')


@vendas_bp.route('/cpf',methods=['GET','POST'])
@login_required

def cpf():
    if request.method == "POST":
        cpf_input = request.form["cpf"]
        tipo=request.form["tipo"]
        # Consulta ao banco por CPF
        cpf= formatar_cpf(cpf_input)
        if not cpf:
            return render_template("vendas/verify.hTml", error="CPF invalido.")
        
        if tipo == "beneficiario":
            coluna = "sCpfUSR"
            tabela = "beneficiarios"
        elif tipo == "responsavel":
            coluna = "sCpfCgcResp"
            tabela = "beneficiarios"
        else:
            return render_template("vendas/verify.html", error="Tipo de busca inválido.")

        
        
        query = f"SELECT * FROM {tabela} WHERE {coluna} = ?"
        result = query_db(query, [cpf], one=False)

        

        return render_template('vendas/lista_cpf.html', result=result)

    return render_template("vendas/verify.html")



@vendas_bp.route('/lista_cpf')
def lista_retorno():    
   
    result = request.args.get('result')
    result('vendas/lista_cpf.html', result=result)


@vendas_bp.route('/nova_venda')
@acesso('vendas','cadastro')
@hierarquia('supervisor','agente','vendedor')
def nova_venda():
    vendedor = listar_vendedor()
    print("Vendedores:", vendedor)  # Para verificar a lista de vendedores

    return render_template('vendas/vendas_form.html', vendedor=vendedor)

@vendas_bp.route('/saldobenef')
@acesso('vendas','cadastro')
@hierarquia('supervisor','agente','vendedor')
def saldos():

    campo_result = request.args.get('campo_result')  # Recebe o parâmetro da URL
    print("campo_result:", campo_result)  # Para verificar o valor completo de campo_result

    if campo_result:
        # Realiza a consulta usando 'campo_result' como parâmetro (por exemplo, 'numero_contrato' ou 'nome_responsavel')
        try:
            query = "SELECT * FROM saldo_benef WHERE contrato = ?"
            result_saldo = query_db(query, [campo_result], one=True)  # Use sua função de consulta ao banco

            if result_saldo:
                return render_template('vendas/vendassaldo.html', result=result_saldo)
        
        except Exception as e:
            return f"Erro: {e}"
    
        return render_template('vendas/vendassaldo.html', error="Nenhum dado encontrado para o contrato.")
    
    return render_template('vendas/vendassaldo.html', error="Parâmetro inválido.")


@vendas_bp.route('venda_form', methods=['GET','POST'])
@login_required
@acesso('vendas','cadastro')
@hierarquia('supervisor','agente','vendedor')


def venda_form():  
    nome_usuario = session.get('user_nome')
    print(nome_usuario)
    
    try:
        print(nome_usuario)
        # Dados da venda
        venda = {
            "numero_proposta": request.form.get('numero_proposta'),
            "data_venda": request.form.get('data_venda'),
            "tipo_contrato": request.form.get('tipo_contrato'),
            "tipo_produto": request.form.get('tipo_produto'),
            "corretor_resp": request.form.get('corretor_resp'),
            "status": "Enviado ao cadastro",
            "digitador": nome_usuario,
            "valor_venda": float(request.form.get('valor_venda', '0').replace(',', '.')),
            "dt_cadastro": datetime.now().strftime("%d-%m-%Y"),
        }

        # Calcular valores adicionais
        venda["taxa_inscricao"] = 15.00 if venda["tipo_contrato"] == "individual" else 30.00
        venda["iss"] = 0.05 if venda["tipo_contrato"] == "empresarial" else 0
        valor_base = venda["valor_venda"] - venda["taxa_inscricao"]
        if venda['iss']>0:
            valor_iss= valor_base * venda['iss']
            valor_base -= valor_iss           
        else:
            valor_iss= 0
            venda["valor_tabela"] = round(valor_base,2)
            

        venda['valor_tabela'] = valor_base
        venda['iss'] = valor_iss
        print(f"Valor base após ISS: {valor_base}")


        # Dados do responsável
        responsavel = {
            "nome": request.form.get('nome_responsavel'),
            "cpf": request.form.get('cpf_responsavel'),
            "data_nascimento": request.form.get('dt_nascimento_responsavel'),
            "endereco": request.form.get('endereco_responsavel'),
            "celular": request.form.get('celular_responsavel'),
            "email": request.form.get('email_responsavel'),
            "estado_civil": request.form.get('estado_cv_responsavel')
        }
        
        

        # Dados do titular
        titular = {
            "nome": request.form.get('nome_beneficiario'),
            "cpf": request.form.get('cpf_beneficiario'),
            "data_nascimento": request.form.get('dt_nascimento_beneficiario'),
            "idade": request.form.get('idade_beneficiario'),
            "endereco": request.form.get('endereco_beneficiario'),
            "celular": request.form.get('celular_titular'),
            "email": request.form.get('email_titular'),
            "estado_civil": request.form.get('estado_cv_beneficiario'),
            "nome_mae": request.form.get('nome_mae_beneficiario'),
            "nome_pai": request.form.get('nome_pai_beneficiario'),
            "sexo": request.form.get('sexo_beneficiario'),
            "quantidade_titular" : 1
        }
        

        # Dados dos dependentes
        quantidade_dependentes = int(request.form.get('quantidade_dependentes', 0))
        dependentes = []
        nomes_dependentes = request.form.getlist('nome_dependente[]')
        cpfs_dependentes = request.form.getlist('cpf_dependente[]')
        datas_nascimento_dependentes = request.form.getlist('dt_nascimento_dependente[]')
        graus_parentesco_dependentes = request.form.getlist('grau_parentesco_dependente[]')
        mae_dependente = request.form.getlist('mae_dependente[]')

        print("Nomes dependentes:", nomes_dependentes)
        print("CPFs dependentes:", cpfs_dependentes)
        print("Datas nascimento dependentes:", datas_nascimento_dependentes)
        print("Graus parentesco dependentes:", graus_parentesco_dependentes)
        print("Mães dependente:", mae_dependente)

        # Usa o menor tamanho entre as listas para evitar erro de index
        num_dependentes = min(
            len(nomes_dependentes),
            len(cpfs_dependentes),
            len(datas_nascimento_dependentes),
            len(graus_parentesco_dependentes),
            len(mae_dependente)
        )

        for i in range(num_dependentes):
            dependente = {
                "nome": nomes_dependentes[i],
                "cpf": cpfs_dependentes[i],
                "data_nascimento": datas_nascimento_dependentes[i],
                "grau_parentesco": graus_parentesco_dependentes[i],
                "mae_dependente": mae_dependente[i]
            }
            print(f"Dependente {i}: {dependente}")
            dependente["cpf_titular"] = titular["cpf"]
            dependente["data_nascimento"] = datetime.strptime(dependente["data_nascimento"], "%Y-%m-%d").strftime("%d/%m/%Y")
            dependentes.append(dependente)
            quantidade_dependentes += 1
        print(f"Quantidade de dependentes: {quantidade_dependentes}")

        venda["vida"] = titular["quantidade_titular"] + quantidade_dependentes
        venda['nome_responsavel'] = responsavel['nome']
        print(venda['nome_responsavel'])
        print(venda["vida"])

        # Salvar os dados no banco
        salvar_venda(venda, responsavel, titular, dependentes)


        return render_template('vendas/concluido.html', venda=venda, responsavel=responsavel, titular=titular, dependentes=dependentes)
    except KeyError as e:
        return f"Erro: chave não encontrada {e}"

    except Exception as e:
        return f"Erro ao processar os dados: {e}"

