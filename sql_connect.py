from mysql.connector import connect, Error
from constants import HOST, USER, PASSWORD, DATABASE
from retry import retry

@retry(delay=1, tries=4, jitter=2)
def send_to_sql(sql_query:str):
  try:
      with connect(
          host=HOST,
          user=USER,
          password=PASSWORD,
          database=DATABASE,
      ) as connection:
          with connection.cursor() as cursor:
              cursor.execute(sql_query)
              connection.commit()
  except Error as e:
      print(e)

@retry(delay=1, tries=4, jitter=2)
def select_sql(sql_query:str):
  try:
      with connect(
          host=HOST,
          user=USER,
          password=PASSWORD,
          database=DATABASE,
      ) as connection:
          with connection.cursor() as cursor:
              cursor.execute(sql_query)
              return cursor.fetchall()
  except Error as e:
      print(e)
