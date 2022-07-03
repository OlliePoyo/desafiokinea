import requests
import pandas as pd
from io import StringIO

class Debenture:
  def __init__(self, ativo):

    url_agenda = f"http://www.debentures.com.br/exploreosnd/consultaadados/eventosfinanceiros/agenda_e.asp?ativo={ativo}"
    results_agenda = requests.get(url_agenda)
    csvString_agenda=results_agenda.content.decode('Windows 1254')
    csvStringIO_agenda = StringIO(csvString_agenda)
    columns_agenda = ['data_evento', 'data_pgto', 'emissor', 'ativo', 'evento', 'tipo', 'taxa', 'liquidacao']
    df_agenda = pd.read_csv(csvStringIO_agenda, sep="\t", index_col=False, header=None, skiprows=[0,1,2], names=columns_agenda)

    df_agenda = df_agenda.drop(['data_evento', 'emissor', 'ativo', 'tipo'], axis = 1)
    df_agenda['taxa']=df_agenda['taxa'].str.replace(',','.').astype(float).div(100)
    df_agenda_amort = df_agenda[df_agenda['evento'] == 'Amortização']
    df_agenda_inicio = df_agenda[df_agenda.taxa>0].iloc[[0]]
    df_agenda_inicio['data_pgto'] = df_agenda.loc[0,'data_pgto']
    df_agenda_fim = df_agenda.iloc[[-1]]
    df_agenda_inicio['taxa'] = (1+df_agenda_inicio['taxa'].mul(-1))**(1/2)-1
    df_agenda_fim['taxa']= 1.0
    self.agenda = df_agenda_inicio.append(df_agenda_amort, ignore_index=True).append(df_agenda_fim, ignore_index=True).drop(['evento', 'liquidacao'], axis=1)

    url_caracteristicas = f"http://www.debentures.com.br/exploreosnd/consultaadados/emissoesdedebentures/caracteristicas_e.asp?Ativo={ativo}"
    results_caracteristicas = requests.get(url_caracteristicas)
    csvString_caracteristicas = results_caracteristicas.content.decode('Windows 1254')
    csvStringIO_caracteristicas = StringIO(csvString_caracteristicas)
    self.caracteristicas = pd.read_csv(csvStringIO_caracteristicas, sep="\t", index_col=False, skiprows=[0,1,2])
    self.vne = float(self.caracteristicas['Valor Nominal na Emissao'].values[0])
    self.juros_taxa = float(self.caracteristicas['Juros Criterio Novo - Taxa'].values[0].replace(',','.'))/100
