from app.models.database import salvar_venda
from flask import Flask

# Configurar o app Flask para usar o banco de dados
app = Flask(__name__)
app.config['DATABASE'] = 'MHV_DB'  # Substitua pelo caminho do seu banco de dados

# Dados simulados para teste
venda = {
    "numero_proposta": "12345",
    "data_venda": "2025-04-18",
    "tipo_contrato": "Residencial",
    "tipo_produto": "Seguro",
    "corretor_resp": "João Corretor",
    "status": "Ativo"
}

responsavel = {
    "nome": "João da Silva",
    "cpf": "123.456.789-00",
    "data_nascimento": "1980-01-01",
    "endereco": "Rua Exemplo, 123",
    "celular": "(11) 98765-4321",
    "email": "joao@example.com",
    "estado_civil": "Casado"
}

titular = {
    "nome": "Maria da Silva",
    "cpf": "987.654.321-00",
    "data_nascimento": "1990-02-02",
    "idade": 35,
    "endereco": "Rua Exemplo, 123",
    "celular": "(11) 91234-5678",
    "email": "maria@example.com",
    "estado_civil": "Casada",
    "nome_mae": "Ana da Silva",
    "nome_pai": "Carlos da Silva",
    "sexo": "Feminino"
}

dependentes = [
    {
        "nome": "Pedro da Silva",
        "cpf": "111.222.333-44",
        "data_nascimento": "2010-03-03",
        "grau_parentesco": "Filho"
    },
    {
        "nome": "Paula da Silva",
        "cpf": "555.666.777-88",
        "data_nascimento": "2015-04-04",
        "grau_parentesco": "Filha"
    }
]

# Testar a função salvar_venda
with app.app_context():
    try:
        salvar_venda(venda, responsavel, titular, dependentes)
        print("Venda salva com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar venda: {e}")