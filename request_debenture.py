from playwright.sync_api import sync_playwright 
import csv


def save_to_csv(to_csv, filename='deb.csv'):
    keys = to_csv[0].keys()

    with open(f'exports/agenda_debentures/{filename}', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(to_csv)


def list_debentures():
    list_url = "https://data.anbima.com.br/debentures?page=1&size=999"
    with sync_playwright() as p: 
        def handle_response(response): 
        # the endpoint we are insterested in 
            if ("/web-bff/v1/debentures?" in response.url):
                list_data = response.json()["content"]
                save_to_csv(list_data, f'{list}.csv')

        browser = p.chromium.launch()
        page = browser.new_page() 

        page.on("response", handle_response) 
        # really long timeout since it gets stuck sometimes 
        page.goto(list_url, wait_until="networkidle") 
        page.wait_for_timeout(10000)

        page.context.close()
        browser.close()


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
        # really long timeout since it gets stuck sometimes 
        page.goto(agenda_url, wait_until="networkidle") 
        page.wait_for_timeout(10000)

        page.context.close()
        browser.close()
