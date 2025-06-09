import pandas as pd
import os
import numpy as np

def analisar_excel(caminho_arquivo):
    print(f"Analisando arquivo: {caminho_arquivo}")
    print(f"O arquivo existe: {os.path.exists(caminho_arquivo)}")
    
    try:
        # Tentar ler o arquivo Excel
        xls = pd.ExcelFile(caminho_arquivo)
        
        # Listar todas as abas do arquivo
        print(f"\nAbas disponíveis no arquivo: {xls.sheet_names}")
        
        # Analisar cada aba
        for aba in xls.sheet_names:
            print(f"\n{'='*50}")
            print(f"ANÁLISE DA ABA: {aba}")
            print(f"{'='*50}")
            
            df = pd.read_excel(caminho_arquivo, sheet_name=aba)
            
            # Mostrar informações básicas
            print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"Colunas disponíveis: {', '.join(df.columns.tolist())}")
            
            # Exibir os primeiros registros para entender a estrutura
            print("\nPrimeiras 5 linhas:")
            print(df.head().to_string())
            
            # Análise detalhada de cada coluna
            print("\nAnálise detalhada de cada coluna:")
            for col in df.columns:
                print(f"\nColuna: {col}")
                print(f"  - Tipo de dados: {df[col].dtype}")
                
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Análise para colunas numéricas
                    print(f"  - Min: {df[col].min()}")
                    print(f"  - Max: {df[col].max()}")
                    print(f"  - Média: {df[col].mean()}")
                    print(f"  - Valores nulos: {df[col].isna().sum()}")
                    try:
                        print(f"  - Valores negativos: {(df[col] < 0).sum()}")
                        if (df[col] < 0).sum() > 0:
                            print(f"    *** ATENÇÃO: Existem valores negativos nesta coluna! ***")
                    except:
                        print("  - Não foi possível verificar valores negativos")
                else:
                    # Análise para colunas não numéricas
                    print(f"  - Valores únicos: {df[col].nunique()}")
                    print(f"  - Valores nulos: {df[col].isna().sum()}")
            
            # Verificar relações específicas entre colunas de custo e venda
            if aba == "Vendas":
                print("\nAnálise da aba de Vendas:")
                if 'Total_PVP' in df.columns:
                    print(f"  - Total de vendas (soma Total_PVP): {df['Total_PVP'].sum()}")
                    print(f"  - Média de vendas: {df['Total_PVP'].mean()}")
                    if (df['Total_PVP'] < 0).sum() > 0:
                        print(f"  - ATENÇÃO: Existem {(df['Total_PVP'] < 0).sum()} vendas com valores negativos!")
                        print(f"    Registros com valores negativos:")
                        print(df[df['Total_PVP'] < 0].to_string())
            
            elif aba == "Custos":
                print("\nAnálise da aba de Custos:")
                if 'Cost' in df.columns:
                    print(f"  - Total de custos (soma Cost): {df['Cost'].sum()}")
                    print(f"  - Média de custos: {df['Cost'].mean()}")
                    if (df['Cost'] < 0).sum() > 0:
                        print(f"  - ATENÇÃO: Existem {(df['Cost'] < 0).sum()} custos com valores negativos!")
                        print(f"    Registros com valores negativos:")
                        print(df[df['Cost'] < 0].to_string())
            
            elif aba == "Resumo":
                print("\nAnálise da aba de Resumo:")
                if 'Total_PVP' in df.columns and 'Total_Cost' in df.columns:
                    # Verificar se há registros com custo maior que venda
                    try:
                        inconsistencias = df[df['Total_PVP'] < df['Total_Cost']]
                        if len(inconsistencias) > 0:
                            print(f"  - ATENÇÃO: Existem {len(inconsistencias)} registros onde o custo é maior que o valor de venda!")
                            print(f"    Registros com inconsistências:")
                            print(inconsistencias.to_string())
                        else:
                            print("  - Não foram encontradas inconsistências entre custos e vendas.")
                            
                        # Calcular margem média
                        if 'Margem_Bruta' in df.columns:
                            margem_media = df['Margem_Bruta'].mean() / df['Total_PVP'].mean() * 100
                            print(f"  - Margem bruta média: {margem_media:.2f}%")
                        
                        if 'Margem_Liquida' in df.columns:
                            margem_liquida_media = df['Margem_Liquida'].mean() / df['Total_PVP'].mean() * 100
                            print(f"  - Margem líquida média: {margem_liquida_media:.2f}%")
                    except Exception as e:
                        print(f"  - Erro ao analisar margens: {e}")
    
    except Exception as e:
        print(f"Erro ao analisar o arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Caminho do arquivo Excel
    caminho_arquivo = r"C:\Users\Bilal\Documents\aiparati\claudia\iva-margem-turismo\Modelo_IVA_Margem_Agencias_Viagens_v3.xlsm.xlsx"
    analisar_excel(caminho_arquivo)
