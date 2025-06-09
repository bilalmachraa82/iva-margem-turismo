#!/usr/bin/env python3
"""
Script para analisar o ficheiro Excel modelo e extrair dados para validação
"""
import pandas as pd
import sys
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def analyze_excel_model():
    """Analisa o ficheiro Excel modelo e extrai informações"""
    
    file_path = "Modelo_IVA_Margem_Agencias_Viagens_v3.xlsm.xlsx"
    
    try:
        # Ler todas as folhas do Excel
        print("🔍 ANÁLISE DO FICHEIRO EXCEL MODELO")
        print("=" * 50)
        
        # Listar todas as folhas
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 Folhas encontradas: {excel_file.sheet_names}")
        print()
        
        # Analisar cada folha
        for sheet_name in excel_file.sheet_names:
            print(f"📊 FOLHA: {sheet_name}")
            print("-" * 30)
            
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
                print(f"Colunas: {list(df.columns)}")
                
                # Mostrar primeiras linhas
                if not df.empty:
                    print("Primeiras 5 linhas:")
                    print(df.head().to_string())
                    
                    # Analisar dados se parecer dados financeiros
                    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
                    if len(numeric_cols) > 0:
                        print(f"\nColunas numéricas: {list(numeric_cols)}")
                        for col in numeric_cols:
                            values = df[col].dropna()
                            if len(values) > 0:
                                print(f"  {col}: min={values.min():.2f}, max={values.max():.2f}, média={values.mean():.2f}")
                
            except Exception as e:
                print(f"Erro ao ler folha {sheet_name}: {str(e)}")
            
            print()
        
        # Tentar identificar folhas específicas de vendas e custos
        print("🎯 ANÁLISE ESPECÍFICA PARA DADOS DE TURISMO")
        print("=" * 50)
        
        # Procurar folhas que possam conter vendas
        vendas_sheets = [name for name in excel_file.sheet_names 
                        if any(keyword in name.lower() for keyword in ['venda', 'fatura', 'receita', 'invoice', 'sales'])]
        
        # Procurar folhas que possam conter custos  
        custos_sheets = [name for name in excel_file.sheet_names
                        if any(keyword in name.lower() for keyword in ['custo', 'compra', 'despesa', 'cost', 'expense'])]
        
        print(f"Possíveis folhas de vendas: {vendas_sheets}")
        print(f"Possíveis folhas de custos: {custos_sheets}")
        
        # Analisar margens se encontrarmos dados financeiros
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                # Procurar colunas que possam ser valores
                value_cols = []
                for col in df.columns:
                    if any(keyword in str(col).lower() for keyword in ['valor', 'montante', 'amount', 'total', 'preço', 'price']):
                        if df[col].dtype in ['float64', 'int64']:
                            value_cols.append(col)
                
                if value_cols:
                    print(f"\n💰 Análise de valores na folha '{sheet_name}':")
                    for col in value_cols:
                        values = df[col].dropna()
                        if len(values) > 0:
                            print(f"  {col}:")
                            print(f"    Total: €{values.sum():,.2f}")
                            print(f"    Média: €{values.mean():,.2f}")
                            print(f"    Min: €{values.min():,.2f}")
                            print(f"    Max: €{values.max():,.2f}")
                            
                            # Verificar se há valores negativos (possíveis notas de crédito)
                            negative_count = (values < 0).sum()
                            if negative_count > 0:
                                print(f"    ⚠️ {negative_count} valores negativos encontrados")
                            
                            # Verificar distribuição (para identificar outliers)
                            if len(values) > 1:
                                std = values.std()
                                outliers = values[abs(values - values.mean()) > 2 * std]
                                if len(outliers) > 0:
                                    print(f"    📊 {len(outliers)} possíveis outliers: {outliers.values}")
            except:
                continue
        
        # Procurar dados de datas
        print(f"\n📅 ANÁLISE DE DATAS")
        print("-" * 20)
        
        for sheet_name in excel_file.sheet_names:
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                
                date_cols = []
                for col in df.columns:
                    if any(keyword in str(col).lower() for keyword in ['data', 'date', 'dia']):
                        date_cols.append(col)
                    elif df[col].dtype == 'datetime64[ns]':
                        date_cols.append(col)
                
                if date_cols:
                    print(f"Folha '{sheet_name}' - Colunas de data: {date_cols}")
                    for col in date_cols:
                        dates = pd.to_datetime(df[col], errors='coerce').dropna()
                        if len(dates) > 0:
                            print(f"  {col}: de {dates.min().strftime('%Y-%m-%d')} até {dates.max().strftime('%Y-%m-%d')}")
            except:
                continue
                
    except FileNotFoundError:
        print(f"❌ Ficheiro não encontrado: {file_path}")
        print("Certifica-te que o ficheiro está na pasta correta.")
    except Exception as e:
        print(f"❌ Erro ao analisar ficheiro: {str(e)}")

if __name__ == "__main__":
    analyze_excel_model()