import json
import pandas as pd
from datetime import datetime
import os

def carregar_json(caminho_arquivo):
    """Carrega um arquivo JSON e retorna seu conteúdo."""
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Erro ao carregar o arquivo {caminho_arquivo}: {e}")
        return None

def converter_timestamp_para_data(timestamp):
    """Converte um timestamp em milissegundos para uma data legível."""
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')

def analisar_dados():
    """Analisa os dados dos arquivos JSON e verifica inconsistências."""
    # Carregar os dados
    diretorio = os.path.dirname(os.path.abspath(__file__))
    
    vendas = carregar_json(os.path.join(diretorio, 'mockup_vendas.json'))
    custos = carregar_json(os.path.join(diretorio, 'mockup_custos.json'))
    resumo = carregar_json(os.path.join(diretorio, 'Resumo.json'))
    workbook = carregar_json(os.path.join(diretorio, 'workbook_all_sheets.json'))
    
    if not all([vendas, custos, resumo, workbook]):
        print("Falha ao carregar um ou mais arquivos JSON.")
        return
    
    # Converter para DataFrames para facilitar a análise
    df_vendas = pd.DataFrame(vendas)
    df_custos = pd.DataFrame(custos)
    df_resumo = pd.DataFrame(resumo)
    
    # Converter timestamps para datas legíveis
    if 'Date' in df_vendas.columns:
        df_vendas['Data'] = df_vendas['Date'].apply(converter_timestamp_para_data)
    if 'Date' in df_custos.columns:
        df_custos['Data'] = df_custos['Date'].apply(converter_timestamp_para_data)
    
    # Análise básica dos dados
    print("\n===== ANÁLISE DOS DADOS =====")
    print(f"Total de registros de vendas: {len(df_vendas)}")
    print(f"Total de registros de custos: {len(df_custos)}")
    print(f"Total de registros de resumo: {len(df_resumo)}")
    
    # Verificar valores totais
    total_vendas = df_vendas['Total_PVP'].sum() if 'Total_PVP' in df_vendas.columns else 0
    total_custos = df_custos['Cost'].sum() if 'Cost' in df_custos.columns else 0
    
    print(f"\nValor total de vendas: {total_vendas:.2f}")
    print(f"Valor total de custos: {total_custos:.2f}")
    
    # Verificar se há valores negativos
    vendas_negativas = df_vendas[df_vendas['Total_PVP'] < 0] if 'Total_PVP' in df_vendas.columns else pd.DataFrame()
    custos_negativos = df_custos[df_custos['Cost'] < 0] if 'Cost' in df_custos.columns else pd.DataFrame()
    
    print(f"\nVendas com valores negativos: {len(vendas_negativas)}")
    if not vendas_negativas.empty:
        print(vendas_negativas[['Invoice_No', 'Data', 'Total_PVP', 'Doc_Type']].to_string(index=False))
    
    print(f"\nCustos com valores negativos: {len(custos_negativos)}")
    if not custos_negativos.empty:
        print(custos_negativos[['SupplierInvoice', 'Data', 'Cost', 'Doc_Type']].to_string(index=False))
    
    # Verificar o problema dos custos nulos no resumo
    custos_nulos = df_resumo[df_resumo['Total_Cost'].isna()] if 'Total_Cost' in df_resumo.columns else pd.DataFrame()
    print(f"\nRegistros de resumo com custos nulos: {len(custos_nulos)} de {len(df_resumo)}")
    
    # Verificar a relação entre vendas e custos
    print("\n===== ANÁLISE DA RELAÇÃO ENTRE VENDAS E CUSTOS =====")
    
    # Verificar se há faturas de venda sem custos associados
    faturas_venda = set(df_vendas['Invoice_No'].tolist()) if 'Invoice_No' in df_vendas.columns else set()
    
    # Verificar quais faturas de venda têm custos associados
    faturas_com_custos = set()
    for custo in df_custos['SaleInvoice'].dropna().tolist() if 'SaleInvoice' in df_custos.columns else []:
        # Alguns registros podem ter múltiplas faturas separadas por vírgula
        for fatura in custo.split(','):
            faturas_com_custos.add(fatura.strip())
    
    faturas_sem_custos = faturas_venda - faturas_com_custos
    print(f"Faturas de venda sem custos associados: {len(faturas_sem_custos)}")
    if faturas_sem_custos:
        print(list(faturas_sem_custos)[:10])  # Mostrar apenas as 10 primeiras para não sobrecarregar a saída
    
    # Verificar se há custos sem faturas de venda associadas
    custos_sem_fatura = df_custos[df_custos['SaleInvoice'].isna()] if 'SaleInvoice' in df_custos.columns else pd.DataFrame()
    print(f"\nCustos sem faturas de venda associadas: {len(custos_sem_fatura)} de {len(df_custos)}")
    
    # Propor uma solução para o problema dos custos nulos no resumo
    print("\n===== PROPOSTA DE SOLUÇÃO =====")
    print("O problema principal identificado é que os custos não estão sendo corretamente associados às vendas no resumo.")
    print("Isso ocorre porque muitos custos não têm uma fatura de venda associada (campo SaleInvoice nulo).")
    print("Para resolver este problema, podemos:")
    print("1. Associar os custos às vendas com base em alguma lógica de negócio (por exemplo, data ou cliente)")
    print("2. Calcular o custo total e distribuí-lo proporcionalmente entre as vendas")
    print("3. Implementar um sistema de alocação manual de custos")
    
    # Exemplo de como poderia ser a distribuição proporcional dos custos
    print("\nExemplo de distribuição proporcional dos custos:")
    if total_vendas > 0:
        fator_custo = total_custos / total_vendas
        print(f"Fator de custo (custo total / venda total): {fator_custo:.4f}")
        print("Aplicando este fator a cada venda, teríamos:")
        
        # Criar um DataFrame de exemplo com a distribuição proporcional
        df_exemplo = pd.DataFrame()
        df_exemplo['Invoice_No'] = df_vendas['Invoice_No']
        df_exemplo['Total_PVP'] = df_vendas['Total_PVP']
        df_exemplo['Custo_Estimado'] = df_vendas['Total_PVP'] * fator_custo
        df_exemplo['Margem_Bruta'] = df_vendas['Total_PVP'] - df_exemplo['Custo_Estimado']
        df_exemplo['Margem_Percentual'] = (df_exemplo['Margem_Bruta'] / df_vendas['Total_PVP']) * 100
        
        print(df_exemplo.head(10).to_string(index=False))

if __name__ == "__main__":
    analisar_dados()
