import logging
logging.level=logging.INFO
from typing import Dict, List
import pandas as pd
from ambima_connect import AmbimaConnect
import utils
from io import StringIO
import requests
from titulos import LTN, NTNB, NTNF, LFT, Priv

def clean_list(list_to_clean:List[Dict], keep_keys):
    res = [{key : val for key, val in sub.items() if key in keep_keys} for sub in list_to_clean]
    return res

def list_debentures():
    url_list = 'http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_e.asp?op_exc=False'
    results_list = requests.get(url_list)
    csvString_list=results_list.content.decode('Windows 1254')
    csvStringIO_list = StringIO(csvString_list)
    df_list = pd.read_csv(csvStringIO_list, sep="\t", index_col=False, skiprows=[0,1,2])
    ativos = df_list['Codigo do Ativo'].str.replace(' ', '').tolist()
    return ativos

def list_public():
    public = AmbimaConnect('titulos publicos').content
    clean_public = clean_list(public, ['tipo_titulo','data_referencia','data_vencimento','taxa_indicativa','pu'])
    return clean_public

def handler():
    public_list = list_public()

    for titulo in public_list:
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

        send_to_sql(
            tipo=calc.tipo,
            data_venc=calc.data_venc,
            data_ref=calc.data_ref,
            taxa=calc.taxa,
            pu=calc.pu,
            pm=calc.pm,
            duration=calc.duration,
            )

    deb_list = list_debentures()

    for codigo in deb_list:
        deb = Priv(codigo_ativo=codigo)

        send_to_sql(
            tipo=deb.codigo_ativo,
            pm=deb.pm,
            duration=deb.duration,
            )
