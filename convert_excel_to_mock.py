#!/usr/bin/env python3
"""
Converte dados do Excel modelo para formato do backend
Lê os ficheiros JSON extraídos do Excel e gera dados mock no formato correto
"""
import json
import uuid
from datetime import datetime

def timestamp_to_date(timestamp):
    """Converte timestamp Unix para string de data"""
    return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")

def convert_excel_data():
    """Converte dados Excel para formato backend"""
    
    print("🔄 Convertendo dados do Excel modelo para formato backend...")
    
    # Ler dados dos ficheiros JSON
    try:
        with open("workbook_all_sheets_atualizado.json", "r", encoding="utf-8") as f:
            workbook = json.load(f)
        
        with open("Resumo_atualizado.json", "r", encoding="utf-8") as f:
            resumo = json.load(f)
            
        print(f"✅ Dados carregados: {len(workbook['Vendas'])} vendas, {len(workbook['Custos'])} custos")
        
    except Exception as e:
        print(f"❌ Erro ao carregar ficheiros: {e}")
        return None
    
    # Converter vendas
    sales = []
    for i, venda in enumerate(workbook["Vendas"]):  # Todas as vendas
        # Gerar customer name baseado no número
        customer_num = str(venda["Customer"])
        if customer_num == "999999990":
            client_name = "Cliente Genérico"
        elif customer_num == "92314397720":
            client_name = "Maria Santos - Empresarial"
        elif customer_num == "517425840":
            client_name = "João Silva - Particular"
        elif customer_num == "516540688":
            client_name = "Pedro Costa - Familiar"
        else:
            client_name = f"Cliente {customer_num[-4:]}"
        
        # Determinar tipo de viagem baseado no valor
        amount = venda["Total_PVP"]
        if amount > 10000:
            trip_type = "Premium International"
        elif amount > 3000:
            trip_type = "Europe Circuit"
        elif amount > 1000:
            trip_type = "Weekend Break"
        elif amount > 0:
            trip_type = "Domestic Trip"
        else:
            trip_type = "Cancellation"
        
        sale = {
            "id": f"s{i+1}",
            "number": venda["Invoice_No"],
            "date": timestamp_to_date(venda["Date"]),
            "client": f"{client_name} - {trip_type}",
            "amount": float(venda["Total_PVP"]),
            "vat_amount": 0,  # Regime de margem
            "gross_total": float(venda["Total_PVP"]),
            "linked_costs": []
        }
        sales.append(sale)
    
    # Converter custos
    costs = []
    cost_counter = 1
    
    for custo in workbook["Custos"]:  # Todos os custos
        # Extrair informação do supplier
        supplier_info = custo["Supplier"]
        if " - " in supplier_info:
            supplier_nif, supplier_name = supplier_info.split(" - ", 1)
        else:
            supplier_nif = "N/A"
            supplier_name = supplier_info
        
        # Gerar descrição baseada no tipo de fornecedor
        if "hotel" in supplier_name.lower() or "resort" in supplier_name.lower():
            description = "Alojamento - Estadia turística"
        elif "air" in supplier_name.lower() or "airways" in supplier_name.lower() or "airlines" in supplier_name.lower():
            description = "Transporte aéreo - Voos"
        elif "tour" in supplier_name.lower() or "viag" in supplier_name.lower():
            description = "Serviços turísticos - Excursões"
        elif "rent" in supplier_name.lower() or "aluguer" in supplier_name.lower():
            description = "Aluguer de viaturas"
        elif "seguros" in supplier_name.lower() or "insurance" in supplier_name.lower():
            description = "Seguro de viagem"
        else:
            description = "Serviços diversos - Fornecimentos"
        
        cost = {
            "id": f"c{cost_counter}",
            "supplier": supplier_name,
            "description": description,
            "date": timestamp_to_date(custo["Date"]),
            "amount": float(custo["Cost"]),
            "vat_amount": float(custo["Cost"]) * 0.23,  # Estimar IVA a 23%
            "gross_total": float(custo["Cost"]) * 1.23,
            "document_number": custo["SupplierInvoice"],
            "linked_sales": []
        }
        costs.append(cost)
        cost_counter += 1
    
    # NÃO criar associações automáticas - o utilizador final fará manualmente
    print("⚠️ Dados carregados SEM associações - utilizador criará as ligações")
    
    # Gerar estrutura final
    mock_data = {
        "sales": sales,
        "costs": costs,
        "metadata": {
            "company_name": "Agência de Viagens Excel Modelo Lda",
            "tax_registration": "999999990",
            "start_date": "2025-01-01",
            "end_date": "2025-12-31",
            "currency": "EUR",
            "source": "Excel modelo convertido automaticamente"
        }
    }
    
    # Estatísticas
    total_sales = sum(s["amount"] for s in sales if s["amount"] > 0)
    total_costs = sum(c["amount"] for c in costs)
    margin = total_sales - total_costs
    margin_pct = (margin / total_sales * 100) if total_sales > 0 else 0
    
    print(f"\n📊 ESTATÍSTICAS DOS DADOS CONVERTIDOS:")
    print(f"  📈 Vendas: {len(sales)} documentos | Total: €{total_sales:,.2f}")
    print(f"  💰 Custos: {len(costs)} documentos | Total: €{total_costs:,.2f}")
    print(f"  📊 Margem estimada: €{margin:,.2f} ({margin_pct:.1f}%)")
    print(f"  ⚠️ SEM associações - utilizador criará manualmente")
    
    return mock_data

def save_converted_data(mock_data):
    """Guarda dados convertidos em ficheiro"""
    if not mock_data:
        return
    
    # Guardar em JSON para análise
    with open("excel_mock_converted.json", "w", encoding="utf-8") as f:
        json.dump(mock_data, f, indent=2, ensure_ascii=False)
    
    # Gerar código Python para backend
    with open("excel_mock_data.py", "w", encoding="utf-8") as f:
        f.write('"""Dados mock gerados automaticamente do Excel modelo"""\n\n')
        f.write('EXCEL_MOCK_DATA = ')
        f.write(json.dumps(mock_data, indent=4, ensure_ascii=False))
    
    print(f"✅ Dados guardados em:")
    print(f"   - excel_mock_converted.json (análise)")
    print(f"   - excel_mock_data.py (backend)")

if __name__ == "__main__":
    # Converter dados
    converted_data = convert_excel_data()
    
    if converted_data:
        # Guardar ficheiros
        save_converted_data(converted_data)
        
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print(f"  1. Verificar dados em excel_mock_converted.json")
        print(f"  2. Substituir mock_data em backend/app/main.py")
        print(f"  3. Testar aplicação com dados reais")
        print(f"  4. Ajustar associações se necessário")
    else:
        print("❌ Falha na conversão dos dados")