#!/usr/bin/env python3
"""
Script adaptado para WSL - análise básica do ficheiro Excel sem dependências externas
"""
import os
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

def analyze_excel_wsl():
    """Análise do Excel usando apenas biblioteca padrão Python"""
    
    file_path = "Modelo_IVA_Margem_Agencias_Viagens_v3.xlsm.xlsx"
    
    print("🔍 ANÁLISE DO FICHEIRO EXCEL MODELO (WSL)")
    print("=" * 50)
    
    if not os.path.exists(file_path):
        print(f"❌ Ficheiro não encontrado: {file_path}")
        print("Ficheiros Excel na pasta atual:")
        for f in os.listdir('.'):
            if f.endswith(('.xlsx', '.xlsm', '.xls')):
                size = os.path.getsize(f) / 1024  # KB
                print(f"  📄 {f} ({size:.1f} KB)")
        return
    
    print(f"📄 Ficheiro encontrado: {file_path}")
    file_size = os.path.getsize(file_path) / 1024 / 1024  # MB
    print(f"📊 Tamanho: {file_size:.2f} MB")
    
    try:
        # Excel .xlsx é um ficheiro ZIP com XML dentro
        with zipfile.ZipFile(file_path, 'r') as excel_zip:
            print(f"📋 Conteúdo do ficheiro Excel:")
            
            # Listar ficheiros dentro do Excel
            file_list = excel_zip.namelist()
            
            # Procurar estrutura típica do Excel
            sheets_found = []
            for file_name in file_list:
                if file_name.startswith('xl/worksheets/sheet'):
                    sheets_found.append(file_name)
                    
            print(f"🗂️ Folhas encontradas: {len(sheets_found)}")
            
            # Tentar ler workbook.xml para nomes das folhas
            try:
                workbook_xml = excel_zip.read('xl/workbook.xml')
                root = ET.fromstring(workbook_xml)
                
                # Namespace do Excel
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                
                sheets = root.findall('.//main:sheet', ns)
                print(f"📝 Nomes das folhas:")
                for i, sheet in enumerate(sheets):
                    name = sheet.get('name', f'Sheet{i+1}')
                    sheet_id = sheet.get('sheetId', 'N/A')
                    print(f"  {i+1}. {name} (ID: {sheet_id})")
                    
            except Exception as e:
                print(f"⚠️ Não foi possível ler nomes das folhas: {str(e)}")
            
            # Tentar analisar a primeira folha
            if sheets_found:
                try:
                    first_sheet = sheets_found[0]
                    print(f"\n🔍 Análise da primeira folha: {first_sheet}")
                    
                    sheet_xml = excel_zip.read(first_sheet)
                    sheet_root = ET.fromstring(sheet_xml)
                    
                    # Namespace do Excel
                    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    
                    # Encontrar todas as células com dados
                    cells = sheet_root.findall('.//main:c', ns)
                    print(f"📊 Total de células com dados: {len(cells)}")
                    
                    # Analisar algumas células para encontrar padrões
                    sample_data = []
                    for i, cell in enumerate(cells[:20]):  # Primeiras 20 células
                        cell_ref = cell.get('r', f'Cell{i}')
                        cell_type = cell.get('t', 'n')  # n=number, s=string, etc
                        
                        value_elem = cell.find('main:v', ns)
                        if value_elem is not None:
                            value = value_elem.text
                            sample_data.append((cell_ref, cell_type, value))
                    
                    if sample_data:
                        print(f"📋 Amostra de dados (primeiras {len(sample_data)} células):")
                        for cell_ref, cell_type, value in sample_data[:10]:
                            type_desc = {'n': 'Número', 's': 'Texto', 'b': 'Boolean'}.get(cell_type, cell_type)
                            print(f"  {cell_ref}: {value} ({type_desc})")
                    
                except Exception as e:
                    print(f"⚠️ Erro ao analisar folha: {str(e)}")
            
            # Procurar por strings compartilhadas (texto do Excel)
            try:
                if 'xl/sharedStrings.xml' in file_list:
                    strings_xml = excel_zip.read('xl/sharedStrings.xml')
                    strings_root = ET.fromstring(strings_xml)
                    
                    ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    string_items = strings_root.findall('.//main:si', ns)
                    
                    print(f"\n📝 Strings encontradas no Excel ({len(string_items)} total):")
                    
                    # Procurar palavras-chave relacionadas com turismo/contabilidade
                    keywords = ['venda', 'custo', 'fatura', 'cliente', 'fornecedor', 'hotel', 'voo', 'viagem', 'margem', 'iva']
                    found_keywords = []
                    
                    for item in string_items[:50]:  # Primeiras 50 strings
                        text_elem = item.find('.//main:t', ns)
                        if text_elem is not None and text_elem.text:
                            text = text_elem.text.lower()
                            for keyword in keywords:
                                if keyword in text:
                                    found_keywords.append((keyword, text_elem.text))
                    
                    if found_keywords:
                        print("🎯 Palavras-chave relevantes encontradas:")
                        for keyword, original_text in found_keywords[:10]:
                            print(f"  '{keyword}' em: {original_text}")
                    else:
                        # Mostrar algumas strings aleatórias
                        print("📄 Algumas strings encontradas:")
                        for i, item in enumerate(string_items[:5]):
                            text_elem = item.find('.//main:t', ns)
                            if text_elem is not None and text_elem.text:
                                print(f"  {i+1}. {text_elem.text}")
                                
            except Exception as e:
                print(f"⚠️ Erro ao ler strings: {str(e)}")
                
    except zipfile.BadZipFile:
        print("❌ Ficheiro não é um Excel válido (.xlsx/.xlsm)")
    except Exception as e:
        print(f"❌ Erro ao analisar ficheiro: {str(e)}")
    
    print(f"\n💡 RECOMENDAÇÕES BASEADAS NA ANÁLISE:")
    print("1. Para análise completa, instalar: pip3 install openpyxl pandas")
    print("2. Verificar se dados seguem padrões de regime de margem")
    print("3. Validar margens entre 5-25% para sector turismo")
    print("4. Confirmar que vendas NÃO têm IVA separado")

if __name__ == "__main__":
    analyze_excel_wsl()