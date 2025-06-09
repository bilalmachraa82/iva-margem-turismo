#!/usr/bin/env python3
"""
Validação final dos dados Excel convertidos para o backend
"""
import json

def validate_excel_data():
    """Valida os dados convertidos do Excel"""
    
    print("🔍 VALIDAÇÃO DOS DADOS EXCEL CONVERTIDOS")
    print("=" * 50)
    
    # Ler dados convertidos
    try:
        with open("excel_mock_converted.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print("✅ Dados carregados com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False
    
    # Validações básicas
    sales = data.get("sales", [])
    costs = data.get("costs", [])
    metadata = data.get("metadata", {})
    
    print(f"\n📊 ESTRUTURA DOS DADOS:")
    print(f"  📈 Vendas: {len(sales)} documentos")
    print(f"  💰 Custos: {len(costs)} documentos")
    print(f"  📝 Metadata: {len(metadata)} campos")
    
    # Validar campos obrigatórios das vendas
    print(f"\n🔍 VALIDAÇÃO VENDAS:")
    required_sale_fields = ["id", "number", "date", "client", "amount", "vat_amount", "gross_total", "linked_costs"]
    valid_sales = 0
    
    for sale in sales:
        if all(field in sale for field in required_sale_fields):
            valid_sales += 1
        else:
            missing = [f for f in required_sale_fields if f not in sale]
            print(f"  ⚠️ Venda {sale.get('id', 'N/A')}: campos em falta {missing}")
    
    print(f"  ✅ Vendas válidas: {valid_sales}/{len(sales)}")
    
    # Validar campos obrigatórios dos custos
    print(f"\n🔍 VALIDAÇÃO CUSTOS:")
    required_cost_fields = ["id", "supplier", "description", "date", "amount", "vat_amount", "gross_total", "document_number", "linked_sales"]
    valid_costs = 0
    
    for cost in costs:
        if all(field in cost for field in required_cost_fields):
            valid_costs += 1
        else:
            missing = [f for f in required_cost_fields if f not in cost]
            print(f"  ⚠️ Custo {cost.get('id', 'N/A')}: campos em falta {missing}")
    
    print(f"  ✅ Custos válidos: {valid_costs}/{len(costs)}")
    
    # Validar regime de margem
    print(f"\n🔍 VALIDAÇÃO REGIME DE MARGEM:")
    
    # Verificar se vendas não têm IVA separado
    sales_with_vat = [s for s in sales if s.get("vat_amount", 0) != 0]
    if sales_with_vat:
        print(f"  ❌ {len(sales_with_vat)} vendas com IVA separado (inválido no regime de margem)")
    else:
        print(f"  ✅ Todas as vendas sem IVA separado (regime de margem correto)")
    
    # Calcular totais
    total_sales = sum(s["amount"] for s in sales if s["amount"] > 0)
    total_costs = sum(c["amount"] for c in costs if c["amount"] > 0)
    margin = total_sales - total_costs
    margin_pct = (margin / total_sales * 100) if total_sales > 0 else 0
    
    print(f"\n📊 ANÁLISE FINANCEIRA:")
    print(f"  📈 Total vendas: €{total_sales:,.2f}")
    print(f"  💰 Total custos: €{total_costs:,.2f}")
    print(f"  📊 Margem: €{margin:,.2f} ({margin_pct:.1f}%)")
    
    # Verificar margens realistas
    if margin_pct < 0:
        print(f"  ⚠️ Margem negativa - verificar associações")
    elif margin_pct > 50:
        print(f"  ⚠️ Margem muito alta para turismo (típico: 5-25%)")
    elif 5 <= margin_pct <= 25:
        print(f"  ✅ Margem dentro dos padrões da indústria")
    else:
        print(f"  ⚡ Margem fora do típico mas aceitável")
    
    # Verificar associações (devem estar vazias)
    print(f"\n🔗 VERIFICAÇÃO ASSOCIAÇÕES:")
    sales_with_links = [s for s in sales if s.get("linked_costs")]
    costs_with_links = [c for c in costs if c.get("linked_sales")]
    
    if sales_with_links or costs_with_links:
        print(f"  ⚠️ Encontradas associações pré-existentes:")
        print(f"    Vendas com custos: {len(sales_with_links)}")
        print(f"    Custos com vendas: {len(costs_with_links)}")
    else:
        print(f"  ✅ Dados sem associações - utilizador criará manualmente")
    
    # Verificar documentos únicos
    print(f"\n🔍 VERIFICAÇÃO UNICIDADE:")
    sale_numbers = [s["number"] for s in sales]
    cost_numbers = [c["document_number"] for c in costs]
    
    if len(set(sale_numbers)) != len(sale_numbers):
        duplicates = len(sale_numbers) - len(set(sale_numbers))
        print(f"  ⚠️ {duplicates} números de venda duplicados")
    else:
        print(f"  ✅ Todos os números de venda são únicos")
    
    if len(set(cost_numbers)) != len(cost_numbers):
        duplicates = len(cost_numbers) - len(set(cost_numbers))
        print(f"  ⚠️ {duplicates} números de custo duplicados")
    else:
        print(f"  ✅ Todos os números de custo são únicos")
    
    # Resumo final
    print(f"\n🎯 RESUMO FINAL:")
    all_valid = (
        valid_sales == len(sales) and
        valid_costs == len(costs) and
        len(sales_with_vat) == 0 and
        len(set(sale_numbers)) == len(sale_numbers) and
        len(set(cost_numbers)) == len(cost_numbers)
    )
    
    if all_valid:
        print(f"  ✅ DADOS VÁLIDOS - Prontos para substituir mock data")
        print(f"  📋 {len(sales)} vendas e {len(costs)} custos do Excel modelo")
        print(f"  🏢 Empresa: {metadata.get('company_name', 'N/A')}")
        print(f"  📅 Período: {metadata.get('start_date')} a {metadata.get('end_date')}")
    else:
        print(f"  ⚠️ DADOS COM PROBLEMAS - Revisar antes do deploy")
    
    return all_valid

if __name__ == "__main__":
    validate_excel_data()