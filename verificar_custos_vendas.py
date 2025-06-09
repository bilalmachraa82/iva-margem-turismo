import pandas as pd
import os

def analisar_custos_vendas(caminho_arquivo):
    print(f"Analisando arquivo: {caminho_arquivo}")
    
    try:
        # Ler todas as abas do arquivo Excel
        xls = pd.ExcelFile(caminho_arquivo)
        print(f"Abas disponíveis: {xls.sheet_names}")
        
        # Analisar aba de Vendas
        if 'Vendas' in xls.sheet_names:
            print("\n===== ANÁLISE DA ABA VENDAS =====")
            df_vendas = pd.read_excel(caminho_arquivo, sheet_name='Vendas')
            print(f"Dimensões: {df_vendas.shape[0]} linhas x {df_vendas.shape[1]} colunas")
            print(f"Colunas: {', '.join(df_vendas.columns.tolist())}")
            
            # Verificar valores de venda
            if 'Total_PVP' in df_vendas.columns:
                print(f"\nAnálise da coluna Total_PVP:")
                print(f"  - Soma total: {df_vendas['Total_PVP'].sum()}")
                print(f"  - Média: {df_vendas['Total_PVP'].mean()}")
                print(f"  - Valor mínimo: {df_vendas['Total_PVP'].min()}")
                print(f"  - Valor máximo: {df_vendas['Total_PVP'].max()}")
                
                # Verificar valores negativos
                negativos = df_vendas[df_vendas['Total_PVP'] < 0]
                if not negativos.empty:
                    print(f"\n  - ATENÇÃO: {len(negativos)} registros com valores negativos:")
                    print(negativos[['Invoice_No', 'Date', 'Customer', 'Total_PVP', 'Doc_Type']].to_string(index=False))
        
        # Analisar aba de Custos
        if 'Custos' in xls.sheet_names:
            print("\n===== ANÁLISE DA ABA CUSTOS =====")
            df_custos = pd.read_excel(caminho_arquivo, sheet_name='Custos')
            print(f"Dimensões: {df_custos.shape[0]} linhas x {df_custos.shape[1]} colunas")
            print(f"Colunas: {', '.join(df_custos.columns.tolist())}")
            
            # Verificar valores de custo
            if 'Cost' in df_custos.columns:
                print(f"\nAnálise da coluna Cost:")
                print(f"  - Soma total: {df_custos['Cost'].sum()}")
                print(f"  - Média: {df_custos['Cost'].mean()}")
                print(f"  - Valor mínimo: {df_custos['Cost'].min()}")
                print(f"  - Valor máximo: {df_custos['Cost'].max()}")
                
                # Verificar valores negativos
                negativos = df_custos[df_custos['Cost'] < 0]
                if not negativos.empty:
                    print(f"\n  - ATENÇÃO: {len(negativos)} registros com valores negativos:")
                    print(negativos[['SaleInvoice', 'Date', 'Supplier', 'Cost', 'Doc_Type']].to_string(index=False))
        
        # Analisar aba de Resumo
        if 'Resumo' in xls.sheet_names:
            print("\n===== ANÁLISE DA ABA RESUMO =====")
            df_resumo = pd.read_excel(caminho_arquivo, sheet_name='Resumo')
            print(f"Dimensões: {df_resumo.shape[0]} linhas x {df_resumo.shape[1]} colunas")
            print(f"Colunas: {', '.join(df_resumo.columns.tolist())}")
            
            # Verificar relação entre custo e venda
            if 'Total_PVP' in df_resumo.columns and 'Total_Cost' in df_resumo.columns:
                # Verificar valores nulos em Total_Cost
                nulos_custo = df_resumo['Total_Cost'].isna().sum()
                if nulos_custo > 0:
                    print(f"\n  - ATENÇÃO: {nulos_custo} registros com valores de custo nulos (NaN)")
                
                # Verificar registros onde o custo é maior que a venda
                df_resumo_valido = df_resumo.dropna(subset=['Total_Cost'])
                inconsistencias = df_resumo_valido[df_resumo_valido['Total_PVP'] < df_resumo_valido['Total_Cost']]
                
                if not inconsistencias.empty:
                    print(f"\n  - ATENÇÃO: {len(inconsistencias)} registros onde o custo é maior que o valor de venda:")
                    print(inconsistencias[['Invoice_No', 'Total_PVP', 'Total_Cost', 'Margem_Bruta']].to_string(index=False))
                else:
                    print("\n  - Não foram encontradas inconsistências onde o custo é maior que o valor de venda.")
                
                # Analisar margens
                if 'Margem_Bruta' in df_resumo.columns and 'Margem_Liquida' in df_resumo.columns:
                    print("\nAnálise de margens:")
                    print(f"  - Margem bruta total: {df_resumo['Margem_Bruta'].sum()}")
                    print(f"  - Margem líquida total: {df_resumo['Margem_Liquida'].sum()}")
                    
                    # Calcular percentuais
                    total_vendas = df_resumo['Total_PVP'].sum()
                    if total_vendas > 0:
                        margem_bruta_pct = df_resumo['Margem_Bruta'].sum() / total_vendas * 100
                        margem_liquida_pct = df_resumo['Margem_Liquida'].sum() / total_vendas * 100
                        print(f"  - Percentual médio de margem bruta: {margem_bruta_pct:.2f}%")
                        print(f"  - Percentual médio de margem líquida: {margem_liquida_pct:.2f}%")
    
    except Exception as e:
        print(f"Erro ao analisar o arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Caminho do arquivo Excel
    caminho_arquivo = r"C:\Users\Bilal\Documents\aiparati\claudia\iva-margem-turismo\Modelo_IVA_Margem_Agencias_Viagens_v3.xlsm.xlsx"
    analisar_custos_vendas(caminho_arquivo)
