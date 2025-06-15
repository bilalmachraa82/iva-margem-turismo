"""
E-Fatura CSV Parser for IVA Margem Turismo
Handles both sales (vendas) and purchases (compras) CSV files from Portal das Finanças
"""
import csv
import uuid
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class EFaturaParser:
    """Parser for e-Fatura CSV files (vendas and compras)"""
    
    # Column mappings for e-Fatura CSV files
    VENDAS_COLUMNS = {
        'Data': 'date',
        'Tipo de Documento': 'doc_type',
        'Número de Documento': 'doc_number',
        'NIF do Adquirente': 'client_nif',
        'Nome do Adquirente': 'client_name',
        'Base Tributável': 'base_amount',
        'Taxa de IVA': 'vat_rate',
        'IVA': 'vat_amount',
        'Total': 'total_amount',
        'País': 'country',
        'Estado do Documento': 'status'
    }
    
    COMPRAS_COLUMNS = {
        'Data': 'date',
        'Tipo de Documento': 'doc_type',
        'Número de Documento': 'doc_number',
        'NIF do Fornecedor': 'supplier_nif',
        'Nome do Fornecedor': 'supplier_name',
        'Base Tributável': 'base_amount',
        'Taxa de IVA': 'vat_rate',
        'IVA': 'vat_amount',
        'Total': 'total_amount',
        'País': 'country',
        'Setor de Atividade': 'activity_sector',
        'Categoria': 'category',
        'Estado do Documento': 'status'
    }
    
    @staticmethod
    def parse(vendas_content: bytes, compras_content: bytes) -> Dict[str, Any]:
        """
        Parse both e-Fatura CSV files (vendas and compras)
        
        Args:
            vendas_content: Content of vendas CSV file
            compras_content: Content of compras CSV file
            
        Returns:
            Dictionary with parsed sales, costs and metadata
        """
        result = {
            "sales": [],
            "costs": [],
            "metadata": {
                "source": "e-Fatura CSV",
                "parsed_at": datetime.now().isoformat(),
                "company_info": {}
            },
            "parsing_errors": [],
            "parsing_warnings": []
        }
        
        try:
            # Parse vendas (sales)
            sales_data, sales_errors = EFaturaParser._parse_vendas_csv(vendas_content)
            result["sales"] = sales_data
            result["parsing_errors"].extend(sales_errors)
            
            # Parse compras (costs)
            costs_data, costs_errors = EFaturaParser._parse_compras_csv(compras_content)
            result["costs"] = costs_data
            result["parsing_errors"].extend(costs_errors)
            
            # Add summary
            result["metadata"]["summary"] = {
                "total_sales": len(result["sales"]),
                "total_costs": len(result["costs"]),
                "sales_amount": sum(s.get("amount", 0) for s in result["sales"]),
                "costs_amount": sum(c.get("amount", 0) for c in result["costs"])
            }
            
        except Exception as e:
            logger.error(f"Error parsing e-Fatura files: {str(e)}")
            result["parsing_errors"].append(f"Fatal error: {str(e)}")
            
        return result
    
    @staticmethod
    def _parse_vendas_csv(content: bytes) -> Tuple[List[Dict], List[str]]:
        """Parse vendas CSV file"""
        sales = []
        errors = []
        
        try:
            # Decode content - e-Fatura uses UTF-8 with BOM
            text_content = content.decode('utf-8-sig')
            lines = text_content.splitlines()
            
            if not lines:
                errors.append("Vendas CSV is empty")
                return sales, errors
            
            # Parse CSV
            reader = csv.DictReader(lines, delimiter=';')
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    sale = EFaturaParser._parse_venda_row(row, row_num)
                    if sale:
                        sales.append(sale)
                except Exception as e:
                    errors.append(f"Error parsing vendas row {row_num}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Error reading vendas CSV: {str(e)}")
            
        return sales, errors
    
    @staticmethod
    def _parse_venda_row(row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """Parse a single venda (sale) row"""
        # Generate unique ID
        sale_id = f"s_{uuid.uuid4().hex[:8]}"
        
        # Parse amounts
        base_amount = EFaturaParser._parse_amount(row.get('Base Tributável', '0'))
        vat_amount = EFaturaParser._parse_amount(row.get('IVA', '0'))
        total_amount = EFaturaParser._parse_amount(row.get('Total', '0'))
        
        # Parse date
        date_str = EFaturaParser._parse_date(row.get('Data', ''))
        
        # Build sale object
        sale = {
            "id": sale_id,
            "number": row.get('Número de Documento', f'DOC_{row_num}'),
            "date": date_str,
            "client": row.get('Nome do Adquirente', 'Unknown'),
            "client_nif": row.get('NIF do Adquirente', ''),
            "amount": base_amount,
            "vat_amount": vat_amount,
            "gross_total": total_amount,
            "doc_type": row.get('Tipo de Documento', ''),
            "country": row.get('País', 'PT'),
            "status": row.get('Estado do Documento', ''),
            "linked_costs": []
        }
        
        return sale
    
    @staticmethod
    def _parse_compras_csv(content: bytes) -> Tuple[List[Dict], List[str]]:
        """Parse compras CSV file"""
        costs = []
        errors = []
        
        try:
            # Decode content - e-Fatura uses UTF-8 with BOM
            text_content = content.decode('utf-8-sig')
            lines = text_content.splitlines()
            
            if not lines:
                errors.append("Compras CSV is empty")
                return costs, errors
            
            # Parse CSV
            reader = csv.DictReader(lines, delimiter=';')
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    cost = EFaturaParser._parse_compra_row(row, row_num)
                    if cost:
                        costs.append(cost)
                except Exception as e:
                    errors.append(f"Error parsing compras row {row_num}: {str(e)}")
                    
        except Exception as e:
            errors.append(f"Error reading compras CSV: {str(e)}")
            
        return costs, errors
    
    @staticmethod
    def _parse_compra_row(row: Dict[str, str], row_num: int) -> Dict[str, Any]:
        """Parse a single compra (cost) row"""
        # Generate unique ID
        cost_id = f"c_{uuid.uuid4().hex[:8]}"
        
        # Parse amounts
        base_amount = EFaturaParser._parse_amount(row.get('Base Tributável', '0'))
        vat_amount = EFaturaParser._parse_amount(row.get('IVA', '0'))
        total_amount = EFaturaParser._parse_amount(row.get('Total', '0'))
        
        # Parse date
        date_str = EFaturaParser._parse_date(row.get('Data', ''))
        
        # Build description
        description = f"{row.get('Categoria', 'N/A')} - {row.get('Setor de Atividade', 'N/A')}"
        
        # Build cost object
        cost = {
            "id": cost_id,
            "supplier": row.get('Nome do Fornecedor', 'Unknown'),
            "supplier_nif": row.get('NIF do Fornecedor', ''),
            "description": description,
            "date": date_str,
            "amount": base_amount,
            "vat_amount": vat_amount,
            "gross_total": total_amount,
            "document_number": row.get('Número de Documento', f'DOC_{row_num}'),
            "doc_type": row.get('Tipo de Documento', ''),
            "category": row.get('Categoria', ''),
            "activity_sector": row.get('Setor de Atividade', ''),
            "country": row.get('País', 'PT'),
            "status": row.get('Estado do Documento', ''),
            "linked_sales": []
        }
        
        return cost
    
    @staticmethod
    def _parse_amount(amount_str: str) -> float:
        """Parse amount string to float"""
        if not amount_str:
            return 0.0
            
        # Remove currency symbols and spaces
        cleaned = amount_str.replace('€', '').replace(' ', '').strip()
        
        # Handle Portuguese decimal format (1.234,56)
        if ',' in cleaned and '.' in cleaned:
            # Portuguese format: dots for thousands, comma for decimal
            cleaned = cleaned.replace('.', '').replace(',', '.')
        elif ',' in cleaned:
            # Just comma for decimal
            cleaned = cleaned.replace(',', '.')
            
        try:
            return float(cleaned)
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return 0.0
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Parse date string to ISO format"""
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
            
        # Try common date formats
        formats = [
            '%d-%m-%Y',  # DD-MM-YYYY
            '%d/%m/%Y',  # DD/MM/YYYY
            '%Y-%m-%d',  # YYYY-MM-DD (already ISO)
            '%d.%m.%Y',  # DD.MM.YYYY
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        logger.warning(f"Could not parse date: {date_str}")
        return datetime.now().strftime('%Y-%m-%d')