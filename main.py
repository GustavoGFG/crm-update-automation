from web_scraper import get_invited_leads
from excel_handler import add_leads_excel
from sharepoint import get_site_id, list_files_in_folder, download_file, upload_file, add_rows_to_excel_table, get_drive_id
from config import file_path

if __name__ == "__main__":
    leads = get_invited_leads()
    
    site_id = get_site_id()
    
    drive_id = get_drive_id(site_id)
    
    if site_id:
        
        file_id = list_files_in_folder(site_id, file_path)
        
        # add_rows_to_excel_table(file_id, "TLeads", leads, site_id, drive_id)
        download_file(file_id, site_id, file_path)
        
        add_leads_excel(file_path, leads)
        
        upload_file(file_id, site_id, file_path)
        
    else:
        print('Id do site não encontrado.')