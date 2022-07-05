import logging
logging.level=logging.INFO
from typing import Dict, List
import pandas as pd
from ambima_connect import AmbimaConnect
from sql_connect import send_to_sql
from io import StringIO
import requests
from titulos import LTN, NTNB, NTNF, LFT, Priv
from sql_utils import public_query_statement, debenture_query_statement

def public(limit=0):
    public_list = AmbimaConnect('titulos publicos').content
    if limit == 0:
        limit = len(public_list)-1
    for titulo in public_list[:limit]:
        if titulo['tipo_titulo'] == 'LTN':
            calc = LTN(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        elif titulo['tipo_titulo'] == 'NTN-B':
            calc = NTNB(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        elif titulo['tipo_titulo'] == 'NTN-F':
            calc = NTNF(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        elif titulo['tipo_titulo'] == 'LFT':
            calc = LFT(
                data_venc=titulo['data_vencimento'],
                taxa=titulo['taxa_indicativa']/100,
                data_ref=titulo['data_referencia'],
                )
        query_statement = public_query_statement(titulo, calc)
        send_to_sql(query_statement)

def list_debentures():
    url_list = 'http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_e.asp?op_exc=False'
    results_list = requests.get(url_list)
    csvString_list=results_list.content.decode('Windows 1254')
    csvStringIO_list = StringIO(csvString_list)
    df_list = pd.read_csv(csvStringIO_list, sep="\t", index_col=False, skiprows=[0,1,2])
    ativos = df_list['Codigo do Ativo'].str.replace(' ', '').tolist()
    return ativos

def debenture(limit=0):
    deb_list = list_debentures()
    if limit == 0:
        limit = len(deb_list)-1
    elif limit in deb_list:
        deb_list = [limit]
        limit = 1
    for codigo in deb_list[:limit]:
        deb = Priv(codigo_ativo=codigo)

        query_statement = debenture_query_statement(deb)
        send_to_sql(query_statement)

def handler():
    public()
    debenture()

if __name__ == "__main__":
    handler()
