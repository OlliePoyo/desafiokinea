from playwright.sync_api import sync_playwright 
import csv
import pandas as pd

def save_to_csv(to_csv, filename='deb.csv', page=1):
    keys = to_csv[0].keys()
    full_filename = f'exports/agenda_debentures/{filename}'
    if page == 0:
        with open(full_filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(to_csv)
    else:
        with open(full_filename, 'a', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writerows(to_csv)


def list_debentures():
    page_num = 1
    with sync_playwright() as p: 
        def handle_response(response):
        # the endpoint we are insterested in
            if ("/web-bff/v1/debentures?" in response.url):
                page_n = int(response.url.partition('page=')[2].partition('&size=')[0])
                list_data = response.json()["content"]
                save_to_csv(list_data, 'list.csv', page_n)

        browser = p.chromium.launch()

        try:
            while True:
                list_url = f"https://data.anbima.com.br/debentures?page={page_num}&size=100"
                
                page = browser.new_page() 

                page.on("response", handle_response)

                page.goto(list_url, wait_until="networkidle")
                page.wait_for_timeout(10000)
                page_num += 1
        except:
            None

        page.context.close()
        browser.close()
    return pd.read_csv(f'exports/agenda_debentures/list.csv')

def agenda_debenture(debenture:str):
    agenda_url = f"https://data.anbima.com.br/debentures/{debenture}/agenda?page=1&size=999"
    with sync_playwright() as p: 
        def handle_response(response):
        # the endpoint we are insterested in
            if ("/web-bff/v1/debentures/" in response.url) and ("/agenda?" in response.url):
                agenda_data = response.json()["content"]
                save_to_csv(agenda_data, f'{debenture}.csv')

        browser = p.chromium.launch()
        page = browser.new_page()

        page.on("response", handle_response)
        
        page.goto(agenda_url, wait_until="networkidle")
        page.wait_for_timeout(10000)

        page.context.close()
        browser.close()
    return pd.read_csv(f'exports/agenda_debentures/{debenture}.csv')

list_debentures()