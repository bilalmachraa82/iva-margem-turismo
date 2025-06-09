import json
import pandas as pd
import os
from datetime import datetime

def carregar_json(caminho_arquivo):
    """Carrega um arquivo JSON e retorna seu conteúdo."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

def salvar_json(dados, caminho_arquivo):
    """Salva dados em um arquivo JSON."""
    try:
        with open(caminho_arquivo, 'w', encoding='utf-8') as file:
            json.dump(dados, file, indent=2, ensure_ascii=False)
        print(f"Arquivo salvo com sucesso: {caminho_arquivo}")
        return True
    except Exception as e:
        print(f"Erro ao salvar o arquivo {caminho_arquivo}: {e}")
        return False

def associar_custos_a_vendas():
    """Associa custos às vendas e atualiza o arquivo de resumo."""
    diretorio = os.path.dirname(os.path.abspath(__file__))
    
    # Carregar os dados
    vendas_path = os.path.join(diretorio, 'mockup_vendas.json')
    custos_path = os.path.join(diretorio, 'mockup_custos.json')
    resumo_path = os.path.join(diretorio, 'Resumo.json')
    workbook_path = os.path.join(diretorio, 'workbook_all_sheets.json')
    
    vendas = carregar_json(vendas_path)
    custos = carregar_json(custos_path)
    resumo = carregar_json(resumo_path)
    workbook = carregar_json(workbook_path)
    
    if not all([vendas, custos, resumo, workbook]):
        print("Falha ao carregar um ou mais arquivos JSON.")
        return
    
    # Converter para DataFrames
    df_vendas = pd.DataFrame(vendas)
    df_custos = pd.DataFrame(custos)
    df_resumo = pd.DataFrame(resumo)
    
    # Método 1: Associar custos diretamente quando o SaleInvoice não é nulo
    print("\n===== MÉTODO 1: ASSOCIAÇÃO DIRETA DE CUSTOS =====")
    
    # Criar um dicionário para mapear faturas de venda aos seus custos
    custos_por_fatura = {}
    
    # Processar custos que já têm uma fatura de venda associada
    for custo in custos:
        if custo['SaleInvoice']:
            # Alguns registros podem ter múltiplas faturas separadas por vírgula
            for fatura in custo['SaleInvoice'].split(','):
                fatura = fatura.strip()
                if fatura not in custos_por_fatura:
                    custos_por_fatura[fatura] = 0
                custos_por_fatura[fatura] += custo['Cost']
    
    # Verificar quantas faturas foram associadas diretamente
    print(f"Faturas com custos associados diretamente: {len(custos_por_fatura)}")
    
    # Método 2: Distribuição proporcional dos custos restantes
    print("\n===== MÉTODO 2: DISTRIBUIÇÃO PROPORCIONAL DOS CUSTOS RESTANTES =====")
    
    # Calcular o total de vendas e custos
    total_vendas = sum(venda['Total_PVP'] for venda in vendas)
    total_custos = sum(custo['Cost'] for custo in custos)
    
    # Calcular o total de custos já associados diretamente
    total_custos_associados = sum(custos_por_fatura.values())
    
    # Calcular o total de custos não associados
    custos_nao_associados = total_custos - total_custos_associados
    
    print(f"Total de vendas: {total_vendas:.2f}")
    print(f"Total de custos: {total_custos:.2f}")
    print(f"Total de custos já associados: {total_custos_associados:.2f}")
    print(f"Total de custos não associados: {custos_nao_associados:.2f}")
    
    # Calcular o fator de distribuição para os custos não associados
    if total_vendas != 0:
        fator_distribuicao = custos_nao_associados / total_vendas
        print(f"Fator de distribuição para custos não associados: {fator_distribuicao:.4f}")
    else:
        fator_distribuicao = 0
        print("Aviso: Total de vendas é zero, não é possível calcular o fator de distribuição.")
    
    # Atualizar o resumo com os custos associados
    resumo_atualizado = []
    
    for item in resumo:
        fatura = item['Invoice_No']
        venda = item['Total_PVP']
        
        # Obter o custo associado diretamente, se existir
        custo_direto = custos_por_fatura.get(fatura, 0)
        
        # Calcular o custo proporcional para os custos não associados
        custo_proporcional = venda * fator_distribuicao
        
        # Custo total é a soma do custo direto e do custo proporcional
        custo_total = custo_direto + custo_proporcional
        
        # Atualizar o item do resumo
        item_atualizado = item.copy()
        item_atualizado['Total_Cost'] = custo_total
        item_atualizado['Margem_Bruta'] = venda - custo_total
        
        # Recalcular a margem líquida (margem bruta - IVA)
        if 'IVA_Due' in item:
            item_atualizado['Margem_Liquida'] = item_atualizado['Margem_Bruta'] - item['IVA_Due']
        
        resumo_atualizado.append(item_atualizado)
    
    # Atualizar o workbook com os dados do resumo atualizado
    if 'Resumo' in workbook:
        workbook['Resumo'] = resumo_atualizado
    
    # Salvar os arquivos atualizados
    print("\n===== SALVANDO ARQUIVOS ATUALIZADOS =====")
    
    # Salvar o resumo atualizado
    resumo_atualizado_path = os.path.join(diretorio, 'Resumo_atualizado.json')
    salvar_json(resumo_atualizado, resumo_atualizado_path)
    
    # Salvar o workbook atualizado
    workbook_atualizado_path = os.path.join(diretorio, 'workbook_all_sheets_atualizado.json')
    salvar_json(workbook, workbook_atualizado_path)
    
    # Mostrar alguns exemplos do resumo atualizado
    print("\n===== EXEMPLOS DO RESUMO ATUALIZADO =====")
    for i, item in enumerate(resumo_atualizado[:5]):
        print(f"Fatura: {item['Invoice_No']}")
        print(f"  Venda: {item['Total_PVP']:.2f}")
        print(f"  Custo: {item['Total_Cost']:.2f}")
        print(f"  Margem Bruta: {item['Margem_Bruta']:.2f}")
        print(f"  Margem Bruta %: {(item['Margem_Bruta'] / item['Total_PVP'] * 100) if item['Total_PVP'] != 0 else 0:.2f}%")
        print(f"  Margem Líquida: {item['Margem_Liquida']:.2f}")
        print(f"  Margem Líquida %: {(item['Margem_Liquida'] / item['Total_PVP'] * 100) if item['Total_PVP'] != 0 else 0:.2f}%")
        print()
    
    # Calcular as margens totais
    total_venda = sum(item['Total_PVP'] for item in resumo_atualizado)
    total_custo = sum(item['Total_Cost'] for item in resumo_atualizado)
    total_margem_bruta = sum(item['Margem_Bruta'] for item in resumo_atualizado)
    total_margem_liquida = sum(item['Margem_Liquida'] for item in resumo_atualizado)
    
    print("===== TOTAIS =====")
    print(f"Total de Vendas: {total_venda:.2f}")
    print(f"Total de Custos: {total_custo:.2f}")
    print(f"Total de Margem Bruta: {total_margem_bruta:.2f}")
    print(f"Percentual de Margem Bruta: {(total_margem_bruta / total_venda * 100) if total_venda != 0 else 0:.2f}%")
    print(f"Total de Margem Líquida: {total_margem_liquida:.2f}")
    print(f"Percentual de Margem Líquida: {(total_margem_liquida / total_venda * 100) if total_venda != 0 else 0:.2f}%")

if __name__ == "__main__":
    associar_custos_a_vendas()
