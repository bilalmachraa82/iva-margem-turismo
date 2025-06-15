#!/usr/bin/env python3
"""
Test script for e-Fatura endpoint
Creates sample CSV files and tests the upload endpoint
"""
import requests
import tempfile
import csv
from datetime import datetime, timedelta
import random

# API endpoint
API_URL = "http://localhost:8000/api/upload-efatura"

def create_sample_vendas_csv():
    """Create a sample vendas CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Header (Portuguese e-Fatura format)
        writer.writerow([
            'Data', 'Tipo de Documento', 'Número de Documento', 
            'NIF do Adquirente', 'Nome do Adquirente', 
            'Base Tributável', 'Taxa de IVA', 'IVA', 'Total',
            'País', 'Estado do Documento'
        ])
        
        # Sample sales data
        base_date = datetime.now() - timedelta(days=30)
        clients = [
            ('123456789', 'João Silva - Viagem Paris'),
            ('234567890', 'Maria Santos - Pacote Roma'),
            ('345678901', 'Pedro Costa - Cruzeiro Mediterrâneo'),
            ('456789012', 'Ana Rodrigues - Safari África')
        ]
        
        for i in range(10):
            date = (base_date + timedelta(days=i*3)).strftime('%d-%m-%Y')
            client_nif, client_name = random.choice(clients)
            base_amount = round(random.uniform(500, 3000), 2)
            vat_rate = 23
            vat_amount = round(base_amount * vat_rate / 100, 2)
            total = base_amount + vat_amount
            
            writer.writerow([
                date, 'FT', f'FT 2025/{i+1}',
                client_nif, client_name,
                f'{base_amount:.2f}', str(vat_rate), f'{vat_amount:.2f}', f'{total:.2f}',
                'PT', 'Normal'
            ])
        
        return f.name

def create_sample_compras_csv():
    """Create a sample compras CSV file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        
        # Header (Portuguese e-Fatura format)
        writer.writerow([
            'Data', 'Tipo de Documento', 'Número de Documento',
            'NIF do Fornecedor', 'Nome do Fornecedor',
            'Base Tributável', 'Taxa de IVA', 'IVA', 'Total',
            'País', 'Setor de Atividade', 'Categoria', 'Estado do Documento'
        ])
        
        # Sample cost data
        base_date = datetime.now() - timedelta(days=35)
        suppliers = [
            ('501234567', 'Hotel Paris Luxe', 'Alojamento'),
            ('502345678', 'Voos Europa SA', 'Transporte'),
            ('503456789', 'Restaurante Roma', 'Restauração'),
            ('504567890', 'Transfers & Tours', 'Outros serviços')
        ]
        
        for i in range(20):
            date = (base_date + timedelta(days=i*2)).strftime('%d-%m-%Y')
            supplier_nif, supplier_name, category = random.choice(suppliers)
            base_amount = round(random.uniform(100, 800), 2)
            vat_rate = random.choice([6, 13, 23])
            vat_amount = round(base_amount * vat_rate / 100, 2)
            total = base_amount + vat_amount
            
            writer.writerow([
                date, 'FT', f'FT-{i+1}/2025',
                supplier_nif, supplier_name,
                f'{base_amount:.2f}', str(vat_rate), f'{vat_amount:.2f}', f'{total:.2f}',
                'PT', 'I - Alojamento, restauração e similares', category, 'Normal'
            ])
        
        return f.name

def test_efatura_upload():
    """Test the e-Fatura upload endpoint"""
    print("🧪 Testing e-Fatura Upload Endpoint")
    print("=" * 50)
    
    # Create sample files
    print("📝 Creating sample CSV files...")
    vendas_file = create_sample_vendas_csv()
    compras_file = create_sample_compras_csv()
    
    print(f"✅ Created vendas file: {vendas_file}")
    print(f"✅ Created compras file: {compras_file}")
    
    # Prepare files for upload
    with open(vendas_file, 'rb') as vf, open(compras_file, 'rb') as cf:
        files = {
            'vendas': ('vendas.csv', vf, 'text/csv'),
            'compras': ('compras.csv', cf, 'text/csv')
        }
        
        print("\n📤 Uploading files to API...")
        try:
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ Upload successful!")
                print(f"📊 Session ID: {data['session_id']}")
                print(f"💰 Total Sales: {data['summary']['total_sales']} (€{data['summary']['sales_amount']:.2f})")
                print(f"💸 Total Costs: {data['summary']['total_costs']} (€{data['summary']['costs_amount']:.2f})")
                
                if data['summary']['total_errors'] > 0:
                    print(f"\n⚠️  Errors: {data['summary']['total_errors']}")
                    for error in data['summary']['errors']:
                        print(f"   - {error}")
                
                if data['summary']['total_warnings'] > 0:
                    print(f"\n⚠️  Warnings: {data['summary']['total_warnings']}")
                    for warning in data['summary']['warnings']:
                        print(f"   - {warning}")
                
                # Show sample data
                print("\n📋 Sample Sales:")
                for sale in data['sales'][:3]:
                    print(f"   - {sale['number']} | {sale['client']} | €{sale['amount']:.2f}")
                
                print("\n📋 Sample Costs:")
                for cost in data['costs'][:3]:
                    print(f"   - {cost['document_number']} | {cost['supplier']} | €{cost['amount']:.2f}")
                
            else:
                print(f"\n❌ Upload failed with status {response.status_code}")
                print(f"Error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("\n❌ Could not connect to API. Make sure the backend is running.")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    
    # Clean up
    import os
    os.unlink(vendas_file)
    os.unlink(compras_file)
    print("\n🧹 Cleaned up temporary files")

if __name__ == "__main__":
    test_efatura_upload()