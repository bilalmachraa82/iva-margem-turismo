"""
Excel export module for IVA Margem calculations
Generates professional multi-sheet Excel reports
"""
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict, Optional
from openpyxl import load_workbook
from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
import logging

logger = logging.getLogger(__name__)


class ExcelExporter:
    """Professional Excel report generator"""
    
    def __init__(self):
        # Define styles
        self.header_fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
        self.header_font = Font(bold=True, color="FFFFFF", size=12)
        self.title_font = Font(bold=True, size=14)
        self.subtitle_font = Font(bold=True, size=11, color="666666")
        
        # Alternating row colors
        self.row_fill_1 = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")
        self.row_fill_2 = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        
        # Borders
        self.thin_border = Border(
            left=Side(style='thin', color='DDDDDD'),
            right=Side(style='thin', color='DDDDDD'),
            top=Side(style='thin', color='DDDDDD'),
            bottom=Side(style='thin', color='DDDDDD')
        )
        
        self.thick_border = Border(
            left=Side(style='medium'),
            right=Side(style='medium'),
            top=Side(style='medium'),
            bottom=Side(style='medium')
        )
        
    def generate(self, calculations: List[Dict], raw_data: Dict, metadata: Dict) -> str:
        """
        Generate complete Excel report
        
        Args:
            calculations: List of VAT calculations
            raw_data: Original sales and costs data
            metadata: File metadata
            
        Returns:
            Path to generated Excel file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"temp/iva_margem_{timestamp}.xlsx"
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        try:
            # Create Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 1. Summary sheet (main calculations)
                self._create_summary_sheet(writer, calculations, metadata)
                
                # 2. Sales sheet
                self._create_sales_sheet(writer, raw_data.get('sales', []))
                
                # 3. Costs sheet
                self._create_costs_sheet(writer, raw_data.get('costs', []))
                
                # 4. Associations sheet
                self._create_associations_sheet(writer, calculations)
                
                # 5. Totals and statistics sheet
                self._create_totals_sheet(writer, calculations, metadata)
                
            # Apply formatting
            self._apply_formatting(filename)
            
            logger.info(f"Excel report generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating Excel: {str(e)}")
            raise
    
    def _create_summary_sheet(self, writer, calculations: List[Dict], metadata: Dict):
        """Create main summary sheet with VAT calculations"""
        
        # Prepare data
        summary_data = []
        for calc in calculations:
            summary_data.append({
                'Nº Documento': calc['invoice_number'],
                'Tipo': calc['invoice_type'],
                'Data': calc['date'],
                'Cliente': calc['client'],
                'Total PVP (€)': calc['sale_amount'],
                'Total Custos (€)': calc['total_allocated_costs'],
                'Margem Bruta (€)': calc['gross_margin'],
                'Taxa IVA (%)': calc['vat_rate'],
                'IVA Margem (€)': calc['vat_amount'],
                'Margem Líquida (€)': calc['net_margin'],
                'Margem (%)': calc['margin_percentage'],
                'Nº Custos': calc['cost_count']
            })
        
        # Create DataFrame and write to Excel
        df = pd.DataFrame(summary_data)
        df.to_excel(writer, sheet_name='Resumo IVA Margem', index=False, startrow=3)
        
        # Get worksheet
        worksheet = writer.sheets['Resumo IVA Margem']
        
        # Add title
        worksheet['A1'] = 'Relatório IVA de Margem - Agência de Viagens'
        worksheet['A1'].font = self.title_font
        worksheet['A2'] = f"Período: {metadata.get('start_date', '')} a {metadata.get('end_date', '')}"
        worksheet['A2'].font = self.subtitle_font
        
    def _create_sales_sheet(self, writer, sales: List[Dict]):
        """Create sales detail sheet"""
        
        sales_data = []
        for sale in sales:
            sales_data.append({
                'ID': sale['id'],
                'Nº Fatura': sale['number'],
                'Data': sale['date'],
                'Cliente': sale['client'],
                'Valor s/ IVA (€)': sale.get('amount', 0),
                'IVA (€)': sale.get('vat_amount', 0),
                'Total c/ IVA (€)': sale.get('gross_total', sale.get('amount', 0)),
                'Custos Associados': len(sale.get('linked_costs', [])),
                'IDs Custos': ', '.join(sale.get('linked_costs', []))
            })
        
        df = pd.DataFrame(sales_data)
        df.to_excel(writer, sheet_name='Vendas Detalhadas', index=False, startrow=2)
        
        worksheet = writer.sheets['Vendas Detalhadas']
        worksheet['A1'] = 'Listagem de Vendas'
        worksheet['A1'].font = self.title_font
        
    def _create_costs_sheet(self, writer, costs: List[Dict]):
        """Create costs detail sheet"""
        
        costs_data = []
        for cost in costs:
            costs_data.append({
                'ID': cost['id'],
                'Fornecedor': cost['supplier'],
                'Descrição': cost['description'],
                'Data': cost['date'],
                'Nº Documento': cost.get('document_number', ''),
                'Valor s/ IVA (€)': cost.get('amount', 0),
                'IVA (€)': cost.get('vat_amount', 0),
                'Total c/ IVA (€)': cost.get('gross_total', cost.get('amount', 0)),
                'Vendas Associadas': len(cost.get('linked_sales', [])),
                'IDs Vendas': ', '.join(cost.get('linked_sales', []))
            })
        
        df = pd.DataFrame(costs_data)
        df.to_excel(writer, sheet_name='Custos Detalhados', index=False, startrow=2)
        
        worksheet = writer.sheets['Custos Detalhados']
        worksheet['A1'] = 'Listagem de Custos'
        worksheet['A1'].font = self.title_font
        
    def _create_associations_sheet(self, writer, calculations: List[Dict]):
        """Create detailed associations sheet"""
        
        associations_data = []
        for calc in calculations:
            for cost_detail in calc.get('linked_costs', []):
                associations_data.append({
                    'Fatura': calc['invoice_number'],
                    'Cliente': calc['client'],
                    'Fornecedor': cost_detail['supplier'],
                    'Descrição Custo': cost_detail['description'],
                    'Data Custo': cost_detail.get('date', ''),
                    'Custo Total (€)': cost_detail['total_amount'],
                    'Custo Alocado (€)': cost_detail['allocated_amount'],
                    'Partilhado com': f"{cost_detail['shared_with']} venda(s)",
                    'Percentagem Alocada': round((cost_detail['allocated_amount'] / cost_detail['total_amount'] * 100) if cost_detail['total_amount'] > 0 else 0, 1)
                })
        
        if associations_data:
            df = pd.DataFrame(associations_data)
            df.to_excel(writer, sheet_name='Associações Detalhadas', index=False, startrow=2)
            
            worksheet = writer.sheets['Associações Detalhadas']
            worksheet['A1'] = 'Mapa de Associações Vendas-Custos'
            worksheet['A1'].font = self.title_font
            
    def _create_totals_sheet(self, writer, calculations: List[Dict], metadata: Dict):
        """Create totals and statistics sheet"""
        
        # Calculate totals
        from .calculator import VATCalculator
        calculator = VATCalculator()
        summary = calculator.calculate_summary(calculations)
        
        # Prepare summary data
        totals_data = [
            {'': 'TOTAIS GERAIS', 'Valor': ''},
            {'': 'Total Vendas (s/ IVA)', 'Valor': f"€ {summary['total_sales']:,.2f}"},
            {'': 'Total Custos', 'Valor': f"€ {summary['total_costs']:,.2f}"},
            {'': 'Margem Bruta Total', 'Valor': f"€ {summary['total_gross_margin']:,.2f}"},
            {'': 'IVA da Margem Total', 'Valor': f"€ {summary['total_vat']:,.2f}"},
            {'': 'Margem Líquida Total', 'Valor': f"€ {summary['total_net_margin']:,.2f}"},
            {'': '', 'Valor': ''},
            {'': 'ESTATÍSTICAS', 'Valor': ''},
            {'': 'Nº Total Documentos', 'Valor': summary['documents_processed']},
            {'': 'Documentos com Lucro', 'Valor': summary['documents_with_margin']},
            {'': 'Documentos com Prejuízo', 'Valor': summary['documents_with_loss']},
            {'': 'Margem Média (%)', 'Valor': f"{summary['average_margin_percentage']}%"},
            {'': '', 'Valor': ''},
            {'': 'INFORMAÇÕES DO FICHEIRO', 'Valor': ''},
            {'': 'Empresa', 'Valor': metadata.get('company_name', '')},
            {'': 'NIF', 'Valor': metadata.get('tax_registration', '')},
            {'': 'Período', 'Valor': f"{metadata.get('start_date', '')} a {metadata.get('end_date', '')}"},
            {'': 'Moeda', 'Valor': metadata.get('currency', 'EUR')},
            {'': 'Taxa IVA Aplicada', 'Valor': f"{metadata.get('vat_rate', 23)}%"},
            {'': 'Data Cálculo', 'Valor': metadata.get('calculation_date', datetime.now().strftime('%Y-%m-%d %H:%M'))},
            {'': '', 'Valor': ''},
            {'': 'POR TIPO DE DOCUMENTO', 'Valor': ''}
        ]
        
        # Add breakdown by document type
        for doc_type, type_data in summary['by_type'].items():
            totals_data.append({
                '': f"{doc_type} ({type_data['count']} docs)",
                'Valor': f"€ {type_data['total_sales']:,.2f}"
            })
            
        df = pd.DataFrame(totals_data)
        df.to_excel(writer, sheet_name='Totais e Estatísticas', index=False, startrow=2, header=False)
        
        worksheet = writer.sheets['Totais e Estatísticas']
        worksheet['A1'] = 'Resumo e Estatísticas'
        worksheet['A1'].font = self.title_font
        
    def _apply_formatting(self, filename: str):
        """Apply professional formatting to all sheets"""
        
        wb = load_workbook(filename)
        
        for sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            
            # Format headers (skip sheets without headers)
            if sheet_name != 'Totais e Estatísticas':
                # Find header row (usually row 4 for summary, row 3 for others)
                header_row = 4 if sheet_name == 'Resumo IVA Margem' else 3
                
                # Apply header formatting
                for cell in ws[header_row]:
                    if cell.value:
                        cell.fill = self.header_fill
                        cell.font = self.header_font
                        cell.alignment = Alignment(horizontal='center', vertical='center')
                        cell.border = self.thin_border
                
                # Apply alternating row colors
                for row_num in range(header_row + 1, ws.max_row + 1):
                    fill = self.row_fill_1 if (row_num - header_row) % 2 == 1 else self.row_fill_2
                    for cell in ws[row_num]:
                        if cell.value is not None:
                            cell.fill = fill
                            cell.border = self.thin_border
                            
                            # Format numbers
                            if isinstance(cell.value, (int, float)) and cell.column > 1:
                                if '€' in str(ws.cell(header_row, cell.column).value):
                                    cell.number_format = '#,##0.00 €'
                                elif '%' in str(ws.cell(header_row, cell.column).value):
                                    cell.number_format = '0.00%'
                                    
                # Add autofilter
                if ws.max_row > header_row:
                    ws.auto_filter.ref = f"A{header_row}:{get_column_letter(ws.max_column)}{ws.max_row}"
                    
            # Adjust column widths
            for column in ws.columns:
                max_length = 0
                column_letter = get_column_letter(column[0].column)
                
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                        
                adjusted_width = min(max_length + 2, 50)
                ws.column_dimensions[column_letter].width = adjusted_width
                
            # Freeze panes
            if sheet_name == 'Resumo IVA Margem':
                ws.freeze_panes = 'A5'
            elif sheet_name != 'Totais e Estatísticas':
                ws.freeze_panes = 'A4'
                
        # Add footer to all sheets
        for sheet in wb.worksheets:
            sheet.oddFooter.center.text = "Powered by Accounting Advantage - &D &T"
            sheet.oddFooter.center.size = 8
            sheet.oddFooter.center.font = "Arial,Italic"
            
        # Save formatted workbook
        wb.save(filename)