import csv
from typing import List, Dict, NoReturn


def check_error(acquired_value:float, expected_value:float) -> str:
  err = abs((acquired_value-expected_value)/expected_value)*100
  err_str = f'{err:0.3}%'
  return err_str

def save_to_csv(filedata:List[Dict], filename:str) -> NoReturn:
  """Take a list of dicts and save as an .csv with the given name"""
  keys = filedata[0].keys()
  with open('exports\\'+filename, 'w', newline='') as output_file:
      dict_writer = csv.DictWriter(output_file, keys)
      dict_writer.writeheader()
      dict_writer.writerows(filedata)
