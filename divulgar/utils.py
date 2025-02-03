import requests

def buscar_endereco(cep):
    url = f'https://viacep.com.br/ws/{cep}/json/'
    resposta = requests.get(url)
    if resposta.status_code == 200:
        dados = resposta.json()
        if 'erro' in dados:
            return False
        return dados
    else:
        return False

def extrair_numeros(string):
    # Filtrar apenas os caracteres que são dígitos
    numeros = [char for char in string if char.isdigit()]
    # Unir todos os números encontrados em uma única string
    return ''.join(numeros)

