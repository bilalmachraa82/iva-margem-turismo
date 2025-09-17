#!/usr/bin/env python3
"""
Enhanced Test Suite for IVA Margem System
Comprehensive testing with the improved calculator and endpoints
"""
import requests
import json
import tempfile
import csv
from datetime import datetime, timedelta
import random
import sys
import os

# API Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINTS = {
    'health': f"{BASE_URL}/api/health",
    'upload_efatura': f"{BASE_URL}/api/upload-efatura",
    'calculate': f"{BASE_URL}/api/calculate",
    'calculate_enhanced_period': f"{BASE_URL}/api/calculate-enhanced-period",
    'session': f"{BASE_URL}/api/session",
    'mock_data': f"{BASE_URL}/api/mock-data"
}


class EnhancedTestSuite:
    """Comprehensive test suite for IVA Margem system"""

    def __init__(self):
        self.session_id = None
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })

    def test_api_health(self):
        """Test API health endpoint"""
        try:
            response = requests.get(API_ENDPOINTS['health'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log_test("API Health Check", True, f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.log_test("API Health Check", False, f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Health Check", False, str(e))
            return False

    def create_test_data(self):
        """Create comprehensive test data"""
        # Create sales data with different scenarios
        sales_data = []
        costs_data = []

        base_date = datetime.now() - timedelta(days=90)

        # Scenario 1: Normal profitable sales
        for i in range(5):
            date = (base_date + timedelta(days=i*10)).strftime('%d-%m-%Y')
            sales_data.append([
                date, 'FT', f'FT 2025/{i+1}',
                '123456789', f'Cliente {i+1} - Viagem Normal',
                f'{1000 + i*200:.2f}', '23', f'{(1000 + i*200)*0.23:.2f}',
                f'{(1000 + i*200)*1.23:.2f}', 'PT', 'Normal'
            ])

        # Scenario 2: Credit notes (negative amounts)
        sales_data.append([
            (base_date + timedelta(days=50)).strftime('%d-%m-%Y'), 'NC', 'NC 2025/1',
            '234567890', 'Cliente 6 - Cancelamento',
            '-500.00', '23', '-115.00', '-615.00', 'PT', 'Normal'
        ])

        # Scenario 3: High margin sales
        sales_data.append([
            (base_date + timedelta(days=60)).strftime('%d-%m-%Y'), 'FT', 'FT 2025/7',
            '345678901', 'Cliente 7 - Pacote Premium',
            '3000.00', '23', '690.00', '3690.00', 'PT', 'Normal'
        ])

        # Create corresponding costs
        suppliers = [
            ('501234567', 'Hotel Partner', 'Alojamento'),
            ('502345678', 'Airline Company', 'Transporte'),
            ('503456789', 'Transfer Service', 'Transfers'),
            ('504567890', 'Restaurant Chain', 'Restauração')
        ]

        for i in range(15):
            date = (base_date + timedelta(days=i*5)).strftime('%d-%m-%Y')
            supplier_nif, supplier_name, category = random.choice(suppliers)
            base_amount = round(random.uniform(50, 500), 2)
            vat_rate = random.choice([6, 13, 23])
            vat_amount = round(base_amount * vat_rate / 100, 2)
            total = base_amount + vat_amount

            costs_data.append([
                date, 'FT', f'FC-{i+1}/2025',
                supplier_nif, supplier_name,
                f'{base_amount:.2f}', str(vat_rate), f'{vat_amount:.2f}', f'{total:.2f}',
                'PT', 'I - Alojamento, restauração', category, 'Normal'
            ])

        return sales_data, costs_data

    def create_csv_files(self, sales_data, costs_data):
        """Create CSV files for testing"""
        # Create vendas CSV
        vendas_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig')
        writer = csv.writer(vendas_file, delimiter=';')

        # Header for sales
        writer.writerow([
            'Data', 'Tipo de Documento', 'Número de Documento',
            'NIF do Adquirente', 'Nome do Adquirente',
            'Base Tributável', 'Taxa de IVA', 'IVA', 'Total',
            'País', 'Estado do Documento'
        ])

        for row in sales_data:
            writer.writerow(row)
        vendas_file.close()

        # Create compras CSV
        compras_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig')
        writer = csv.writer(compras_file, delimiter=';')

        # Header for costs
        writer.writerow([
            'Data', 'Tipo de Documento', 'Número de Documento',
            'NIF do Fornecedor', 'Nome do Fornecedor',
            'Base Tributável', 'Taxa de IVA', 'IVA', 'Total',
            'País', 'Setor de Atividade', 'Categoria', 'Estado do Documento'
        ])

        for row in costs_data:
            writer.writerow(row)
        compras_file.close()

        return vendas_file.name, compras_file.name

    def test_efatura_upload(self):
        """Test e-Fatura upload functionality"""
        sales_data, costs_data = self.create_test_data()
        vendas_file, compras_file = self.create_csv_files(sales_data, costs_data)

        try:
            with open(vendas_file, 'rb') as vf, open(compras_file, 'rb') as cf:
                files = {
                    'vendas': ('vendas.csv', vf, 'text/csv'),
                    'compras': ('compras.csv', cf, 'text/csv')
                }

                response = requests.post(API_ENDPOINTS['upload_efatura'], files=files)

                if response.status_code == 200:
                    data = response.json()
                    self.session_id = data['session_id']

                    # Validate response structure
                    required_fields = ['session_id', 'sales', 'costs', 'summary']
                    missing_fields = [field for field in required_fields if field not in data]

                    if missing_fields:
                        self.log_test("E-Fatura Upload Structure", False, f"Missing fields: {missing_fields}")
                    else:
                        self.log_test("E-Fatura Upload", True,
                                    f"Session: {self.session_id[:8]}... | Sales: {len(data['sales'])} | Costs: {len(data['costs'])}")

                        # Test data quality
                        if len(data['sales']) == len(sales_data):
                            self.log_test("Sales Data Integrity", True, f"All {len(sales_data)} sales imported")
                        else:
                            self.log_test("Sales Data Integrity", False,
                                        f"Expected {len(sales_data)}, got {len(data['sales'])}")

                        return True
                else:
                    self.log_test("E-Fatura Upload", False, f"HTTP {response.status_code}: {response.text}")
                    return False

        except Exception as e:
            self.log_test("E-Fatura Upload", False, str(e))
            return False
        finally:
            # Cleanup
            os.unlink(vendas_file)
            os.unlink(compras_file)

    def test_enhanced_calculation(self):
        """Test enhanced calculation with corrected VAT formula"""
        if not self.session_id:
            self.log_test("Enhanced Calculation", False, "No session ID available")
            return False

        try:
            # Test standard calculation
            calc_request = {
                "session_id": self.session_id,
                "vat_rate": 23
            }

            response = requests.post(API_ENDPOINTS['calculate'], json=calc_request)

            if response.status_code == 200:
                # Should return Excel file
                if response.headers.get('content-type') == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                    self.log_test("Enhanced Calculation", True,
                                f"Excel generated successfully ({len(response.content)} bytes)")
                    return True
                else:
                    self.log_test("Enhanced Calculation", False,
                                f"Unexpected content type: {response.headers.get('content-type')}")
                    return False
            else:
                self.log_test("Enhanced Calculation", False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test("Enhanced Calculation", False, str(e))
            return False

    def test_period_calculation(self):
        """Test new period calculation feature"""
        if not self.session_id:
            self.log_test("Period Calculation", False, "No session ID available")
            return False

        try:
            period_request = {
                "session_id": self.session_id,
                "vat_rate": 23,
                "period_start": "2025-01-01",
                "period_end": "2025-03-31",
                "start_date": "2025-01-01",
                "end_date": "2025-03-31"
            }

            response = requests.post(API_ENDPOINTS['calculate_enhanced_period'], json=period_request)

            if response.status_code == 200:
                data = response.json()

                # Validate period calculation structure
                if 'period_result' in data and 'summary' in data['period_result']:
                    summary = data['period_result']['summary']

                    # Validate compliance information
                    if summary.get('compliance') == "CIVA Art. 308º - Regime Especial Agências Viagens":
                        self.log_test("Period Calculation", True,
                                    f"Period calculation successful | Margin: €{summary.get('total_gross_margin', 0):.2f}")

                        # Test the corrected VAT formula
                        total_margin = summary.get('total_gross_margin', 0)
                        total_vat = summary.get('total_vat', 0)
                        expected_vat = total_margin * 23 / 100

                        if abs(total_vat - expected_vat) < 0.01:  # Allow for rounding
                            self.log_test("VAT Formula Validation", True,
                                        f"VAT correctly calculated: €{total_vat:.2f}")
                        else:
                            self.log_test("VAT Formula Validation", False,
                                        f"VAT mismatch: expected €{expected_vat:.2f}, got €{total_vat:.2f}")

                        return True
                    else:
                        self.log_test("Period Calculation", False, "Compliance information missing")
                        return False
                else:
                    self.log_test("Period Calculation", False, "Invalid response structure")
                    return False
            else:
                self.log_test("Period Calculation", False, f"HTTP {response.status_code}: {response.text}")
                return False

        except Exception as e:
            self.log_test("Period Calculation", False, str(e))
            return False

    def test_mock_data_consistency(self):
        """Test mock data for consistency with real calculations"""
        try:
            response = requests.post(API_ENDPOINTS['mock_data'])

            if response.status_code == 200:
                data = response.json()
                mock_session_id = data['session_id']

                # Test calculation on mock data
                calc_request = {
                    "session_id": mock_session_id,
                    "vat_rate": 23
                }

                calc_response = requests.post(API_ENDPOINTS['calculate'], json=calc_request)

                if calc_response.status_code == 200:
                    self.log_test("Mock Data Consistency", True,
                                f"Mock data calculation successful (Session: {mock_session_id[:8]}...)")
                    return True
                else:
                    self.log_test("Mock Data Consistency", False,
                                f"Mock calculation failed: {calc_response.status_code}")
                    return False
            else:
                self.log_test("Mock Data Consistency", False, f"Mock data load failed: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Mock Data Consistency", False, str(e))
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Enhanced Test Suite for IVA Margem System")
        print("=" * 60)

        # Test sequence
        tests = [
            ("API Health", self.test_api_health),
            ("E-Fatura Upload", self.test_efatura_upload),
            ("Enhanced Calculation", self.test_enhanced_calculation),
            ("Period Calculation", self.test_period_calculation),
            ("Mock Data Consistency", self.test_mock_data_consistency)
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🧪 Running {test_name}...")
            if test_func():
                passed += 1

        # Summary
        print("\n" + "=" * 60)
        print(f"📊 Test Summary: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! System is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Review the issues above.")
            return False


def main():
    """Main test execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("Enhanced Test Suite for IVA Margem System")
        print("Usage: python test_enhanced_suite.py")
        print("Make sure the backend is running on http://localhost:8000")
        return

    suite = EnhancedTestSuite()
    success = suite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()