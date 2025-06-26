import sqlite3
from flask import current_app

def get_db_connection(database_path=None):
    """
    Retorna uma conexão com o banco de dados.
    Se `database_path` for fornecido, usa esse caminho; caso contrário, usa o banco configurado no Flask.
    """
    db_path = database_path or current_app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False, database_path=None):
    """
    Executa uma consulta no banco de dados.
    """
    conn = get_db_connection(database_path)
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def salvar_venda(venda, responsavel, titular, dependentes, database_path=None):
    """
    Salva os dados da venda, responsável, titular e dependentes no banco de dados.
    Agora usa apenas proposta_id (TEXT) como referência, sem venda_id.
    """
    try:
        conn = get_db_connection(database_path)
        cur = conn.cursor()

        # Inserir dados da venda
        cur.execute("""
            INSERT INTO venda (numero_proposta, data_venda, tipo_contrato, tipo_produto, corretor_resp, status, digitador, valor_venda, dt_cadastro, taxa_inscricao, iss, valor_tabela, vidas, nome_responsavel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (venda['numero_proposta'], venda['data_venda'], venda['tipo_contrato'], venda['tipo_produto'],
              venda['corretor_resp'], venda['status'], venda['digitador'], venda['valor_venda'], venda['dt_cadastro'], venda['taxa_inscricao'], venda['iss'], venda['valor_tabela'], venda['vida'], venda['nome_responsavel']))

        proposta_id = venda['numero_proposta']  # Usar o número da proposta como referência

        # Inserir dados do responsável
        cur.execute("""
            INSERT INTO responsavel (proposta_id, nome, cpf, data_nascimento, cep, celular, email, estado_civil)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (proposta_id, responsavel['nome'], responsavel['cpf'], responsavel['data_nascimento'],
              responsavel['endereco'], responsavel['celular'], responsavel['email'], responsavel['estado_civil']))

        # Inserir dados do titular
        cur.execute("""
            INSERT INTO titulares (proposta_id, nome, cpf, data_nascimento, idade, cep, celular, email, estado_civil, nome_mae, nome_pai, sexo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (proposta_id, titular['nome'], titular['cpf'], titular['data_nascimento'], titular['idade'],
              titular['endereco'], titular['celular'], titular['email'], titular['estado_civil'],
              titular['nome_mae'], titular['nome_pai'], titular['sexo']))

        # Inserir dados dos dependentes
        for dependente in dependentes:
            cur.execute("""
                INSERT INTO dependentes (proposta_id, nome, cpf, data_nascimento, grau_parentesco, cpf_titular,mae_dependente)
                VALUES (?, ?, ?, ?, ?, ?,?)
            """, (proposta_id, dependente['nome'], dependente['cpf'], dependente['data_nascimento'],
                  dependente['grau_parentesco'], dependente['cpf_titular'],dependente['mae_dependente']))

        conn.commit()
        conn.close()

    except Exception as e:
        conn.rollback()
        conn.close()
        raise e