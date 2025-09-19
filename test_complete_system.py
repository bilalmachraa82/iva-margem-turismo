#!/usr/bin/env python3
"""
Script de teste completo do sistema IVA Margem Turismo
Testa todos os endpoints e funcionalidades
"""

import asyncio
import aiohttp
import json
import os
import time
from datetime import datetime
import pandas as pd

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

async def test_api_health():
    """Testa se a API está respondendo"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/") as resp:
                data = await resp.json()
                status_text = data.get("status", "")
                success = resp.status == 200 and "IVA Margem" in status_text
                details = f"HTTP {resp.status} · {status_text}"
                results.add_result("API Health Check", success, details)
                return success
        except Exception as e:
            results.add_result("API Health Check", False, str(e))
            return False

async def test_upload_efatura():
    """Testa upload de ficheiros CSV e-Fatura"""
    global TEST_SESSION_ID
    
    async with aiohttp.ClientSession() as session:
        try:
            # Preparar os ficheiros
            with open('test_vendas_efatura.csv', 'rb') as f:
                vendas_data = f.read()
            with open('test_compras_efatura.csv', 'rb') as f:
                compras_data = f.read()
            
            # Criar FormData
            data = aiohttp.FormData()
            data.add_field('vendas', vendas_data, filename='vendas.csv', content_type='text/csv')
            data.add_field('compras', compras_data, filename='compras.csv', content_type='text/csv')
            
            async with session.post(f"{BASE_URL}/api/upload-efatura", data=data) as resp:
                result = await resp.json()
                success = resp.status == 200 and "session_id" in result
                
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

async def test_get_session():
    """Testa obtenção de dados da sessão"""
    if not TEST_SESSION_ID:
        results.add_result("Get Session Data", False, "Sem session_id")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}") as resp:
                data = await resp.json()
                success = resp.status == 200 and "sales" in data and "costs" in data
                
                if success:
                    details = f"Vendas: {len(data['sales'])}, Custos: {len(data['costs'])}, Associações: {len(data.get('associations', []))}"
                else:
                    details = f"Resposta inválida: {data}"
                
                results.add_result("Get Session Data", success, details)
                return success
        except Exception as e:
            results.add_result("Get Session Data", False, str(e))
            return False

async def test_manual_association():
    """Testa associação manual de vendas com custos"""
    if not TEST_SESSION_ID:
        results.add_result("Manual Association", False, "Sem session_id")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            # Primeiro obter os IDs
            async with session.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}") as resp:
                data = await resp.json()
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
            
            async with session.post(f"{BASE_URL}/api/associate", json=association_data) as resp:
                result = await resp.json()
                success = resp.status == 200 and result.get("status") == "success"
                
                if success:
                    details = f"Venda {sale_id} associada com {len(cost_ids)} custos"
                else:
                    details = f"Erro: {result}"
                
                results.add_result("Manual Association", success, details)
                return success
        except Exception as e:
            results.add_result("Manual Association", False, str(e))
            return False

async def test_auto_match():
    """Testa auto-associação automática"""
    if not TEST_SESSION_ID:
        results.add_result("Auto-Match", False, "Sem session_id")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            match_data = {
                "session_id": TEST_SESSION_ID,
                "threshold": 50
            }
            
            async with session.post(f"{BASE_URL}/api/auto-match", json=match_data) as resp:
                result = await resp.json()
                matches_found = result.get("matches_found", len(result.get("matches", [])))
                success = resp.status == 200 and result.get("status") == "success"
                
                if success:
                    details = f"{matches_found} associações automáticas criadas (threshold: 50%)"
                else:
                    details = f"Erro: {result}"
                
                results.add_result("Auto-Match", success, details)
                return success
        except Exception as e:
            results.add_result("Auto-Match", False, str(e))
            return False

async def test_calculate_and_export():
    """Testa cálculo de IVA e exportação Excel"""
    if not TEST_SESSION_ID:
        results.add_result("Calculate & Export", False, "Sem session_id")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            calc_data = {
                "session_id": TEST_SESSION_ID,
                "vat_rate": 23
            }
            
            async with session.post(f"{BASE_URL}/api/calculate", json=calc_data) as resp:
                if resp.status == 200:
                    # Verificar headers
                    content_type = resp.headers.get('Content-Type', '')
                    if 'application/vnd.openxmlformats' in content_type:
                        # É um arquivo Excel
                        excel_data = await resp.read()
                        
                        # Salvar para verificar
                        test_file = f"test_export_{TEST_SESSION_ID[:8]}.xlsx"
                        with open(test_file, 'wb') as f:
                            f.write(excel_data)
                        
                        success = len(excel_data) > 0
                        details = f"Excel gerado com {len(excel_data)} bytes, salvo como {test_file}"
                    else:
                        # É JSON (erro ou resposta alternativa)
                        data = await resp.json()
                        success = False
                        details = f"Resposta JSON: {data}"
                else:
                    data = await resp.json()
                    success = False
                    details = f"Erro HTTP {resp.status}: {data}"
                
                results.add_result("Calculate & Export Excel", success, details)
                return success
        except Exception as e:
            results.add_result("Calculate & Export Excel", False, str(e))
            return False

async def test_premium_analytics_suite():
    """Valida todos os endpoints de analytics premium"""
    if not TEST_SESSION_ID:
        results.add_result("Analytics - Precondition", False, "Sem session_id")
        return False

    async with aiohttp.ClientSession() as session:
        payload = {
            "session_id": TEST_SESSION_ID,
            "vat_rate": 23
        }

        async def call_json(name, method, url, expect_key):
            try:
                async with session.request(method, url, json=payload if method == "POST" else None) as resp:
                    data = await resp.json()
                    success = resp.status == 200 and expect_key in data
                    details = f"HTTP {resp.status} · Chave '{expect_key}' {'ok' if expect_key in data else 'ausente'}"
                    results.add_result(name, success, details)
                    return success
            except Exception as exc:
                results.add_result(name, False, str(exc))
                return False

        success = True
        success &= await call_json(
            "Analytics - Executive Summary",
            "POST",
            f"{BASE_URL}/api/analytics/executive-summary",
            "executive_summary"
        )

        success &= await call_json(
            "Analytics - Waterfall",
            "POST",
            f"{BASE_URL}/api/analytics/waterfall",
            "waterfall_analysis"
        )

        success &= await call_json(
            "Analytics - Scenarios",
            "POST",
            f"{BASE_URL}/api/analytics/scenarios",
            "scenario_analysis"
        )

        success &= await call_json(
            "Analytics - Outliers",
            "POST",
            f"{BASE_URL}/api/analytics/outliers",
            "outlier_analysis"
        )

        # Advanced KPIs é GET com querystring
        try:
            async with session.get(f"{BASE_URL}/api/analytics/kpis/{TEST_SESSION_ID}", params={"vat_rate": 23}) as resp:
                data = await resp.json()
                success_kpi = resp.status == 200 and "advanced_kpis" in data
                details = f"HTTP {resp.status} · KPI keys: {list(data.get('advanced_kpis', {}).keys())[:3]}"
                results.add_result("Analytics - Advanced KPIs", success_kpi, details)
                success &= success_kpi
        except Exception as exc:
            results.add_result("Analytics - Advanced KPIs", False, str(exc))
            success = False

        return success

async def test_reset_session():
    """Testa reset/limpeza de sessão"""
    if not TEST_SESSION_ID:
        results.add_result("Reset Session", False, "Sem session_id")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            # Criar nova sessão vazia (simula reset)
            async with session.post(f"{BASE_URL}/api/upload-efatura") as resp:
                # Upload vazio deve falhar ou criar sessão vazia
                success = resp.status in [400, 422]  # Esperamos erro por falta de arquivos
                details = "Reset simulado através de tentativa de upload vazio"
                
                results.add_result("Reset Session", success, details)
                return success
        except Exception as e:
            results.add_result("Reset Session", False, str(e))
            return False

async def test_data_persistence():
    """Testa persistência de dados após recarregar"""
    if not TEST_SESSION_ID:
        results.add_result("Data Persistence", False, "Sem session_id")
        return False
    
    async with aiohttp.ClientSession() as session:
        try:
            # Primeira leitura
            async with session.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}") as resp:
                data1 = await resp.json()
            
            # Aguardar um pouco
            await asyncio.sleep(1)
            
            # Segunda leitura
            async with session.get(f"{BASE_URL}/api/session/{TEST_SESSION_ID}") as resp:
                data2 = await resp.json()
            
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

async def test_cors_headers():
    """Testa configuração CORS para frontend"""
    async with aiohttp.ClientSession() as session:
        try:
            headers = {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'POST'
            }
            
            async with session.options(f"{BASE_URL}/api/upload-efatura", headers=headers) as resp:
                cors_headers = resp.headers.get('Access-Control-Allow-Origin', '')
                success = cors_headers in ['*', 'http://localhost:3000']
                
                details = f"CORS Origin: {cors_headers}"
                results.add_result("CORS Configuration", success, details)
                return success
        except Exception as e:
            results.add_result("CORS Configuration", False, str(e))
            return False

async def test_error_handling():
    """Testa tratamento de erros"""
    async with aiohttp.ClientSession() as session:
        tests_passed = 0
        
        # Teste 1: Session ID inválido
        try:
            async with session.get(f"{BASE_URL}/api/session/invalid-session-id") as resp:
                if resp.status == 404:
                    tests_passed += 1
        except:
            pass
        
        # Teste 2: Dados inválidos
        try:
            async with session.post(f"{BASE_URL}/api/calculate", json={"invalid": "data"}) as resp:
                if resp.status in [400, 422]:
                    tests_passed += 1
        except:
            pass
        
        success = tests_passed >= 1
        details = f"{tests_passed}/2 testes de erro passaram"
        results.add_result("Error Handling", success, details)
        return success

async def run_all_tests():
    """Executa todos os testes em paralelo quando possível"""
    print("🚀 Iniciando teste completo do sistema IVA Margem Turismo...")
    print("="*80)
    
    # Testes que devem ser sequenciais
    await test_api_health()
    await test_upload_efatura()
    
    if TEST_SESSION_ID:
        # Testes que podem ser paralelos
        parallel_tests = [
            test_get_session(),
            test_cors_headers(),
            test_error_handling()
        ]
        await asyncio.gather(*parallel_tests)
        
        # Testes que dependem de estado
        await test_manual_association()
        await test_auto_match()
        await test_premium_analytics_suite()
        await test_calculate_and_export()
        await test_data_persistence()
        await test_reset_session()
    
    # Imprimir relatório
    results.print_report()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
