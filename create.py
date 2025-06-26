import pandas as pd
import sqlite3
import shutil
import os

# Caminho do arquivo CSV
csv_file = r"C:\Users\d.figueiredo\Desktop\banco\lista_aberto_pagamento.csv"
db_name = "MHV_DB.db"

# Função para criar a tabela beneficiarios
def criar_tabela_beneficiarios():
    df = pd.read_csv(csv_file, delimiter=';', encoding='latin1')

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS beneficiarios (
        sCodigoUSRTIT TEXT,
        sNomeTIT TEXT,
        iControleTIT INTEGER,
        dMatricula TEXT,
        dNascimentoTIT TEXT,
        dExclusao TEXT,
        sMotivoCancelamentoTIT TEXT,
        sDescricaoCancTit TEXT,
        Fone_TIT TEXT,
        iDiaVenctoPadraoCNT INTEGER,
        iDiaVenctoPadraoTIT INTEGER,
        sCodigoUSR TEXT,
        sNomeUSR TEXT,
        dMatriculaUSR TEXT,
        dExclusaoUSR TEXT,
        dNascimento TEXT,
        sCpfUSR TEXT,
        sMotivoCancelamentoUSR TEXT,
        sDescricaoCancUsu TEXT,
        sNomePRD TEXT,
        dExclusaoPUSR TEXT,
        sNomeProduto TEXT,
        cPrecoPRD REAL,
        IdadeUSR INTEGER,
        IdadeTIT INTEGER,
        TempoPermanenciaUSR INTEGER,
        TempoPermanenciaTIT INTEGER,
        sTipoUsuario TEXT
    );
    """)

    df.to_sql("beneficiarios", conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Tabela 'beneficiarios' criada e populada com sucesso!")

# Nova função para criar a tabela usuarios
def criar_tabela_usuarios():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        senha TEXT NOT NULL,
        tipo_usuario TEXT NOT NULL,
        autorizado INTEGER DEFAULT 0 CHECK(autorizado IN (0, 1))
    );
    """)

    conn.commit()
    conn.close()
    print("Tabela 'usuarios' criada com sucesso!")

def alterar():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    cursor.execute("""
       ALTER TABLE usuarios RENAME TO usuarios_bkp;       
""")
    
    print('alterado')


def copiar_usr():
    conn= sqlite3.connect(db_name)
    cursor= conn.cursor()

    cursor.execute("""
    INSERT INTO usuarios (id, nome, cpf, email, senha, tipo_usuario, autorizado)
    SELECT id, nome, cpf, email, senha, tipo_usuario, autorizado
    FROM usuarios_bkp;
""")
    
    print('copiados')


def criar_novatab():
    conn= sqlite3.connect(db_name)
    cursor= conn.cursor()
    cursor.execute("""
    CREATE TABLE pagamentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_usuario INTEGER NOT NULL, -- Relaciona com a tabela de usuários,
    ncontrato TEXT,
    nresponsavel TEXT NOT NULL,
    valor REAL NOT NULL,
    data_pagamento DATE NOT NULL,
    metodo_pagamento TEXT NOT NULL, -- Exemplo: 'PIX', 'Cartão', 'Boleto'
    descricao TEXT, -- Detalhes adicionais sobre o pagamento
    status TEXT DEFAULT 'pendente' CHECK(status IN ('efetuado', 'baixado', 'cancelado')),
    nusuario TEXT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id)
);""")

def criar_venda():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS venda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_proposta TEXT NOT NULL UNIQUE,
        data_venda DATE NOT NULL,
        tipo_contrato TEXT NOT NULL,
        tipo_produto TEXT NOT NULL,
        corretor_resp TEXT NOT NULL,
        status TEXT,
        digitador varchar(50),
        valor_venda REAL NOT NULL,
        dt_cadastro DATE NOT NULL,
        taxa_inscricao REAL NOT NULL,
        iss REAL NOT NULL,
        valor_tabela REAL NOT NULL,
        numero_contrato TEXT,
        last_resp TEXT,
        vidas INTEGER NOT NULL,
        finalizado_em DATE,
        exportado INTEGER DEFAULT 0 CHECK(exportado IN (0, 1))
    );
    """)
    conn.commit()
    conn.close()
    print("Tabela 'vendas' criada com sucesso!")

def criar_responsavel():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS responsavel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposta_id TEXT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        data_nascimento DATE NOT NULL,
        cep TEXT NOT NULL,
        celular TEXT NOT NULL,
        email TEXT NOT NULL,
        estado_civil TEXT NOT NULL,
        FOREIGN KEY (proposta_id) REFERENCES venda (numero_proposta) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()
    print("Tabela 'responsaveis' criada com sucesso!")

def criar_titular():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS titulares")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS titulares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposta_id TEXT NOT NULL UNIQUE,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL UNIQUE,
        data_nascimento DATE NOT NULL,
        idade INTEGER NOT NULL,
        cep TEXT NOT NULL,
        celular TEXT NOT NULL,
        email TEXT NOT NULL,
        estado_civil TEXT NOT NULL,
        nome_mae TEXT NOT NULL,
        nome_pai TEXT,
        sexo TEXT NOT NULL,
        FOREIGN KEY (proposta_id) REFERENCES venda (numero_proposta) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()
    print("Tabela 'titulares' criada com sucesso!")

def criar_dependente():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dependentes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        proposta_id TEXT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL,
        data_nascimento DATE NOT NULL,
        grau_parentesco TEXT NOT NULL,
        cpf_titular TEXT NOT NULL,
        FOREIGN KEY (proposta_id) REFERENCES venda (numero_proposta) ON DELETE CASCADE,
        FOREIGN KEY (cpf_titular) REFERENCES titulares (cpf) ON DELETE CASCADE
    );
    """)
    conn.commit()
    conn.close()
    print("Tabela 'dependentes' criada com sucesso!")

def criar_saldo():
    df = pd.read_csv(csv_file, delimiter=';', encoding='latin1')

    conn= sqlite3.connect(db_name)
    cursor= conn.cursor()
    cursor.execute("""
    CREATE TABLE saldo_benef (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_contrato TEXT NOT NULL,
    nome_responsavel TEXT NOT NULL,
    parcela_abt REAL NOT NULL,
    valor_total REAL NOT NULL
    );""")
    
    df.to_sql("saldo_benef", conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()
    print("Tabela 'beneficiarios' criada e populada com sucesso!")

def resetar_tabelas():
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF")

    cursor.execute("DROP TABLE IF EXISTS dependentes")
    cursor.execute("DROP TABLE IF EXISTS titulares")
    cursor.execute("DROP TABLE IF EXISTS responsavel")
    cursor.execute("DROP TABLE IF EXISTS venda")

    cursor.execute("PRAGMA foreign_keys = ON")

    conn.commit()
    conn.close()
    print("Tabelas 'dependentes' e 'titulares' removidas com sucesso.")

def backup_and_replace_db(db_path, backup_path):
    # Cria backup do banco atual
    shutil.copy2(db_path, backup_path)
    print(f"Backup criado em: {backup_path}")

    # Remove o banco original
    os.remove(db_path)
    print(f"Banco original removido: {db_path}")

    # Restaura o backup (se quiser restaurar imediatamente)
    shutil.copy2(backup_path, db_path)
    print(f"Banco restaurado a partir do backup: {db_path}")

def backup_db(db_path, backup_path):
    """
    Cria um backup simples do banco SQLite, sem alterar nada no banco original.
    """
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"Backup criado em: {backup_path}")

def backup_tabelas_especificas(origem, destino, tabelas):
    """
    Cria um novo banco SQLite contendo apenas as tabelas especificadas e seus dados.
    """
    import sqlite3
    import shutil
    # Cria uma cópia do banco original
    shutil.copy2(origem, destino)
    conn = sqlite3.connect(destino)
    cursor = conn.cursor()
    # Lista todas as tabelas do banco
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    todas = [row[0] for row in cursor.fetchall()]
    # Remove as tabelas que não estão na lista desejada
    for tabela in todas:
        if tabela not in tabelas and not tabela.startswith('sqlite_'):
            cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
    conn.commit()
    conn.close()
    print(f"Backup criado em: {destino} apenas com as tabelas: {', '.join(tabelas)}")

def exportar_tabelas_para_novo_banco(origem, destino, tabelas):
    """
    Exporta apenas as tabelas especificadas e seus dados para um novo banco SQLite.
    """
    import sqlite3
    # Cria novo banco vazio
    conn_origem = sqlite3.connect(origem)
    conn_destino = sqlite3.connect(destino)
    cursor_origem = conn_origem.cursor()
    cursor_destino = conn_destino.cursor()
    for tabela in tabelas:
        # Recupera o comando de criação da tabela
        cursor_origem.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (tabela,))
        create_sql = cursor_origem.fetchone()
        if create_sql:
            cursor_destino.execute(create_sql[0])
            # Copia os dados
            cursor_origem.execute(f"SELECT * FROM {tabela}")
            rows = cursor_origem.fetchall()
            if rows:
                # Monta o insert
                n_cols = len(rows[0])
                placeholders = ','.join(['?'] * n_cols)
                cursor_destino.executemany(f"INSERT INTO {tabela} VALUES ({placeholders})", rows)
    conn_destino.commit()
    conn_origem.close()
    conn_destino.close()
    print(f"Novo banco '{destino}' criado apenas com as tabelas: {', '.join(tabelas)}")

def apagar_tabelas(tabelas, db_path):
    """
    Apaga as tabelas especificadas do banco SQLite informado.
    """
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for tabela in tabelas:
        cursor.execute(f"DROP TABLE IF EXISTS {tabela}")
    conn.commit()
    conn.close()
    print(f"Tabelas apagadas: {', '.join(tabelas)}")



# Chamando as funções
if __name__ == "__main__":
    # Garante que as tabelas serão zeradas antes de criar
   backup_db (db_name, "MHV_DB_backup.db")