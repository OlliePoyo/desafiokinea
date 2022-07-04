import pandas as pd
from dateutil.relativedelta import relativedelta
from cal import AmbimaCalendar
from datetime import date, datetime
from ambima_connect import AmbimaConnect
from debenture import Debenture

data_vna = AmbimaConnect('vna').content

def get_dias_cupom(start_date:date, end_date:date):
  """Retorna uma listagem de cupons entre duas datas, indo da data final até a inicial, de 6 em 6 meses"""
  pgto_date_list = list()
  pgto_date = end_date
  # Gera da lista de datas a partir da data final, em incrementos de 6 meses
  while pgto_date > start_date:
    pgto_date_list.append(pgto_date)
    pgto_date -= relativedelta(months=6)
  # Inverte a ordem da lista para crescente
  pgto_date_list=pgto_date_list[::-1]
  return pgto_date_list

def dias_uteis(start_date:date, end_date:date) -> int:
  """O formato de data é date(AAAA, MM, DD), como date(2022, 2, 4) para 4 de fev de 2022"""
  interval = AmbimaCalendar().get_working_days_delta(start_date, end_date)+1
  return interval

class LTN():
  def __init__(self, data_venc, taxa, data_ref):
    self.tipo = 'LTN'
    self.data_venc = data_venc
    self.taxa = taxa
    self.data_ref = data_ref
    
    d_data_ref=datetime.strptime(data_ref, "%Y-%m-%d").date()
    d_data_venc=datetime.strptime(data_venc, "%Y-%m-%d").date()

    self.duration = dias_uteis(d_data_ref, d_data_venc)
    self.pm = (d_data_venc - d_data_ref).days
    self.pu = 1000/((1+taxa)**(self.duration/252))

class NTNF():
  def __init__(self, data_venc, taxa, data_ref):
    self.tipo = 'NTNF'
    self.data_venc = data_venc
    self.taxa = taxa
    self.data_ref = data_ref
    
    d_data_ref=datetime.strptime(data_ref, "%Y-%m-%d").date()
    d_data_venc=datetime.strptime(data_venc, "%Y-%m-%d").date()
    
    lista_datas = get_dias_cupom(d_data_ref, d_data_venc)
    self.fluxo_pgto = pd.DataFrame(lista_datas, columns=['data_pgto'])
    self.fluxo_pgto['cupom_semestral'] = [(1.1**(1/2)-1)*1000]*len(lista_datas)
    self.fluxo_pgto['cupom_semestral'].iloc[-1] = self.fluxo_pgto['cupom_semestral'].iloc[-1] + 1000
    self.fluxo_pgto['dias_uteis'] = self.fluxo_pgto['data_pgto'].apply(lambda x: dias_uteis(d_data_ref, x))
    self.fluxo_pgto['dias_corridos'] = self.fluxo_pgto['data_pgto'].apply(lambda x: (x - d_data_ref).days)
    self.fluxo_pgto['vp_pgto'] = self.fluxo_pgto.apply(lambda x: (x['cupom_semestral'])/((1+taxa)**(x['dias_uteis']/252)), axis=1)

    self.pu = self.fluxo_pgto['vp_pgto'].sum()
    self.duration = (self.fluxo_pgto['vp_pgto']*self.fluxo_pgto['dias_uteis']).sum()/self.pu
    self.pm = (self.fluxo_pgto['cupom_semestral']*self.fluxo_pgto['dias_corridos']).sum()/self.fluxo_pgto['cupom_semestral'].sum()

class NTNB():
  def __init__(self, data_venc, taxa, data_ref):
    self.tipo = 'NTNB'
    self.data_venc = data_venc
    self.taxa = taxa
    self.data_ref = data_ref
    
    d_data_ref=datetime.strptime(data_ref, "%Y-%m-%d").date()
    d_data_venc=datetime.strptime(data_venc, "%Y-%m-%d").date()
  # d15_base = data_liqui.replace(day=15)
  # d15_proj = d15_base + relativedelta(months=1)
  
  # VNA deveria puxar dados de um banco, porém ainda não existe esse banco e o API tem só uma data em sandbox
  # Recomenda-se fazer teste de eficiencia. Talvez a chamada em api usando data como parametro seja preferível ao banco de dados
    self.vna = [x['vna'] for x in [x['titulos'] for x in data_vna if x['data_referencia']==self.data_ref][0] if x['codigo_selic']=='760100'][0]

    lista_datas = get_dias_cupom(d_data_ref, d_data_venc)
    self.fluxo_pgto = pd.DataFrame(lista_datas, columns=['data_pgto'])
    self.fluxo_pgto['fluxo'] = [(1.06**(1/2)-1)]*len(lista_datas)
    self.fluxo_pgto['fluxo'].iloc[-1] = self.fluxo_pgto['fluxo'].iloc[-1] + 1
    self.fluxo_pgto['dias_uteis'] = self.fluxo_pgto['data_pgto'].apply(lambda x: dias_uteis(d_data_ref, x))
    self.fluxo_pgto['dias_corridos'] = self.fluxo_pgto['data_pgto'].apply(lambda x: (x - d_data_ref).days)
    self.fluxo_pgto['vf_fluxo_taxa'] = self.fluxo_pgto.apply(lambda x: ((1+taxa)**(x['dias_uteis']/252)), axis=1)
    self.fluxo_pgto['cotacao'] = self.fluxo_pgto.apply(lambda x: x['fluxo']/x['vf_fluxo_taxa'], axis=1)

    self.fluxo_pgto['cupom_semestral'] = self.fluxo_pgto['fluxo']*self.vna
    self.fluxo_pgto['vp_pgto'] = self.fluxo_pgto['cupom_semestral']/self.fluxo_pgto['vf_fluxo_taxa']

    self.pu = self.fluxo_pgto['cotacao'].sum()*self.vna
    self.duration = (self.fluxo_pgto['vp_pgto']*self.fluxo_pgto['dias_uteis']).sum()/self.fluxo_pgto['vp_pgto'].sum()
    self.pm = (self.fluxo_pgto['cupom_semestral']*self.fluxo_pgto['dias_corridos']).sum()/self.fluxo_pgto['cupom_semestral'].sum()

class LFT():
  def __init__(self, data_venc, taxa, data_ref):
    self.tipo = 'LFT'
    self.data_venc = data_venc
    self.taxa = taxa
    self.data_ref = data_ref
    
    d_data_ref=datetime.strptime(data_ref, "%Y-%m-%d").date()
    d_data_venc=datetime.strptime(data_venc, "%Y-%m-%d").date()

    self.duration = dias_uteis(d_data_ref, d_data_venc)
    self.pm = (d_data_venc - d_data_ref).days

    self.vna = [x['vna'] for x in [x['titulos'] for x in data_vna if x['data_referencia']==self.data_ref][0] if x['codigo_selic']=='210100'][0]
    self.cotacao = (1+taxa)**(-self.duration/252)
    self.pu = self.vna*self.cotacao

class Priv():
  def __init__(self, codigo_ativo):
    self.codigo_ativo = codigo_ativo

    debenture = Debenture(codigo_ativo)

    self.caracteristicas = debenture.caracteristicas

    self.data_ref = datetime.strptime(debenture.inicio_rent, "%d/%m/%Y").date()
    
    self.fluxo_pgto = debenture.agenda
    self.fluxo_pgto['dias_uteis'] = self.fluxo_pgto['data_pgto'].apply(lambda x: dias_uteis(self.data_ref, datetime.strptime(x, "%d/%m/%Y").date()))
    self.fluxo_pgto['juros_perc'] = self.fluxo_pgto.loc[0, 'taxa']*(-1)

    self.fluxo_pgto.loc[0, 'remaining_perc'] = 1
    self.fluxo_pgto.loc[0, 'amort'] = debenture.vne * self.fluxo_pgto.loc[0, 'taxa']
    self.fluxo_pgto.loc[0, 'juros'] = debenture.vne * self.fluxo_pgto.loc[0, 'juros_perc']

    for i in range(1, len(self.fluxo_pgto)):
      self.fluxo_pgto.loc[i, 'remaining_perc'] = self.fluxo_pgto.loc[i-1, 'remaining_perc'] * (1-self.fluxo_pgto.loc[i, 'taxa'])
      self.fluxo_pgto.loc[i, 'amort_perc'] = self.fluxo_pgto.loc[i-1, 'remaining_perc'] - self.fluxo_pgto.loc[i, 'remaining_perc']

    self.fluxo_pgto.loc[1, 'amort'] = debenture.vne * self.fluxo_pgto.loc[1, 'amort_perc']
    self.fluxo_pgto.loc[0, 'sld_dev'] = debenture.vne - self.fluxo_pgto.loc[0, 'amort']
    self.fluxo_pgto.loc[1, 'sld_dev'] = self.fluxo_pgto.loc[0, 'sld_dev'] - self.fluxo_pgto.loc[1, 'amort']

    for i in range(2, len(self.fluxo_pgto)):
      self.fluxo_pgto.loc[i, 'amort'] = self.fluxo_pgto.loc[1, 'sld_dev'] * self.fluxo_pgto.loc[i, 'amort_perc']
      self.fluxo_pgto.loc[i, 'sld_dev'] = self.fluxo_pgto.loc[i-1, 'sld_dev'] - self.fluxo_pgto.loc[i, 'amort']

    for i in range(1, len(self.fluxo_pgto)):
      self.fluxo_pgto.loc[i, 'juros'] = self.fluxo_pgto.loc[i, 'sld_dev'] * self.fluxo_pgto.loc[i, 'juros_perc']

    self.fluxo_pgto['fv'] = self.fluxo_pgto['amort'] + self.fluxo_pgto['juros']
    self.fluxo_pgto['fator_desc'] = (debenture.juros_taxa+1)**(self.fluxo_pgto['dias_uteis']/252)
    self.fluxo_pgto['pv'] = self.fluxo_pgto['fv']/self.fluxo_pgto['fator_desc']

    self.pm = (self.fluxo_pgto['dias_uteis']*self.fluxo_pgto['fv']).sum()/self.fluxo_pgto['fv'].sum()
    self.duration = (self.fluxo_pgto['dias_uteis']*self.fluxo_pgto['pv']).sum()/self.fluxo_pgto['pv'].sum()

if __name__ == '__main__':
  t = Priv(codigo_ativo='CRMD11')
  print('end') 
