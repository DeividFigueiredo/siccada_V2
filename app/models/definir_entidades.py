class Venda:
    def __init__(self, numero_proposta, data_venda, tipo_contrato, tipo_produto, corretor_resp,status):
        self.numero_proposta = numero_proposta
        self.data_venda = data_venda
        self.tipo_contrato = tipo_contrato
        self.tipo_produto = tipo_produto
        self.corretor_resp=corretor_resp
        self.status=status

class Responsavel:
    def __init__(self, nome, cpf, data_nascimento, endereco, celular, email, estado_civil):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.endereco = endereco
        self.celular = celular
        self.email = email
        self.estado_civil = estado_civil


class Titular:
    def __init__(self, nome, cpf, data_nascimento, idade, endereco, celular, email, estado_civil, nome_mae, nome_pai, sexo):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.idade = idade
        self.endereco = endereco
        self.celular = celular
        self.email = email
        self.estado_civil = estado_civil
        self.nome_mae = nome_mae
        self.nome_pai = nome_pai
        self.sexo = sexo


class Dependente:
    def __init__(self, nome, cpf, data_nascimento, grau_parentesco):
        self.nome = nome
        self.cpf = cpf
        self.data_nascimento = data_nascimento
        self.grau_parentesco = grau_parentesco


