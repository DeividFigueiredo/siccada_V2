import re

def formatar_cpf(cpf):
    cpf= re.sub(r'\D','',cpf)
    if len(cpf) != 11:
        return None
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


cpf_test = "07454358748"
print(formatar_cpf(cpf_test))  # Deve retornar: 074.543.587-48
