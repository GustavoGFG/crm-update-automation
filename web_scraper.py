# web_scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
import time
from datetime import datetime, timedelta
import pytz
from config import catacliente_email, catacliente_password

def login_catacliente():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Roda o Chrome sem interface gráfica
    chrome_options.add_argument("--no-sandbox")  # Necessário para rodar no GitHub Actions
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memória compartilhada

    driver = webdriver.Chrome(options=chrome_options)  # Passa as opções headless para o driver
    # driver = webdriver.Chrome()  # Passa as opções headless para o driver

    wait = WebDriverWait(
        driver,
        30,
        poll_frequency=1,  # frequencia q vai tentar fazer algo
        ignored_exceptions=[
            NoSuchElementException,
            ElementNotVisibleException,
            ElementNotSelectableException,
        ]
    )
    driver.get("https://app.catacliente.com.br/login")
    
    # Exemplo de como fazer login no site
    username_input = driver.find_element(By.NAME, 'user')  # Ajuste os seletores conforme o site
    password_input = driver.find_element(By.NAME, 'pass')
    
    username_input.send_keys(catacliente_email)
    password_input.send_keys(catacliente_password)
    password_input.send_keys(Keys.RETURN)
    
    # Aguarda a página carregar
    time.sleep(5)
    
    return driver, wait

def close_modal(driver, wait):
    close_modal_btn = wait.until(EC.element_to_be_clickable((By.ID, 'seeLater')))
    close_modal_btn.click()
    
    time.sleep(2)

def check_campaign(driver, wait):
    driver.get("https://app.catacliente.com.br/index#mudarCampanha")
    time.sleep(5)
    
    tables = driver.find_elements(By.TAG_NAME, "table")
    
    # Access the first table
    first_table = tables[0]

    # Locate the tbody element within the table
    tbody = first_table.find_element(By.TAG_NAME, "tbody")

    # Locate all tr elements within the tbody
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        # Find all th elements within the current row
        cells = row.find_elements(By.TAG_NAME, "td")
        
        # Print or process each th element
        for index, cell in enumerate(cells):
            
            
            if (index == 3):
                if (datetime.strptime(cell.text.split(' ')[0], "%d/%m/%Y").date() == datetime.today().date()):
                    # Campanha nova
                    campaign = {
                        "description": cells[0].text,
                        "start": cells[3].text,

                    }
                    # crm_add_campaign(campaign)
                else:
                    break

def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });", element)

def order_by_date(driver, wait, el_inner_text, el_class):
    el = wait.until(EC.presence_of_element_located((By.XPATH, f'//th[contains(text(),"{el_inner_text}")]')))
    
    while el_class not in el.get_attribute('class'):
        scroll_to_element(driver, el)
        el = wait.until(EC.element_to_be_clickable((By.XPATH, f'//th[contains(text(),"{el_inner_text}")]')))
        el.click()
        time.sleep(3)

# def get_invited_leads(driver, wait):
def get_invited_leads(driver, wait, leads):
    # Brazil timezone (e.g., America/Sao_Paulo)
    brazil_tz = pytz.timezone('America/Sao_Paulo')

    # Yesterday date in Brazil timezone (without time)
    yesterday_date_brazil = (datetime.now(brazil_tz) - timedelta(days=1)).date()

    driver.get("https://app.catacliente.com.br/index#contatos?t=1")
    time.sleep(5)

    # order_by_date(driver, wait, 'Data da sincronização do aceite', 'sorting_desc')
    order_by_date(driver, wait, 'Data do convite', 'sorting_desc')

    # table = wait.until(EC.presence_of_element_located((By.ID, "example")))
    tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    rows = wait.until(lambda driver: tbody.find_elements(By.TAG_NAME, "tr"))

    for row in rows:
        lead = {
            "name": "",
            "company": "",
            "linkedin": "",
            "data_invite": "",
            "campaign": "",
            "status": "Convidado"
        }
        
        cells = row.find_elements(By.TAG_NAME, "td")
        lead["data_invite"] =  datetime.strptime(cells[7].text, "%d/%m/%Y %H:%M:%S").date()
       
        # Comparar as datas
        if yesterday_date_brazil > lead["data_invite"]:
            return leads
            
        if yesterday_date_brazil == lead["data_invite"]:
            lead["name"] = cells[1].text
            lead["company"] = cells[4].text
            lead["linkedin"] = "https://www.linkedin.com/in/" + cells[2].text
            lead["data_invite"] = cells[7].text.split(" ")[0]
            lead["campaign"] = "AD.GM&E.027" if cells[5].text == "Campanha 2 - Papel e Celulose" else "AD.GM&E.001" if cells[5].text == "P001 | CADENCIA AD001 | 4 MENSAGENS" else cells[5].text

            # print(f'nome: {lead["name"]} | empresa: {lead["company"]} | campanha: {lead["campaign"]} | perfil: {lead["linkedin"]} | inicio: {lead["data_invite"]}')

            leads.append(lead)


def update_leads(driver, wait, leads):
    # Brazil timezone (e.g., America/Sao_Paulo)
    brazil_tz = pytz.timezone('America/Sao_Paulo')

    # Yesterday date in Brazil timezone (without time)
    yesterday_date_brazil = (datetime.now(brazil_tz) - timedelta(days=1)).date()

    driver.get("https://app.catacliente.com.br/index#contatos?t=2")
    time.sleep(5)

    # order_by_date(driver, wait, 'Data da sincronização do aceite', 'sorting_desc')
    order_by_date(driver, wait, 'Data da sincronização do aceite', 'sorting_desc')

    tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    rows = wait.until(lambda driver: tbody.find_elements(By.TAG_NAME, "tr"))

    for row in rows:
        lead = {
            "name": "",
            "company": "",
            "linkedin": "",
            "data_invite": "",
            "campaign": "",
            "status": "Conectado"
        }
        
        cells = row.find_elements(By.TAG_NAME, "td")
        data_accept = datetime.strptime(cells[14].text, "%d/%m/%Y %H:%M:%S").date()

        if  yesterday_date_brazil > data_accept:
            return leads

        if yesterday_date_brazil == lead["data_invite"]:

            lead["name"] = cells[1].text
            lead["campaign"] = "AD.GM&E.027" if cells[9].text == "Campanha 2 - Papel e Celulose" else "AD.GM&E.001" if cells[9].text == "P001 | CADENCIA AD001 | 4 MENSAGENS" else cells[9].text
            lead["linkedin"] = "https://www.linkedin.com/in/" + cells[2].text
            lead["data_invite"] = cells[13].text.split(" ")[0]
            lead["company"] = cells[5].text

            # print(f'nome: {lead["name"]} | empresa: {lead["company"]} | campanha: {lead["campaign"]} | perfil: {lead["linkedin"]} | inicio: {lead["data_invite"]} | data_aceite: {data_accept}')

            leads.append(lead)
       


def fechar_driver(driver):
    driver.quit()
