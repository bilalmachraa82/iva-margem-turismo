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
            print(f"\n--- Análise da aba: {aba} ---")
            df = pd.read_excel(caminho_arquivo, sheet_name=aba)
            
            # Mostrar informações básicas
            print(f"Dimensões: {df.shape[0]} linhas x {df.shape[1]} colunas")
            
            # Verificar se existem colunas relacionadas a custo e venda
            colunas = df.columns.tolist()
            print(f"Colunas disponíveis: {colunas}")
            
            # Procurar colunas relacionadas a custo e venda
            colunas_custo = [col for col in colunas if 'custo' in str(col).lower() or 'cost' in str(col).lower()]
            colunas_venda = [col for col in colunas if 'venda' in str(col).lower() or 'preco' in str(col).lower() or 'preço' in str(col).lower() or 'price' in str(col).lower() or 'pvp' in str(col).lower() or 'total_pvp' in str(col).lower()]
            
            if colunas_custo:
                print(f"\nColunas de custo encontradas: {colunas_custo}")
                for col in colunas_custo:
                    print(f"Estatísticas de {col}:")
                    if pd.api.types.is_numeric_dtype(df[col]):
                        print(f"  - Min: {df[col].min()}")
                        print(f"  - Max: {df[col].max()}")
                        print(f"  - Média: {df[col].mean()}")
                        print(f"  - Valores nulos: {df[col].isna().sum()}")
                        print(f"  - Valores negativos: {(df[col] < 0).sum()}")
                    else:
                        print(f"  - Tipo de dados: {df[col].dtype}")
                        print(f"  - Valores únicos: {df[col].nunique()}")
                        print(f"  - Valores nulos: {df[col].isna().sum()}")
            else:
                print("\nNenhuma coluna de custo identificada diretamente.")
            
            if colunas_venda:
                print(f"\nColunas de venda encontradas: {colunas_venda}")
                for col in colunas_venda:
                    print(f"Estatísticas de {col}:")
                    if pd.api.types.is_numeric_dtype(df[col]):
                        print(f"  - Min: {df[col].min()}")
                        print(f"  - Max: {df[col].max()}")
                        print(f"  - Média: {df[col].mean()}")
                        print(f"  - Valores nulos: {df[col].isna().sum()}")
                        print(f"  - Valores negativos: {(df[col] < 0).sum()}")
                    else:
                        print(f"  - Tipo de dados: {df[col].dtype}")
                        print(f"  - Valores únicos: {df[col].nunique()}")
                        print(f"  - Valores nulos: {df[col].isna().sum()}")
            else:
                print("\nNenhuma coluna de venda identificada diretamente.")
            
            # Verificar valores numéricos em todas as colunas
            print("\nAnálise de valores numéricos em todas as colunas:")
            for col in colunas:
                print(f"Coluna {col}:")
                if pd.api.types.is_numeric_dtype(df[col]):
                    print(f"  - Tipo de dados: {df[col].dtype}")
                    print(f"  - Min: {df[col].min()}")
                    print(f"  - Max: {df[col].max()}")
                    print(f"  - Média: {df[col].mean()}")
                    print(f"  - Valores nulos: {df[col].isna().sum()}")
                    print(f"  - Valores negativos: {(df[col] < 0).sum()}")
                else:
                    print(f"  - Tipo de dados: {df[col].dtype}")
                    print(f"  - Valores únicos: {df[col].nunique()}")
                    print(f"  - Valores nulos: {df[col].isna().sum()}")
            
            # Verificar se há inconsistências (como valores de venda menores que custo)
            if colunas_custo and colunas_venda:
                for custo_col in colunas_custo:
                    for venda_col in colunas_venda:
                        if pd.api.types.is_numeric_dtype(df[custo_col]) and pd.api.types.is_numeric_dtype(df[venda_col]):
                            try:
                                inconsistencias = (df[venda_col] < df[custo_col]).sum()
                                print(f"\nInconsistências entre {venda_col} e {custo_col} (venda < custo): {inconsistencias} registros")
                            except Exception as e:
                                print(f"\nNão foi possível comparar {venda_col} e {custo_col}: {e}")
    
    except Exception as e:
        print(f"Erro ao analisar o arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Caminho do arquivo Excel
    caminho_arquivo = r"C:\Users\Bilal\Documents\aiparati\claudia\iva-margem-turismo\Modelo_IVA_Margem_Agencias_Viagens_v3.xlsm.xlsx"
    analisar_excel(caminho_arquivo)
