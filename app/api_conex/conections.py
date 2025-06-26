import requests

def consultar_api():
    #url da api
    url= 'https://sandbox.rapidoc.tech/tema'

    #headers 
    headers= {
        "Authorization": "Bearer eyJhbGciOiJSUzUxMiJ9.eyJjbGllbnQiOiJNSFZJREEifQ.dpb8Lazd9TDs1tKIhYi2TOTIPr6gnF_s1RdczDwLmpaP14lIY9Lp0XFb9I54kJOjgZ2d6jK6AxbMPDJ7ifioUK12jVBtvaB-wkKtl6NajpURab8mb2YGzeg-JNOF2JMfk80fdI-PYxwv2fq-QgJCq2dNgr8X_D3gXVfa3P6J5Z3UlOP0VvebB_KFUkKY1izLOhKMHlmWq5frXlxlshOy40u_9Rz-dO9fSazEiu5exCbSRCzX240PbG0I-Gvuc02CY-XQ0ypAogA5OpHMVSVCB20Ol_FUD2ls5Rom4Vo-ghOCSg7xVwfEoB6G1Yp6IfY13v_s0RADxGSZxUJa5HSeadrQ-mGVs9keylBTjdmzwANI-rd6JqM1XkbsAi0Yrygwf47lj0CuqDfVSim_9ADUy4tCP7Mwt1SD0ivoXq3wefX104YzBj-Uzd8FXeXMUQIo0VQyaXQ37U4Y__I2BNf2FBgY5eXfmfYX1ebnkI9VtJWSojVoHBG-nA8uJOYy4qyqdWnY6B64ibI674RVI1iuafEmLIWhbCw1G_nD1VPUejbG1lJCnV2s-mUJPoS9_qrAnNVShMaKElXB4nVAIrSbzW_bdsGhiqJJXmuvFxVCOzIbexFtBdT-VDwZdcik0SZDgfI1XsVqXnaMsZprSzXtofxDhF-MU8my4mEzKUz0Kys",
        "x-rapidoc-client": "3163f8c7-cd1a-4e04-a54d-d5335e9afd10",
        "Content-Type": "application/json"
    }

    #teste

    response = requests.get(url, headers=headers)

    # Verifique o status e imprima a resposta
    print("Status Code:", response.status_code)
    print("Resposta JSON:", response.json())

def consultar_cep(cep):
    """
    Consulta um CEP usando a API ViaCEP.
    Retorna um dicionário com os dados do endereço ou None se não encontrar.
    """
    cep = ''.join(filter(str.isdigit, str(cep)))
    if len(cep) != 8:
        return None

    url = f'https://viacep.com.br/ws/{cep}/json/'
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if 'erro' in data:
            return None
        return data
    except Exception as e:
        print(f"Erro ao consultar CEP: {e}")
        return None

# Exemplo de uso:
if __name__ == "__main__":
    resultado = consultar_cep('23098006')
    print(resultado)