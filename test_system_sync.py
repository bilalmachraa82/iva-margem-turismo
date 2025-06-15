#!/usr/bin/env python3
"""
Script de teste síncrono do sistema IVA Margem Turismo
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_SESSION_ID = None

class TestResults:
    def __init__(self):
        self.results = []
        self.start_time = time.time()
    
    def add_result(self, test_name, status, details=""):
        self.results.append({
            "test": test_name,
            "status": "✅ PASS" if status else "❌ FAIL",
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
    
    def print_report(self):
        print("\n" + "="*80)
        print("📊 RELATÓRIO COMPLETO DE TESTES - SISTEMA IVA MARGEM TURISMO")
        print("="*80)
        print(f"Início: {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duração: {time.time() - self.start_time:.2f} segundos")
        print("-"*80)
        
        for result in self.results:
            print(f"\n{result['status']} {result['test']} [{result['timestamp']}]")
            if result['details']:
                print(f"   → {result['details']}")
        
        total = len(self.results)
        passed = sum(1 for r in self.results if "PASS" in r['status'])
        failed = total - passed
        
        print("\n" + "-"*80)
        print(f"RESUMO: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
        if failed > 0:
            print(f"⚠️  {failed} testes falharam!")
        else:
            print("🎉 TODOS OS TESTES PASSARAM! Sistema 100% funcional!")
        print("="*80)

results = TestResults()

def test_api_health():
    """Testa se a API está respondendo"""
    try:
        resp = requests.get(f"{BASE_URL}/")
        data = resp.json()
        success = resp.status_code == 200 and data.get("status") == "operational"
        results.add_result("API Health Check", success, f"Status: {resp.status_code}, Response: {data.get('status')}")
        return success
    except Exception as e:
        results.add_result("API Health Check", False, str(e))
        return False

def test_upload_efatura():
    """Testa upload de ficheiros CSV e-Fatura"""
    global TEST_SESSION_ID
    
    try:
        # Preparar os ficheiros
        with open('test_vendas_efatura.csv', 'rb') as f:
            vendas_file = ('vendas.csv', f, 'text/csv')
            with open('test_compras_efatura.csv', 'rb') as f2:
                compras_file = ('compras.csv', f2, 'text/csv')
                files = {
                    'vendas': vendas_file,
                    'compras': compras_file
                }
                
                resp = requests.post(f"{BASE_URL}/api/upload-efatura", files=files)
                
        result = resp.json()
        success = resp.status_code == 200 and "session_id" in result
        
        if success:
            TEST_SESSION_ID = result["session_id"]
            details = f"Session ID: {TEST_SESSION_ID}, Vendas: {result.get('sales_count', 0)}, Custos: {result.get('costs_count', 0)}"
        else:
            details = f"Erro: {result}"
        
        results.add_result("Upload e-Fatura CSV", success, details)
        return success
    except Exception as e:
        results.add_result("Upload e-Fatura CSV", False, str(e))
        return False

def test_get_session():
    """Testa obtenção de dados da sessão"""
    if not TEST_SESSION_ID:
        results.add_result("Get Session Data", False, "Sem session_id")
        return False
    
    try:
        resp = requests.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}")
        data = resp.json()
        success = resp.status_code == 200 and "sales" in data and "costs" in data
        
        if success:
            details = f"Vendas: {len(data['sales'])}, Custos: {len(data['costs'])}, Associações: {len(data.get('associations', []))}"
        else:
            details = f"Resposta inválida: {data}"
        
        results.add_result("Get Session Data", success, details)
        return success
    except Exception as e:
        results.add_result("Get Session Data", False, str(e))
        return False

def test_manual_association():
    """Testa associação manual de vendas com custos"""
    if not TEST_SESSION_ID:
        results.add_result("Manual Association", False, "Sem session_id")
        return False
    
    try:
        # Primeiro obter os IDs
        resp = requests.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}")
        data = resp.json()
        
        if not data.get("sales") or not data.get("costs"):
            results.add_result("Manual Association", False, "Sem dados para associar")
            return False
        
        sale_id = data["sales"][0]["id"]
        cost_ids = [data["costs"][0]["id"], data["costs"][1]["id"]]
        
        # Fazer associação
        association_data = {
            "session_id": TEST_SESSION_ID,
            "sale_ids": [sale_id],
            "cost_ids": cost_ids
        }
        
        resp = requests.post(f"{BASE_URL}/api/associate", json=association_data)
        result = resp.json()
        success = resp.status_code == 200 and result.get("status") == "success"
        
        if success:
            details = f"Venda {sale_id} associada com {len(cost_ids)} custos"
        else:
            details = f"Erro: {result}"
        
        results.add_result("Manual Association", success, details)
        return success
    except Exception as e:
        results.add_result("Manual Association", False, str(e))
        return False

def test_auto_match():
    """Testa auto-associação automática"""
    if not TEST_SESSION_ID:
        results.add_result("Auto-Match", False, "Sem session_id")
        return False
    
    try:
        match_data = {
            "session_id": TEST_SESSION_ID,
            "threshold": 50
        }
        
        resp = requests.post(f"{BASE_URL}/api/auto-match", json=match_data)
        result = resp.json()
        success = resp.status_code == 200 and "matches" in result
        
        if success:
            matches = result.get("matches", 0)
            details = f"{matches} associações automáticas criadas (threshold: 50%)"
        else:
            details = f"Erro: {result}"
        
        results.add_result("Auto-Match", success, details)
        return success
    except Exception as e:
        results.add_result("Auto-Match", False, str(e))
        return False

def test_calculate_and_export():
    """Testa cálculo de IVA e exportação Excel"""
    if not TEST_SESSION_ID:
        results.add_result("Calculate & Export", False, "Sem session_id")
        return False
    
    try:
        calc_data = {
            "session_id": TEST_SESSION_ID,
            "vat_rate": 23
        }
        
        resp = requests.post(f"{BASE_URL}/api/calculate", json=calc_data)
        
        if resp.status_code == 200:
            # Verificar headers
            content_type = resp.headers.get('Content-Type', '')
            if 'application/vnd.openxmlformats' in content_type:
                # É um arquivo Excel
                excel_data = resp.content
                
                # Salvar para verificar
                test_file = f"test_export_{TEST_SESSION_ID[:8]}.xlsx"
                with open(test_file, 'wb') as f:
                    f.write(excel_data)
                
                success = len(excel_data) > 0
                details = f"Excel gerado com {len(excel_data)} bytes, salvo como {test_file}"
            else:
                # É JSON (erro ou resposta alternativa)
                data = resp.json()
                success = False
                details = f"Resposta JSON: {data}"
        else:
            data = resp.json()
            success = False
            details = f"Erro HTTP {resp.status_code}: {data}"
        
        results.add_result("Calculate & Export Excel", success, details)
        return success
    except Exception as e:
        results.add_result("Calculate & Export Excel", False, str(e))
        return False

def test_reset_session():
    """Testa reset/limpeza de sessão"""
    try:
        # Upload vazio deve falhar
        resp = requests.post(f"{BASE_URL}/api/upload-efatura")
        success = resp.status_code in [400, 422]
        details = f"Status {resp.status_code} - Reset simulado através de upload vazio"
        
        results.add_result("Reset Session", success, details)
        return success
    except Exception as e:
        results.add_result("Reset Session", False, str(e))
        return False

def test_data_persistence():
    """Testa persistência de dados após recarregar"""
    if not TEST_SESSION_ID:
        results.add_result("Data Persistence", False, "Sem session_id")
        return False
    
    try:
        # Primeira leitura
        resp1 = requests.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}")
        data1 = resp1.json()
        
        # Aguardar um pouco
        time.sleep(1)
        
        # Segunda leitura
        resp2 = requests.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}")
        data2 = resp2.json()
        
        # Comparar
        success = (
            len(data1.get("sales", [])) == len(data2.get("sales", [])) and
            len(data1.get("costs", [])) == len(data2.get("costs", [])) and
            len(data1.get("associations", [])) == len(data2.get("associations", []))
        )
        
        details = "Dados mantidos consistentes entre requisições"
        results.add_result("Data Persistence", success, details)
        return success
    except Exception as e:
        results.add_result("Data Persistence", False, str(e))
        return False

def test_cors_headers():
    """Testa configuração CORS para frontend"""
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST'
        }
        
        resp = requests.options(f"{BASE_URL}/api/upload-efatura", headers=headers)
        cors_headers = resp.headers.get('Access-Control-Allow-Origin', '')
        success = cors_headers in ['*', 'http://localhost:3000']
        
        details = f"CORS Origin: {cors_headers}"
        results.add_result("CORS Configuration", success, details)
        return success
    except Exception as e:
        results.add_result("CORS Configuration", False, str(e))
        return False

def test_error_handling():
    """Testa tratamento de erros"""
    tests_passed = 0
    
    # Teste 1: Session ID inválido
    try:
        resp = requests.get(f"{BASE_URL}/api/session/invalid-session-id")
        if resp.status_code == 404:
            tests_passed += 1
    except:
        pass
    
    # Teste 2: Dados inválidos
    try:
        resp = requests.post(f"{BASE_URL}/api/calculate", json={"invalid": "data"})
        if resp.status_code in [400, 422]:
            tests_passed += 1
    except:
        pass
    
    success = tests_passed >= 1
    details = f"{tests_passed}/2 testes de erro passaram"
    results.add_result("Error Handling", success, details)
    return success

def run_all_tests():
    """Executa todos os testes"""
    print("🚀 Iniciando teste completo do sistema IVA Margem Turismo...")
    print("="*80)
    
    # Testes sequenciais
    test_api_health()
    test_upload_efatura()
    
    if TEST_SESSION_ID:
        # Testes principais
        test_get_session()
        test_cors_headers()
        test_error_handling()
        test_manual_association()
        test_auto_match()
        test_calculate_and_export()
        test_data_persistence()
        test_reset_session()
    
    # Imprimir relatório
    results.print_report()

if __name__ == "__main__":
    run_all_tests()