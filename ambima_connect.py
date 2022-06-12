# import logging
import requests
import base64 as b64
import json

client_id = "9r2j5fK3DntV"
client_secret = "ufaORoKwRRmw"

def b64encode(data:str) -> str:
  "Codifica uma string em base64"
  encodedBytes = b64.b64encode(data.encode("utf-8"))
  encodedStr = str(encodedBytes, "utf-8")
  return encodedStr

def get_access_token(_id:str, secret:str) -> requests.models.Response:
    """Recebe id e secret de um dado app e retorna o toke de acesso para aquele app"""
    address = "https://api.anbima.com.br/oauth/access-token?"
    credentials = b64encode(f"{_id}:{secret}")
    body = {"grant_type": "client_credentials"}
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    # logging.debug(f"Auth headers: {headers}")
    res = requests.post(address, headers=headers, json=body)
    # logging.info(f"Auth res status: {res.status_code}")
    # logging.debug(f"Auth res text: {res.text}")
    token = json.loads(res.content)["access_token"]
    return token

class AmbimaConnect:
    client_id = "9r2j5fK3DntV"
    client_secret = "ufaORoKwRRmw"
    access_token = get_access_token(client_id, client_secret)

    address_base = "https://api-sandbox.anbima.com.br"
    address_book = {
        'titulos_publicos':f'{address_base}/feed/precos-indices/v1/titulos-publicos/mercado-secundario-TPF',
        'selic': f'{address_base}/feed/precos-indices/v1/titulos-publicos/estimativa-selic',
        'vna': f"{address_base}/feed/precos-indices/v1/titulos-publicos/vna",
        'ipca_igpm': f'{address_base}/feed/precos-indices/v1/titulos-publicos/projecoes',
        'debentures':f'{address_base}/feed/precos-indices/v1/debentures/mercado-secundario',
    }

    def __init__(self, category: str, params:dict={}):
        self.address = AmbimaConnect.address_book[category.lower()]
        for key in params: self.address += f'?{key}={params[key]}'
        headers = {
            "Content-Type": "application/json",
            "access_token": AmbimaConnect.access_token,
            "client_id": AmbimaConnect.client_id
        }
        # logging.debug(f"Auth headers: {headers}")
        self.res = requests.get(self.address, headers=headers)
        if self.res.status_code == 401:
            AmbimaConnect.access_token = get_access_token(AmbimaConnect.client_id, AmbimaConnect.client_secret)
            headers['access_token'] = AmbimaConnect.access_token
            self.res = requests.get(self.address, headers=headers)
        # logging.info(f"Auth res status: {self.res.status_code}")
        
        self.content = json.loads(self.res.content)
