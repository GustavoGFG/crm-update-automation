from msal import ConfidentialClientApplication
import requests
import json

from config import client_id, client_secret, tenant_id, site_url


authority=f"https://login.microsoftonline.com/{tenant_id}"

graph_api_url = "https://graph.microsoft.com/v1.0/"

scopes = ["https://graph.microsoft.com/.default"]

# Aplicação confidencial
app = ConfidentialClientApplication(
    client_id,
    authority=authority,
    client_credential=client_secret
)

def get_access_token():
    result = app.acquire_token_silent(scopes, account=None)

    if not result: 
        print("No valid token in cache, acquiring a new token...")
        result = app.acquire_token_for_client(scopes=scopes)

    if "access_token" in result:
        return result['access_token']
    else:
        print(f"Failed to acquire token: {result.get('error_description')}")
        return None

def get_site_id():
    access_token = get_access_token()
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(site_url, headers=headers)
        print(json.dumps(response.json(), indent=4))

        if response.status_code == 200:
            site_info = response.json()
            print(f"Site ID: {site_info['id']}")
            return site_info['id']
        else:
            print(f"Erro ao obter o site ID: {response.status_code}, {response.text}")
            return None
        
def list_files_in_folder(site_id, file_path):
    access_token = get_access_token()
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        # Requisição para listar o conteúdo da pasta "Gustavo"
        folder_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/root:/General/Gustavo:/children"
        response = requests.get(folder_url, headers=headers)
        # print(json.dumps(response.json(), indent=4))

        if response.status_code == 200:
            files = response.json().get('value', [])
            for item in files:
                if item['name'] == file_path:
                    return item['id']  # Retornar o ID do arquivo .xlsm
        else:
            print(f"Erro ao listar arquivos: {response.status_code}, {response.text}")
            return None
        
def download_file(file_id, site_id, file_path):
    access_token = get_access_token()
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        # Baixar o arquivo usando seu ID
        download_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{file_id}/content"
        response = requests.get(download_url, headers=headers)

        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print("Arquivo baixado com sucesso.")
        else:
            print(f"Erro ao baixar arquivo: {response.status_code}, {response.text}")

def upload_file(file_id, site_id, file_path):
    access_token = get_access_token()
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/octet-stream'  # Tipo de conteúdo do arquivo
        }
        # Fazer o upload do arquivo de volta
        upload_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drive/items/{file_id}/content"
        
        with open(file_path, 'rb') as f:
            response = requests.put(upload_url, headers=headers, data=f)

        if response.status_code == 200:
            print("Arquivo enviado com sucesso.")
        else:
            print(f"Erro ao enviar o arquivo: {response.status_code}, {response.text}")

def get_drive_id(site_id):
    access_token = get_access_token()
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        # Request to get drives under the site
        drive_url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives"
        response = requests.get(drive_url, headers=headers)

        if response.status_code == 200:
            drives = response.json().get('value', [])
            if drives:
                # Assuming you want the first drive, but you can modify it to select a specific one
                drive_id = drives[0]['id']
                print(f"Drive ID: {drive_id}")
                return drive_id
            else:
                print("No drives found under the site.")
                return None
        else:
            print(f"Error fetching drives: {response.status_code}, {response.text}")
            return None


# Função para adicionar linhas à tabela do Excel
def add_rows_to_excel_table(file_id, table_name, rows_data, site_id, drive_id):
    # Mapeamento dos dados para cada linha da tabela
    rows = [
        [
            "",               # Coluna vazia
            entry["name"],    # Nome
            entry["company"], # Empresa
            entry["campaign"],
            "",               # Coluna vazia
            "",               # Coluna vazia
            entry["data_invite"],
            entry["linkedin"],
            entry["status"],  
            "",               # Mais colunas vazias, se necessário
            "",               # Mais colunas vazias, se necessário
            "",               # Mais colunas vazias, se necessário
            "",               # Mais colunas vazias, se necessário
        ]
        for entry in rows_data  # Usando rows_data como argumento em vez de 'data'
    ]

    access_token = get_access_token()
    if access_token:
        url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/drives/{drive_id}/items/{file_id}/workbook/tables/{table_name}/rows/add"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # Dados do corpo da requisição
        data = {
            "values": rows
        }

        # Requisição POST para adicionar as linhas
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print("Linhas adicionadas com sucesso!")
        else:
            print(f"Erro ao adicionar linhas: {response.status_code} - {response.text}")
# Dados que você deseja adicionar à tabela
# Mapeamento para transformar os dados na estrutura de colunas da tabela no Excel
# Supondo que sua tabela tenha 7 colunas, com 3 delas vazias entre os dados.

