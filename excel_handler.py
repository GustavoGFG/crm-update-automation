from config import excel_password
import xlwings as xw

def add_leads_excel(file_path, leads):
    
    # Abre o arquivo Excel
    wb = xw.Book(file_path)
    
    try:
        # Seleciona a planilha 'Leads'
        sheet = wb.sheets['Leads']
        
        # Desbloqueia a planilha
        sheet.api.Unprotect(Password=excel_password)

        # Seleciona a tabela pelo nome
        table_range = sheet.tables["TLeads"].range

        # Encontra a última linha da tabela
        last_row = table_range.last_cell.row
        last_id = sheet.range(f'B{last_row}').value

        # Define uma macro
        add_row = wb.macro("AddRow_Leads")

        for data_row in leads:
            # Insere uma nova linha ao final da tabela
            add_row()
            next_row = last_row + 1

            # Preenche as colunas com os valores do dicionário
            sheet.range(f'B{next_row}').value = last_id + 1
            sheet.range(f'C{next_row}').value = data_row["name"]
            sheet.range(f'D{next_row}').value = data_row["company"]
            sheet.range(f'E{next_row}').value = data_row["campaign"]
            sheet.range(f'H{next_row}').value = data_row["data_invite"]
            sheet.range(f'I{next_row}').value = data_row["linkedin"]
            sheet.range(f'J{next_row}').value = data_row["status"]

            # Atualiza o ID e a última linha
            last_id += 1
            last_row += 1

        # Protege novamente a planilha
        sheet.api.Protect(Password=excel_password)
        
        # Salva as alterações
        wb.save()

    finally:
        # Fecha o arquivo
        wb.close()
