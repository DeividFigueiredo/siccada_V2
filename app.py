from flask import Flask, request, render_template
import sqlite3
import re

app = Flask(__name__)

# Caminho para o banco de dados
DATABASE = 'MHV_DB.db'

def query_db(query, args=(), one=False):
    """Executa uma consulta no banco de dados."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def formatar_cpf(cpf):
    cpf= re.sub(r'\D','',cpf)
    if len(cpf) != 11:
        return None
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        cpf_input = request.form["cpf"]
        tipo=request.form["tipo"]
        # Consulta ao banco por CPF
        cpf= formatar_cpf(cpf_input)
        if not cpf:
            return render_template("index.hTml", error="CPF invalido.")
        
        if tipo == "beneficiario":
            coluna = "sCpfUSR"
            tabela = "beneficiarios"
        elif tipo == "responsavel":
            coluna = "sCpfCgcResp"
            tabela = "beneficiarios"
        else:
            return render_template("index.html", error="Tipo de busca inválido.")

        
        
        query = f"SELECT * FROM {tabela} WHERE {coluna} = ?"
        result = query_db(query, [cpf], one=True)

        return render_template("result.html", result=result, cpf=cpf)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5001', debug=True)
