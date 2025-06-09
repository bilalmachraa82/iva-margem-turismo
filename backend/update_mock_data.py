#!/usr/bin/env python3
"""
Script para atualizar dados mock no main.py com todos os dados do Excel
Substitui os 20 custos atuais pelos 157 custos completos
"""
import json
import re

def update_mock_data():
    print("🔄 ATUALIZANDO DADOS MOCK COM EXCEL COMPLETO...")
    
    # Ler dados completos do Excel
    with open('../excel_mock_converted.json', 'r', encoding='utf-8') as f:
        excel_data = json.load(f)
    
    print(f"📊 Dados Excel: {len(excel_data['sales'])} vendas + {len(excel_data['costs'])} custos")
    
    # Ler main.py atual
    with open('app/main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Formatar costs como string Python
    costs_lines = []
    for cost in excel_data['costs']:
        cost_str = json.dumps(cost, ensure_ascii=False, separators=(',', ': '))
        costs_lines.append(f"            {cost_str},")
    
    costs_section = '\n'.join(costs_lines)
    
    # Encontrar e substituir seção de custos
    pattern = r'(\s*"costs": \[)[^]]*(\])'
    replacement = f'\\1\n{costs_section}\n        \\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Verificar se a substituição funcionou
    if '"costs": [' in new_content and len(costs_lines) > 20:
        # Fazer backup
        with open('app/main.py.backup', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Escrever novo conteúdo
        with open('app/main.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ ATUALIZAÇÃO COMPLETA!")
        print(f"📁 Backup criado: app/main.py.backup")
        print(f"📊 Agora o site terá {len(excel_data['sales'])} vendas + {len(excel_data['costs'])} custos")
        print(f"🔢 Total: {len(excel_data['sales']) + len(excel_data['costs'])} documentos")
        
        # Verificar se foi tudo substituído corretamente
        with open('app/main.py', 'r', encoding='utf-8') as f:
            new_file_content = f.read()
        
        cost_count = new_file_content.count('"id": "c')
        print(f"🔍 Verificação: {cost_count} custos encontrados no arquivo atualizado")
        
        if cost_count == len(excel_data['costs']):
            print("✅ VERIFICAÇÃO PASSOU: Todos os custos foram atualizados!")
        else:
            print("⚠️ VERIFICAÇÃO FALHOU: Número de custos não confere")
            
    else:
        print("❌ ERRO: Não foi possível fazer a substituição")

if __name__ == "__main__":
    update_mock_data()