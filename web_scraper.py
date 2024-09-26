# web_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import *
import time
from datetime import datetime
from config import catacliente_email, catacliente_password

def login_catacliente():
    driver = webdriver.Chrome()  # Você pode configurar seu próprio WebDriver
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
                    print('Campanha nova')
                    campaign = {
                        "description": cells[0].text,
                        "start": cells[3].text,

                    }
                    # crm_add_campaign(campaign)
                else:
                    print('Nenhuma campanha nova')
                    break

# def get_invited_leads(driver, wait):
def get_invited_leads():
    [driver, wait] = login_catacliente()
    close_modal(driver, wait)

    driver.get("https://app.catacliente.com.br/index#contatos?t=1")
    time.sleep(5)

    # table = wait.until(EC.presence_of_element_located((By.ID, "example")))
    tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    rows = wait.until(lambda driver: tbody.find_elements(By.TAG_NAME, "tr"))

    leads = []

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
        lead["name"] = cells[1].text
        lead["company"] = cells[4].text
        lead["linkedin"] = "https://www.linkedin.com/in/" + cells[2].text
        lead["data_invite"] = cells[7].text.split(" ")[0]
        lead["campaign"] = "AD.GM&E.027" if cells[5].text == "Campanha 2 - Papel e Celulose" else "AD.GM&E.001"

        print(f'nome: {lead["name"]} | empresa: {lead["company"]} | campanha: {lead["campaign"]} | perfil: {lead["linkedin"]} | inicio: {lead["data_invite"]}')

        leads.append(lead)

        fechar = input("Fechar programa? ")
        print(len(leads))
        if fechar == 's':
            return leads
            driver.quit()

def update_leads(driver, wait):
    driver.get("https://app.catacliente.com.br/index#contatos?t=2")
    time.sleep(5)

    print('0')
    table = wait.until(EC.presence_of_element_located((By.ID, "example")))
    print('1')
    tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
    print('2')

    rows = wait.until(lambda driver: tbody.find_elements(By.TAG_NAME, "tr"))
    print('3')

    for row in rows:
        lead = {
            "name": "",
            "company": "",
            "linkedin": "",
            "data_invite": "",
            "campaign": "",
            "data_accept": "",
        }
        
        cells = row.find_elements(By.TAG_NAME, "td")
        lead["name"] = cells[1].text
        lead["company"] = "AD.GM&E.027" if cells[6].text == "Camapanha 2 - Papel e Celulose" else "AD.GM&E.001"
        lead["linkedin"] = "https://www.linkedin.com/in/" + cells[2].text
        lead["data_invite"] = cells[13].text.split(" ")[0]
        lead["campaign"] = cells[9].text
        lead["data_accept"] = cells[14].text.split(" ")[0]

        print(f'nome: {lead["name"]} | empresa: {lead["company"]} | campanha: {lead["campaign"]} | perfil: {lead["linkedin"]} | inicio: {lead["data_invite"]} | data_aceite: {lead["data_accept"]}')

        fechar = input("Fechar programa? ")
        if fechar == 's':
            driver.quit()


def fechar_driver(driver):
    driver.quit()
