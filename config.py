from dotenv import load_dotenv
import os

load_dotenv()

client_id = os.getenv("AZURE_CLIENT_ID")
client_secret = os.getenv("AZURE_CLIENT_SECRET")
tenant_id = os.getenv("AZURE_TENANT_ID")

file_id = os.getenv("AZURE_FILE_ID")
file_path = os.getenv("AZURE_FILE_PATH")

site_url = os.getenv("AZURE_SITE_URL")

excel_password = os.getenv("EXCEL_FILE_PASSWORD")

catacliente_email = os.getenv("CATACLIENTE_EMAIL")
catacliente_password = os.getenv("CATACLIENTE_PASSWORD")