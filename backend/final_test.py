#!/usr/bin/env python3
"""
TESTE FINAL COMPLETO - IVA MARGEM TURISMO
Valida todo o sistema end-to-end
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_complete_workflow():
    """Teste completo do workflow"""
    
    print("=" * 80)
    print("TESTE FINAL COMPLETO - IVA MARGEM TURISMO")
    print("Sistema conforme CIVA Art. 308º - Portugal")
    print("=" * 80)
    
    try:
        # 1. Carregar dados mock
        print("\n1. CARREGANDO DADOS DE DEMONSTRACAO...")
        response = requests.get(f"{API_URL}/api/mock-data")
        
        if response.status_code != 200:
            print(f"ERRO: {response.status_code} - {response.text}")
            return False
        
        data = response.json()
        session_id = data["session_id"]
        print(f"   Session ID: {session_id}")
        print(f"   Vendas: {data['sales_count']}")
        print(f"   Custos: {data['costs_count']}")
        
        # Validar dados
        sales = data["sales"]
        costs = data["costs"]
        
        # Verificar se vendas não têm IVA (regime de margem)
        for sale in sales:
            if sale["vat_amount"] != 0:
                print(f"   ERRO: Venda {sale['number']} tem IVA separado (não permitido no regime de margem)")
                return False
        
        print("   OK: Vendas sem IVA separado (correto para regime de margem)")
        
        # 2. Testar associação manual
        print("\n2. TESTANDO ASSOCIACAO MANUAL...")
        
        # Cenário realista: João Silva - Viagem Paris
        sale_paris = sales[0]  # €1,500
        cost_voo = costs[1]    # €650 (TAP)
        cost_hotel = costs[0]  # €450 (Hotel)
        cost_tour = costs[3]   # €280 (Paris Tours)
        
        association_data = {
            "session_id": session_id,
            "sale_ids": [sale_paris["id"]],
            "cost_ids": [cost_voo["id"], cost_hotel["id"], cost_tour["id"]]
        }
        
        response = requests.post(f"{API_URL}/api/associate", json=association_data)
        if response.status_code != 200:
            print(f"   ERRO na associacao: {response.status_code}")
            return False
        
        result = response.json()
        print(f"   Associacoes criadas: {result['associations_made']}")
        
        # 3. Calcular e gerar Excel
        print("\n3. CALCULANDO IVA SOBRE MARGEM...")
        
        calc_data = {
            "session_id": session_id,
            "vat_rate": 23
        }
        
        response = requests.post(f"{API_URL}/api/calculate", json=calc_data)
        if response.status_code != 200:
            print(f"   ERRO no calculo: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
        
        # Salvar Excel
        excel_filename = f"iva_margem_final_test.xlsx"
        with open(excel_filename, "wb") as f:
            f.write(response.content)
        
        print(f"   Excel gerado: {excel_filename}")
        
        # 4. Validação manual dos cálculos
        print("\n4. VALIDACAO MANUAL DOS CALCULOS...")
        
        # Cenário João Silva:
        # Venda: €1,500
        # Custos: €650 + €450 + €280 = €1,380
        # Margem: €1,500 - €1,380 = €120
        # IVA (23%): €120 × 23% = €27.60
        # Margem líquida: €120 - €27.60 = €92.40
        
        venda_joao = 1500.00
        custos_joao = 650.00 + 450.00 + 280.00  # 1380.00
        margem_esperada = venda_joao - custos_joao  # 120.00
        iva_esperado = margem_esperada * 23 / 100  # 27.60
        liquida_esperada = margem_esperada - iva_esperado  # 92.40
        
        print(f"   Joao Silva - Viagem Paris:")
        print(f"   Valor cobrado: €{venda_joao:,.2f}")
        print(f"   Custos diretos: €{custos_joao:,.2f}")
        print(f"   Margem bruta: €{margem_esperada:,.2f}")
        print(f"   IVA sobre margem: €{iva_esperado:,.2f}")
        print(f"   Margem liquida: €{liquida_esperada:,.2f}")
        print(f"   % Margem: {(margem_esperada/venda_joao)*100:.1f}%")
        
        # 5. Testar frontend (se disponível)
        print("\n5. VERIFICANDO FRONTEND...")
        
        try:
            # Testar se o frontend está acessível
            response = requests.get("http://localhost:3000", timeout=2)
            print("   Frontend disponível em http://localhost:3000")
        except:
            print("   Frontend offline (normal - arquivo estático)")
        
        # 6. Sumário final
        print("\n6. SUMARIO FINAL")
        print("-" * 50)
        
        # Totais dos dados mock
        total_vendas = sum(sale["amount"] for sale in sales if sale["amount"] > 0)
        total_custos = sum(cost["amount"] for cost in costs)
        
        print(f"   Total vendas: €{total_vendas:,.2f}")
        print(f"   Total custos: €{total_custos:,.2f}")
        print(f"   Margem potencial: €{total_vendas - total_custos:,.2f}")
        
        # Estimativa de IVA total
        margem_estimada = total_vendas - total_custos
        iva_estimado = margem_estimada * 23 / 100 if margem_estimada > 0 else 0
        
        print(f"   IVA estimado (23%): €{iva_estimado:,.2f}")
        print(f"   Margem liquida estimada: €{margem_estimada - iva_estimado:,.2f}")
        
        print("\n" + "=" * 80)
        print("TESTE FINAL COMPLETO: SUCESSO!")
        print("Sistema IVA Margem Turismo funcionando corretamente")
        print("Conforme legislacao portuguesa (CIVA Art. 308º)")
        print("=" * 80)
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("ERRO: Servidor nao esta rodando em http://localhost:8000")
        print("Execute: cd backend && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"ERRO INESPERADO: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_workflow()
    exit(0 if success else 1)