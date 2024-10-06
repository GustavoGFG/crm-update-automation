# web_scraper.py
import logging
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

# Configuração do logger para armazenar logs em um arquivo
logging.basicConfig(filename='scrapper.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def login_catacliente():
    """
    Inicializa o driver e realiza o login na plataforma Catacliente
    """
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Roda o Chrome sem interface gráfica
        chrome_options.add_argument("--no-sandbox")  # Necessário para rodar no GitHub Actions
        chrome_options.add_argument("--disable-dev-shm-usage")  # Evitar problemas de memória compartilhada

        driver = webdriver.Chrome(options=chrome_options)  # Inicializa o Driver com as opções especificadas
        # driver = webdriver.Chrome()  # Inicializa o Driver com as opções especificadas

        # Define um tempo de espera, uma frequência e exceções de erros que deve ignorar no tempo de espera
        wait = WebDriverWait(driver, 30, poll_frequency=1, ignored_exceptions=[
                NoSuchElementException,
                ElementNotVisibleException,
                ElementNotSelectableException,
            ]
        )

        driver.get("https://app.catacliente.com.br/login") # Acessa a página de login
        logging.info('Página de login acessada com sucesso.')

        username_input = driver.find_element(By.NAME, 'user') # Campo do email do usuário
        password_input = driver.find_element(By.NAME, 'pass') # Campo da senha do usuário 
        
        username_input.send_keys(catacliente_email)
        password_input.send_keys(catacliente_password)
        password_input.send_keys(Keys.RETURN)
        logging.info('Login realizado com sucesso.')
        
        return driver, wait
    except TimeoutException as e:
        logging.error(f'Tempo limite atingido durante o login: {e}', exc_info=True)
        raise
    except Exception as e:
        logging.error(f'Erro inesperado no login: {e}', exc_info=True)
        raise

def close_modal(driver, wait):
    """
    Fecha o modal de dicas do catacliente
    """
    try:
        close_modal_btn = wait.until(EC.element_to_be_clickable((By.ID, 'seeLater')))
        close_modal_btn.click()
        wait.until(EC.invisibility_of_element_located((By.ID, "seeLater")))
        logging.info('Modal fechado com sucesso.')
    except TimeoutException:
        logging.warning('Modal não apareceu ou já estava fechado.')
    except Exception as e:
        logging.error(f'Erro ao fechar o modal: {e}', exc_info=True)

def check_campaign(driver, wait):
    """
    Verifica campanhas que começaram ontem
    """
    try:
        driver.get("https://app.catacliente.com.br/index#mudarCampanha")
        # time.sleep(5)
        
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
                        campaign = {
                            "description": cells[0].text,
                            "start": cells[3].text,
                        }
                        
                    else:
                        break
        logging.info('Campanhas verificadas com sucesso.')
    except Exception as e:
        logging.error(f'Erro ao verificar campanhas: {e}', exc_info=True)

def scroll_to_element(driver, element):
    """
    Realiza o scroll até o elemento da página
    """
    try:
        driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' });", element)
        logging.info('Scroll realizado até o elemento com sucesso.')
    except Exception as e:
        logging.error(f'Erro ao fazer scroll para o elemento: {e}', exc_info=True)

def order_by_date(driver, wait, el_inner_text, el_class):
    """
    Ordena a tabela por data clicando no cabeçalho correspondente
    """
    try:
        el = wait.until(EC.presence_of_element_located((By.XPATH, f'//th[contains(text(),"{el_inner_text}")]')))
        # loading_table = (By.CLASS_NAME, 'dataTables_processing dts_loading')
        
        while el_class not in el.get_attribute('class'):
            scroll_to_element(driver, el)
            el = wait.until(EC.element_to_be_clickable((By.XPATH, f'//th[contains(text(),"{el_inner_text}")]')))
            el.click()
            logging.info('Tabela está carregando...')
            time.sleep(3)
            logging.info('Tabela carregada com sucesso.')
        logging.info(f'Tabela ordenada por {el_inner_text} em ordem {el.get_attribute('class')}.')
    except Exception as e:
        logging.error(f'Erro ao ordenar tabela por {el_inner_text}: {e}', exc_info=True)


def get_invited_leads(driver, wait, leads):
    """
    Coleta leads que forma convidados no dia anterior.
    """
    try:
        brazil_tz = pytz.timezone('America/Sao_Paulo')
        yesterday_date_brazil = (datetime.now(brazil_tz) - timedelta(days=1)).date()

        driver.get("https://app.catacliente.com.br/index#contatos?t=1")
        time.sleep(5)
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        rows = wait.until(lambda driver: tbody.find_elements(By.TAG_NAME, "tr"))
        
        order_by_date(driver, wait, 'Data do convite', 'sorting_desc')
        
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
                logging.info(f'{len(leads)} leads convidados coletados.')
                return leads
                
            if yesterday_date_brazil <= lead["data_invite"]:
                lead["name"] = cells[1].text
                lead["company"] = cells[4].text
                lead["linkedin"] = "https://www.linkedin.com/in/" + cells[2].text
                lead["data_invite"] = cells[7].text.split(" ")[0]
                lead["campaign"] = "AD.GM&E.027" if cells[5].text == "Campanha 2 - Papel e Celulose" else "AD.GM&E.001" if cells[5].text == "P001 | CADENCIA AD001 | 4 MENSAGENS" else cells[5].text

                # print(f'nome: {lead["name"]} | empresa: {lead["company"]} | campanha: {lead["campaign"]} | perfil: {lead["linkedin"]} | inicio: {lead["data_invite"]}')

                leads.append(lead)
    except Exception as e:
        logging.error(f'Erro ao coletar leads convidados: {e}', exc_info=True)


def update_leads(driver, wait, leads):
    """
    Coleta os leads que aceitaram a conexão ontem.
    """
    try:
        old_len = len(leads)
        brazil_tz = pytz.timezone('America/Sao_Paulo')
        yesterday_date_brazil = (datetime.now(brazil_tz) - timedelta(days=1)).date()

        driver.get("https://app.catacliente.com.br/index#contatos?t=2")
        time.sleep(5)
        tbody = wait.until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        rows = wait.until(lambda driver: tbody.find_elements(By.TAG_NAME, "tr"))

        order_by_date(driver, wait, 'Data da sincronização do aceite', 'sorting_desc')

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
                logging.info(f'{len(leads) - old_len} leads conectados coletados.')
                return leads

            # if yesterday_date_brazil == data_accept:
            if yesterday_date_brazil <= data_accept:

                lead["name"] = cells[1].text
                lead["campaign"] = "AD.GM&E.027" if cells[9].text == "Campanha 2 - Papel e Celulose" else "AD.GM&E.001" if cells[9].text == "P001 | CADENCIA AD001 | 4 MENSAGENS" else cells[9].text
                lead["linkedin"] = "https://www.linkedin.com/in/" + cells[2].text
                lead["data_invite"] = cells[13].text.split(" ")[0]
                lead["company"] = cells[5].text

                # print(f'nome: {lead["name"]} | empresa: {lead["company"]} | campanha: {lead["campaign"]} | perfil: {lead["linkedin"]} | inicio: {lead["data_invite"]} | data_aceite: {data_accept}')

                leads.append(lead)
    except Exception as e:
        logging.error(f'Erro ao atualizar leads: {e}', exc_info=True)  


def fechar_driver(driver):
    """
    Encerra o driver do navegador.
    """
    if driver:
        driver.quit()
        logging.info('Driver fechado com sucesso.')
