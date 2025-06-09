#!/usr/bin/env python3
"""
Análise detalhada dos dados mock vs padrões da indústria
"""
import json
from datetime import datetime

def analyze_mock_data():
    """Analisa dados mock e identifica problemas"""
    
    # Dados mock atuais (copiados do backend)
    sales = [
        {"id": "s1", "number": "FT E2025/1", "date": "2025-01-05", "client": "João Silva - Viagem Paris", "amount": 1800.00},
        {"id": "s2", "number": "FT E2025/2", "date": "2025-01-08", "client": "Maria Santos - Tour Europa", "amount": 2800.00},
        {"id": "s3", "number": "FT E2025/3", "date": "2025-01-10", "client": "Pedro Costa - Escapada Lisboa", "amount": 850.00},
        {"id": "s4", "number": "FR E2025/1", "date": "2025-01-12", "client": "Ana Ferreira - Cruzeiro Douro", "amount": 1600.00},
        {"id": "s5", "number": "FR E2025/3", "date": "2025-01-18", "client": "Sofia Rodrigues - América Tour", "amount": 12000.00},
        {"id": "s6", "number": "FT E2025/16", "date": "2025-01-20", "client": "Miguel Alves - Tailândia", "amount": 3200.00},
        {"id": "s7", "number": "NC E2025/1", "date": "2025-01-22", "client": "Correção - João Silva", "amount": -200.00}
    ]
    
    costs = [
        {"id": "c1", "supplier": "Hotel Pestana Porto", "description": "Alojamento 3 noites Twin", "date": "2025-01-03", "amount": 450.00},
        {"id": "c2", "supplier": "TAP Air Portugal", "description": "Voos LIS-CDG-LIS Classe Y", "date": "2025-01-02", "amount": 650.00},
        {"id": "c3", "supplier": "Europcar", "description": "Aluguer VW Golf 5 dias", "date": "2025-01-06", "amount": 180.00},
        {"id": "c4", "supplier": "Paris Tours SARL", "description": "City tour + Versailles", "date": "2025-01-04", "amount": 280.00},
        {"id": "c5", "supplier": "Douro Azul", "description": "Cruzeiro 2 dias Régua-Pinhão", "date": "2025-01-11", "amount": 1200.00},
        {"id": "c6", "supplier": "American Express Travel", "description": "Pacote USA 15 dias all-inclusive", "date": "2025-01-16", "amount": 9200.00},
        {"id": "c7", "supplier": "Thai Airways", "description": "Voos LIS-BKK-LIS Business", "date": "2025-01-17", "amount": 2500.00}
    ]
    
    print("🔍 ANÁLISE DOS DADOS MOCK ATUAIS")
    print("=" * 50)
    
    # Análise das vendas
    total_sales = sum(s["amount"] for s in sales if s["amount"] > 0)
    positive_sales = [s for s in sales if s["amount"] > 0]
    
    print(f"📈 VENDAS:")
    print(f"  Total: €{total_sales:,.2f}")
    print(f"  Documentos positivos: {len(positive_sales)}")
    print(f"  Média: €{total_sales/len(positive_sales):,.2f}")
    print(f"  Min: €{min(s['amount'] for s in positive_sales):,.2f}")
    print(f"  Max: €{max(s['amount'] for s in positive_sales):,.2f}")
    
    # Análise dos custos
    total_costs = sum(c["amount"] for c in costs)
    
    print(f"\n💰 CUSTOS:")
    print(f"  Total: €{total_costs:,.2f}")
    print(f"  Documentos: {len(costs)}")
    print(f"  Média: €{total_costs/len(costs):,.2f}")
    print(f"  Min: €{min(c['amount'] for c in costs):,.2f}")
    print(f"  Max: €{max(c['amount'] for c in costs):,.2f}")
    
    # Análise de margens (assumindo associações lógicas)
    margin_total = total_sales - total_costs
    margin_pct = (margin_total / total_sales) * 100
    
    print(f"\n📊 MARGENS:")
    print(f"  Margem Total: €{margin_total:,.2f}")
    print(f"  Margem %: {margin_pct:.1f}%")
    
    # Identificar problemas
    print(f"\n🚨 PROBLEMAS IDENTIFICADOS:")
    
    if margin_pct > 30:
        print(f"  ❌ Margem muito alta ({margin_pct:.1f}%) - Típico turismo: 5-25%")
    
    if margin_pct < 5:
        print(f"  ❌ Margem muito baixa ({margin_pct:.1f}%) - Negócio inviável")
    
    # Análise por venda (simulando associações lógicas)
    print(f"\n🔍 ANÁLISE POR VIAGEM:")
    
    # Simular associações baseadas em descrições e datas
    trips = [
        {
            "name": "João Silva - Paris",
            "sale": 1800.00,
            "costs": [450.00, 650.00, 180.00, 280.00],  # Hotel + Voo + Carro + Tour
            "description": "Weekend Paris"
        },
        {
            "name": "Maria Santos - Europa", 
            "sale": 2800.00,
            "costs": [1200.00, 650.00],  # Cruzeiro + elementos extras
            "description": "Tour Europa multi-país"
        },
        {
            "name": "Sofia Rodrigues - USA",
            "sale": 12000.00,
            "costs": [9200.00],  # Pacote all-inclusive
            "description": "Tour América 15 dias"
        },
        {
            "name": "Miguel Alves - Tailândia",
            "sale": 3200.00,
            "costs": [2500.00],  # Voo Business
            "description": "Viagem Ásia"
        }
    ]
    
    for trip in trips:
        trip_costs = sum(trip["costs"])
        trip_margin = trip["sale"] - trip_costs
        trip_margin_pct = (trip_margin / trip["sale"]) * 100
        
        print(f"  {trip['name']}:")
        print(f"    Venda: €{trip['sale']:,.2f} | Custos: €{trip_costs:,.2f}")
        print(f"    Margem: €{trip_margin:,.2f} ({trip_margin_pct:.1f}%)")
        
        if trip_margin_pct > 25:
            print(f"    ⚠️ Margem alta para {trip['description']}")
        elif trip_margin_pct < 8:
            print(f"    ⚠️ Margem baixa para {trip['description']}")
        else:
            print(f"    ✅ Margem realista")
    
    # Recomendações baseadas no Excel modelo
    print(f"\n💡 RECOMENDAÇÕES BASEADAS NO EXCEL MODELO:")
    print(f"  1. Usar campos encontrados: IVA_Rate, Margem_Bruta, Margem_Liquida")
    print(f"  2. Incluir mais documentos 'Fatura-recibo' (encontrados no modelo)")
    print(f"  3. Ajustar margens para 8-20% (padrão indústria)")
    print(f"  4. Adicionar mais variabilidade de fornecedores")
    print(f"  5. Incluir custos típicos: seguro viagem, transfers, guias")
    
    # Sugerir dados melhorados
    print(f"\n🎯 SUGESTÕES DE MELHORIA:")
    print(f"  - Reduzir margem da viagem USA para ~15%")
    print(f"  - Adicionar custos de seguro e transfers")
    print(f"  - Incluir mais notas de crédito realistas")
    print(f"  - Datas mais espalhadas ao longo do ano")
    print(f"  - Valores mais granulares (evitar números redondos)")

if __name__ == "__main__":
    analyze_mock_data()