"""
SAF-T XML Parser for Portuguese tax files
Supports multiple namespaces and document types
"""
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import hashlib
import re
import logging

logger = logging.getLogger(__name__)


class SAFTParser:
    """Parser for SAF-T (Standard Audit File for Tax) XML files"""
    
    def __init__(self):
        # Common namespaces in Portuguese SAF-T files
        self.namespaces = {
            'saft': 'urn:OECD:StandardAuditFile-Tax:PT_1.04_01',
            'saftpt': 'urn:OECD:StandardAuditFile-Tax:PT_1.04_01',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        # Track parsing errors and warnings
        self.parsing_errors = []
        self.parsing_warnings = []
        
    def parse(self, xml_content: bytes) -> Dict:
        """
        Parse SAF-T XML content and extract sales and costs
        
        Args:
            xml_content: XML file content as bytes
            
        Returns:
            Dictionary with sales, costs, metadata, errors and warnings
        """
        # Reset error tracking for new parse
        self.parsing_errors = []
        self.parsing_warnings = []
        
        try:
            # Parse XML
            root = ET.fromstring(xml_content)
            
            # Detect actual namespace
            ns = self._detect_namespace(root)
            
            # Extract data
            metadata = self._extract_metadata(root, ns)
            sales = self._extract_sales(root, ns)
            costs = self._extract_costs(root, ns)
            
            # Add parsing statistics
            total_docs = len(sales) + len(costs)
            if total_docs == 0:
                self.parsing_warnings.append("Nenhum documento encontrado no ficheiro SAF-T")
            
            logger.info(f"Parsed SAF-T: {len(sales)} sales, {len(costs)} costs, {len(self.parsing_errors)} errors, {len(self.parsing_warnings)} warnings")
            
            return {
                "sales": sales,
                "costs": costs,
                "metadata": metadata,
                "parsing_errors": self.parsing_errors,
                "parsing_warnings": self.parsing_warnings
            }
            
        except ET.ParseError as e:
            logger.error(f"XML Parse error: {str(e)}")
            raise ValueError(f"Invalid XML file: {str(e)}")
        except Exception as e:
            logger.error(f"SAF-T parse error: {str(e)}")
            raise Exception(f"Error processing SAF-T file: {str(e)}")
    
    def _detect_namespace(self, root: ET.Element) -> Dict[str, str]:
        """Detect the actual namespace used in the XML"""
        # Check root tag for namespace
        if root.tag.startswith("{"):
            ns_url = root.tag.split("}")[0][1:]
            return {'saft': ns_url}
        
        # Check for xmlns attributes
        for attr, value in root.attrib.items():
            if attr == 'xmlns' or attr.endswith('xmlns'):
                return {'saft': value}
                
        # Return default
        return self.namespaces
    
    def _extract_metadata(self, root: ET.Element, ns: Dict[str, str]) -> Dict:
        """Extract file metadata from Header section"""
        metadata = {}
        
        header = self._find_element(root, ['Header', 'saft:Header'], ns)
        if header is not None:
            metadata['company_name'] = self._get_text(header, ['CompanyName', 'saft:CompanyName'], ns, "")
            metadata['tax_registration'] = self._get_text(header, ['TaxRegistrationNumber', 'saft:TaxRegistrationNumber'], ns, "")
            metadata['start_date'] = self._get_text(header, ['StartDate', 'saft:StartDate'], ns, "")
            metadata['end_date'] = self._get_text(header, ['EndDate', 'saft:EndDate'], ns, "")
            metadata['currency'] = self._get_text(header, ['CurrencyCode', 'saft:CurrencyCode'], ns, "EUR")
            metadata['date_created'] = self._get_text(header, ['DateCreated', 'saft:DateCreated'], ns, "")
            metadata['software_name'] = self._get_text(header, ['SoftwareCompanyName', 'saft:SoftwareCompanyName'], ns, "")
            metadata['software_version'] = self._get_text(header, ['SoftwareVersion', 'saft:SoftwareVersion'], ns, "")
            
        return metadata
    
    def _extract_sales(self, root: ET.Element, ns: Dict[str, str]) -> List[Dict]:
        """Extract sales invoices from the SAF-T file"""
        sales = []
        
        # Try multiple paths for invoices
        invoice_paths = [
            './/saft:SourceDocuments/saft:SalesInvoices/saft:Invoice',
            './/SourceDocuments/SalesInvoices/Invoice',
            './/saft:SalesInvoices/saft:Invoice',
            './/SalesInvoices/Invoice'
        ]
        
        invoices = []
        for path in invoice_paths:
            invoices = self._find_all_elements(root, path, ns)
            if invoices:
                break
                
        for invoice in invoices:
            try:
                sale = self._parse_invoice(invoice, ns, root)
                if sale:
                    sales.append(sale)
            except Exception as e:
                invoice_no = self._get_text(invoice, ['InvoiceNo', 'saft:InvoiceNo'], ns, 'Unknown')
                error_msg = f"Erro ao processar fatura {invoice_no}: {str(e)}"
                self.parsing_errors.append(error_msg)
                logger.warning(error_msg)
                continue
                
        return sales
    
    def _parse_invoice(self, invoice: ET.Element, ns: Dict[str, str], root: ET.Element) -> Optional[Dict]:
        """Parse a single invoice element"""
        # Extract basic fields
        invoice_no = self._get_text(invoice, ['InvoiceNo', 'saft:InvoiceNo'], ns)
        if not invoice_no:
            return None
            
        invoice_date = self._get_text(invoice, ['InvoiceDate', 'saft:InvoiceDate'], ns, "")
        invoice_type = self._get_text(invoice, ['InvoiceType', 'saft:InvoiceType'], ns, "FT")
        customer_id = self._get_text(invoice, ['CustomerID', 'saft:CustomerID'], ns, "")
        
        # Extract totals
        totals = self._find_element(invoice, ['DocumentTotals', 'saft:DocumentTotals'], ns)
        if totals is not None:
            gross_total = float(self._get_text(totals, ['GrossTotal', 'saft:GrossTotal'], ns, "0"))
            net_total = float(self._get_text(totals, ['NetTotal', 'saft:NetTotal'], ns, "0"))
            tax_payable = float(self._get_text(totals, ['TaxPayable', 'saft:TaxPayable'], ns, "0"))
        else:
            # Try to calculate from lines
            net_total, tax_payable = self._calculate_from_lines(invoice, ns)
            gross_total = net_total + tax_payable
        
        # Get customer name
        customer_name = self._get_customer_name(root, customer_id, ns)
        
        # Validate important fields
        if not invoice_date:
            self.parsing_warnings.append(f"Fatura {invoice_no} sem data")
        if not customer_id and not customer_name:
            self.parsing_warnings.append(f"Fatura {invoice_no} sem identificação de cliente")
        if net_total == 0:
            self.parsing_warnings.append(f"Fatura {invoice_no} com valor zero")
            
        # Generate unique ID
        sale_id = hashlib.md5(f"{invoice_no}_{invoice_date}".encode()).hexdigest()[:8]
        
        return {
            "id": sale_id,
            "number": invoice_no,
            "date": invoice_date,
            "client": customer_name,
            "amount": round(net_total, 2),
            "vat_amount": round(tax_payable, 2),
            "gross_total": round(gross_total, 2),
            "invoice_type": invoice_type,
            "linked_costs": []
        }
    
    def _extract_costs(self, root: ET.Element, ns: Dict[str, str]) -> List[Dict]:
        """Extract cost documents from various sources in SAF-T"""
        costs = []
        
        # Multiple document types can represent costs
        document_configs = [
            # Movement of Goods (stock movements)
            {
                'paths': ['.//saft:SourceDocuments/saft:MovementOfGoods/saft:StockMovement',
                         './/SourceDocuments/MovementOfGoods/StockMovement'],
                'number_fields': ['DocumentNumber', 'saft:DocumentNumber'],
                'date_fields': ['MovementDate', 'saft:MovementDate'],
                'type': 'movement'
            },
            # Working Documents
            {
                'paths': ['.//saft:SourceDocuments/saft:WorkingDocuments/saft:WorkDocument',
                         './/SourceDocuments/WorkingDocuments/WorkDocument'],
                'number_fields': ['DocumentNumber', 'saft:DocumentNumber'],
                'date_fields': ['WorkDate', 'saft:WorkDate'],
                'type': 'work'
            },
            # Payments
            {
                'paths': ['.//saft:SourceDocuments/saft:Payments/saft:Payment',
                         './/SourceDocuments/Payments/Payment'],
                'number_fields': ['PaymentRefNo', 'saft:PaymentRefNo'],
                'date_fields': ['TransactionDate', 'saft:TransactionDate'],
                'type': 'payment'
            }
        ]
        
        for config in document_configs:
            documents = []
            for path in config['paths']:
                documents = self._find_all_elements(root, path, ns)
                if documents:
                    break
                    
            for doc in documents:
                try:
                    cost = self._parse_cost_document(doc, ns, config, root)
                    if cost and cost['amount'] > 0:
                        costs.append(cost)
                    elif cost and cost['amount'] == 0:
                        doc_no = self._get_text(doc, config['number_fields'], ns, 'Unknown')
                        self.parsing_warnings.append(f"Custo {doc_no} com valor zero ignorado")
                except Exception as e:
                    doc_no = self._get_text(doc, config['number_fields'], ns, 'Unknown')
                    error_msg = f"Erro ao processar documento de custo {doc_no}: {str(e)}"
                    self.parsing_errors.append(error_msg)
                    logger.warning(error_msg)
                    continue
                    
        return costs
    
    def _parse_cost_document(self, doc: ET.Element, ns: Dict[str, str], config: Dict, root: ET.Element) -> Optional[Dict]:
        """Parse a cost document based on its type"""
        # Get document number
        doc_no = self._get_text(doc, config['number_fields'], ns)
        if not doc_no:
            return None
            
        # Get date
        doc_date = self._get_text(doc, config['date_fields'], ns, "")
        
        # Get supplier/entity
        supplier_id = self._get_text(doc, ['SupplierID', 'saft:SupplierID', 'CustomerID', 'saft:CustomerID'], ns, "")
        supplier_name = self._get_supplier_name(root, supplier_id, ns)
        
        # Get amounts based on document type
        if config['type'] == 'payment':
            # For payments, use PaymentAmount
            total = float(self._get_text(doc, ['PaymentAmount', 'saft:PaymentAmount'], ns, "0"))
            vat = 0  # Payments usually don't separate VAT
        else:
            # For other documents, look for totals
            totals = self._find_element(doc, ['DocumentTotals', 'saft:DocumentTotals'], ns)
            if totals:
                total = float(self._get_text(totals, ['GrossTotal', 'saft:GrossTotal'], ns, "0"))
                vat = float(self._get_text(totals, ['TaxPayable', 'saft:TaxPayable'], ns, "0"))
            else:
                # Try to get from lines
                total, vat = self._calculate_from_lines(doc, ns)
        
        # Get description
        description = self._extract_description(doc, ns)
        
        # Generate unique ID
        cost_id = hashlib.md5(f"{doc_no}_{doc_date}_{total}".encode()).hexdigest()[:8]
        
        return {
            "id": cost_id,
            "supplier": supplier_name,
            "description": description,
            "date": doc_date,
            "amount": round(total - vat, 2),
            "vat_amount": round(vat, 2),
            "gross_total": round(total, 2),
            "document_number": doc_no,
            "document_type": config['type'],
            "linked_sales": []
        }
    
    def _calculate_from_lines(self, element: ET.Element, ns: Dict[str, str]) -> Tuple[float, float]:
        """Calculate totals from document lines"""
        net_total = 0
        tax_total = 0
        
        lines = self._find_all_elements(element, ['Line', 'saft:Line'], ns)
        for line in lines:
            # Get quantity and unit price
            quantity = float(self._get_text(line, ['Quantity', 'saft:Quantity'], ns, "1"))
            unit_price = float(self._get_text(line, ['UnitPrice', 'saft:UnitPrice'], ns, "0"))
            
            # Calculate line total
            line_net = quantity * unit_price
            net_total += line_net
            
            # Get tax
            tax_percentage = float(self._get_text(line, ['.//TaxPercentage', './/saft:TaxPercentage'], ns, "0"))
            if tax_percentage > 0:
                tax_total += line_net * (tax_percentage / 100)
                
        return net_total, tax_total
    
    def _extract_description(self, doc: ET.Element, ns: Dict[str, str]) -> str:
        """Extract description from document"""
        # Try various description fields
        description = self._get_text(doc, [
            'MovementComments', 'saft:MovementComments',
            'Description', 'saft:Description',
            'Remarks', 'saft:Remarks'
        ], ns, "")
        
        # If no description at document level, try first line
        if not description:
            first_line = self._find_element(doc, ['Line', 'saft:Line'], ns)
            if first_line:
                description = self._get_text(first_line, ['Description', 'saft:Description'], ns, "")
                
        return description[:100] if description else "Sem descrição"
    
    def _get_customer_name(self, root: ET.Element, customer_id: str, ns: Dict[str, str]) -> str:
        """Get customer name by ID"""
        if not customer_id:
            return "Cliente Desconhecido"
            
        # Try to find customer in MasterFiles
        customer_paths = [
            f'.//saft:MasterFiles/saft:Customer[saft:CustomerID="{customer_id}"]',
            f'.//MasterFiles/Customer[CustomerID="{customer_id}"]'
        ]
        
        for path in customer_paths:
            customer = self._find_element(root, path, ns)
            if customer:
                name = self._get_text(customer, ['CompanyName', 'saft:CompanyName'], ns)
                if name:
                    return name
                    
        return f"Cliente {customer_id}"
    
    def _get_supplier_name(self, root: ET.Element, supplier_id: str, ns: Dict[str, str]) -> str:
        """Get supplier name by ID"""
        if not supplier_id:
            return "Fornecedor Desconhecido"
            
        # Try to find supplier in MasterFiles
        supplier_paths = [
            f'.//saft:MasterFiles/saft:Supplier[saft:SupplierID="{supplier_id}"]',
            f'.//MasterFiles/Supplier[SupplierID="{supplier_id}"]'
        ]
        
        for path in supplier_paths:
            supplier = self._find_element(root, path, ns)
            if supplier:
                name = self._get_text(supplier, ['CompanyName', 'saft:CompanyName'], ns)
                if name:
                    return name
                    
        # Also check in customers (some systems mix them)
        customer_name = self._get_customer_name(root, supplier_id, ns)
        if not customer_name.startswith("Cliente"):
            return customer_name
            
        return f"Fornecedor {supplier_id}"
    
    def _find_element(self, parent: ET.Element, paths: List[str], ns: Dict[str, str]) -> Optional[ET.Element]:
        """Find first matching element from multiple possible paths"""
        for path in paths:
            try:
                # Try with namespace
                elem = parent.find(path, ns)
                if elem is not None:
                    return elem
                # Try without namespace
                elem = parent.find(path.replace('saft:', ''))
                if elem is not None:
                    return elem
            except:
                pass
        return None
    
    def _find_all_elements(self, parent: ET.Element, path: str, ns: Dict[str, str]) -> List[ET.Element]:
        """Find all matching elements"""
        elements = []
        try:
            # Try with namespace
            elements = parent.findall(path, ns)
            if not elements:
                # Try without namespace
                elements = parent.findall(path.replace('saft:', ''))
        except:
            pass
        return elements
    
    def _get_text(self, element: Optional[ET.Element], paths: List[str], ns: Dict[str, str], default: str = "") -> str:
        """Get text content from element trying multiple paths"""
        if element is None:
            return default
            
        elem = self._find_element(element, paths, ns)
        if elem is not None and elem.text:
            return elem.text.strip()
            
        return default