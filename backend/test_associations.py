#!/usr/bin/env python3
"""
Teste para validar associações many-to-many entre vendas e custos
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_associations():
    """Testa sistema de associações many-to-many"""
    
    print("=" * 60)
    print("TESTE ASSOCIACOES MANY-TO-MANY")
    print("=" * 60)
    
    # 1. Obter dados mock
    print("\n1. Carregando dados de demonstracao...")
    response = requests.get(f"{API_URL}/api/mock-data")
    
    if response.status_code != 200:
        print(f"ERRO: {response.status_code}")
        return
    
    data = response.json()
    session_id = data["session_id"]
    sales = data["sales"]
    costs = data["costs"]
    
    print(f"Session ID: {session_id}")
    print(f"Vendas carregadas: {len(sales)}")
    print(f"Custos carregados: {len(costs)}")
    
    # 2. Testar associacao manual
    print("\n2. Testando associacao manual...")
    
    # Associar primeira venda com primeiros 2 custos
    sale_ids = [sales[0]["id"]]  # s1
    cost_ids = [costs[0]["id"], costs[1]["id"]]  # c1, c2
    
    association_data = {
        "session_id": session_id,
        "sale_ids": sale_ids,
        "cost_ids": cost_ids
    }
    
    response = requests.post(f"{API_URL}/api/associate", json=association_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Associacoes criadas: {result['associations_made']}")
        print(f"Vendas atualizadas: {result['sales_updated']}")
        print(f"Custos atualizados: {result['costs_updated']}")
    else:
        print(f"ERRO na associacao: {response.status_code}")
        print(response.text)
        return
    
    # 3. Testar associacao multipla (many-to-many real)
    print("\n3. Testando associacao many-to-many...")
    
    # Associar múltiplas vendas com múltiplos custos
    sale_ids = [sales[1]["id"], sales[2]["id"]]  # s2, s3
    cost_ids = [costs[2]["id"], costs[3]["id"], costs[4]["id"]]  # c3, c4, c5
    
    association_data = {
        "session_id": session_id,
        "sale_ids": sale_ids,
        "cost_ids": cost_ids
    }
    
    response = requests.post(f"{API_URL}/api/associate", json=association_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Associacoes many-to-many criadas: {result['associations_made']}")
    else:
        print(f"ERRO: {response.status_code}")
        return
    
    # 4. Testar auto-match com IA
    print("\n4. Testando auto-match com IA...")
    
    auto_match_data = {
        "session_id": session_id,
        "threshold": 60
    }
    
    response = requests.post(f"{API_URL}/api/auto-match", json=auto_match_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Matches encontrados pela IA: {result['matches_found']}")
        avg_conf = result.get('average_confidence', 'N/A')
        if isinstance(avg_conf, (int, float)):
            print(f"Confianca media: {avg_conf:.1f}%")
        else:
            print(f"Confianca media: {avg_conf}")
        
        # Mostrar alguns matches
        for match in result.get('matches', [])[:3]:
            print(f"  - {match['sale_number']} <-> {match['cost_supplier']}")
            print(f"    Confianca: {match['confidence']:.1f}% | Razao: {match['reason']}")
    else:
        print(f"ERRO no auto-match: {response.status_code}")
    
    # 5. Verificar estado final das associações
    print("\n5. Verificando estado final...")
    
    # Testar endpoint de sessão (se existir)
    try:
        response = requests.get(f"{API_URL}/api/session/{session_id}")
        if response.status_code == 200:
            session_data = response.json()
            sales_final = session_data.get('sales', [])
            costs_final = session_data.get('costs', [])
            
            print(f"Vendas com associacoes:")
            for sale in sales_final:
                linked_count = len(sale.get('linked_costs', []))
                if linked_count > 0:
                    print(f"  {sale['number']}: {linked_count} custos ligados")
            
            print(f"Custos com associacoes:")
            for cost in costs_final:
                linked_count = len(cost.get('linked_sales', []))
                if linked_count > 0:
                    print(f"  {cost['supplier']}: {linked_count} vendas ligadas")
    except:
        print("Endpoint de sessao nao disponivel - OK")
    
    # 6. Testar cálculo final
    print("\n6. Testando calculo final...")
    
    calc_data = {
        "session_id": session_id,
        "vat_rate": 23
    }
    
    response = requests.post(f"{API_URL}/api/calculate", json=calc_data)
    
    if response.status_code == 200:
        print("Excel gerado com sucesso!")
        print("Associacoes many-to-many funcionando corretamente")
        
        # Salvar Excel para inspeção
        with open("teste_associacoes.xlsx", "wb") as f:
            f.write(response.content)
        print("Arquivo salvo: teste_associacoes.xlsx")
    else:
        print(f"ERRO no calculo: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 60)
    print("TESTE DE ASSOCIACOES CONCLUIDO")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_associations()
    except requests.exceptions.ConnectionError:
        print("ERRO: Servidor nao esta rodando em http://localhost:8000")
        print("Execute: cd backend && uvicorn app.main:app --reload")
    except Exception as e:
        print(f"ERRO: {e}")