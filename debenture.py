import requests
import pandas as pd
from io import StringIO
from retry import retry

@retry(ConnectionError, delay=1, tries=4, jitter=2)
def get_caracteristicas(ativo):
  url_caracteristicas = f"http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_e.asp?Ativo={ativo}"
  results_caracteristicas = requests.get(url_caracteristicas)
  csvString_caracteristicas = results_caracteristicas.content.decode('Windows 1254')
  csvStringIO_caracteristicas = StringIO(csvString_caracteristicas)
  return csvStringIO_caracteristicas

class Debenture:
  def __init__(self, ativo):
    url_agenda = f"http://www.debentures.com.br/exploreosnd/consultaadados/eventosfinanceiros/agenda_e.asp?ativo={ativo}"
    results_agenda = requests.get(url_agenda)
    csvString_agenda=results_agenda.content.decode('Windows 1254')
    csvStringIO_agenda = StringIO(csvString_agenda)
    columns_agenda = ['data_evento', 'data_pgto', 'emissor', 'ativo', 'evento', 'tipo', 'taxa', 'liquidacao']
    df_agenda = pd.read_csv(csvStringIO_agenda, sep="\t", index_col=False, header=None, skiprows=[0,1,2], names=columns_agenda)

    df_agenda = df_agenda.drop(['data_evento', 'emissor', 'ativo', 'tipo', 'liquidacao'], axis = 1)
    df_agenda['taxa']=df_agenda['taxa'].str.replace(',','.').astype(float).div(100)
    df_agenda_amort = df_agenda[(df_agenda['evento'] == 'Amortização') | (df_agenda['evento'] == 'Vencimento')].reset_index()

    df_agenda_amort.loc[0, 'remaining'] = 1- df_agenda_amort.loc[0, 'taxa']
    df_agenda_amort.loc[0, 'amort_perc'] = 1 - df_agenda_amort.loc[0, 'remaining']
    df_agenda_amort.loc[len(df_agenda_amort)-1, 'taxa'] = 1.0
    for i in range(1, len(df_agenda_amort)):
      df_agenda_amort.loc[i, 'remaining'] = df_agenda_amort.loc[i-1, 'remaining'] * (1-df_agenda_amort.loc[i, 'taxa'])
      df_agenda_amort.loc[i, 'amort_perc'] = df_agenda_amort.loc[i-1, 'remaining'] - df_agenda_amort.loc[i, 'remaining']
    df_agenda_amort['taxa'] = df_agenda_amort['amort_perc']
    df_agenda_amort = df_agenda_amort.drop(['amort_perc', 'remaining'], axis = 1)

    for i in df_agenda_amort['index'].to_list():
      df_agenda.loc[i, 'taxa'] = float(df_agenda_amort[df_agenda_amort['index']==i]['taxa'])
    self.agenda_completa = df_agenda

    df_agenda_amort = df_agenda_amort.drop(['index'], axis = 1)

    df_agenda_inicio = df_agenda[df_agenda.taxa>0].iloc[[0]]
    df_agenda_inicio['data_pgto'] = df_agenda.loc[0,'data_pgto']
    df_agenda_inicio['taxa'] = (1+df_agenda_inicio['taxa'].mul(-1))**(1/2)-1
    self.agenda_amort = df_agenda_inicio.append(df_agenda_amort, ignore_index=True).drop(['evento'], axis=1)

    csvStringIO_caracteristicas = get_caracteristicas(ativo)
    self.caracteristicas = pd.read_csv(csvStringIO_caracteristicas, sep="\t", index_col=False, skiprows=[0,1,2])
    self.vne = float(self.caracteristicas['Valor Nominal na Emissao'].values[0])
    self.juros_taxa = float(str(self.caracteristicas['Juros Criterio Novo - Taxa'].values[0]).replace(',','.'))/100
    self.inicio_rent = self.caracteristicas[' Data do Inicio da Rentabilidade'].values[0]
