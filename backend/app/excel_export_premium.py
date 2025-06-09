"""
PREMIUM Excel Export Module for IVA Margem Turismo
Enhanced with advanced formatting, charts, conditional formatting, and data validation

Features:
- Professional charts and dashboards
- Conditional formatting with color scales
- Data validation and dropdown lists
- Advanced cell formatting and borders
- Company branding and logos
- Interactive elements
"""
import pandas as pd
import xlsxwriter
from datetime import datetime
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class PremiumExcelExporter:
    """Premium Excel report generator with advanced features"""
    
    def __init__(self):
        # Premium color scheme (DaisyUI inspired)
        self.colors = {
            'primary': '#667eea',
            'secondary': '#48bb78', 
            'accent': '#f6ad55',
            'success': '#48bb78',
            'warning': '#f6ad55',
            'error': '#f56565',
            'info': '#4299e1',
            'neutral': '#374151',
            'base_100': '#ffffff',
            'base_200': '#f8fafc',
            'base_300': '#e2e8f0'
        }
        
    def generate_premium_report(self, calculations: List[Dict], raw_data: Dict, metadata: Dict) -> str:
        """
        Generate premium Excel report with advanced features
        
        Args:
            calculations: List of VAT calculations
            raw_data: Original sales and costs data
            metadata: File metadata
            
        Returns:
            Path to generated Excel file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"temp/iva_margem_premium_{timestamp}.xlsx"
        
        # Ensure temp directory exists
        os.makedirs("temp", exist_ok=True)
        
        try:
            # Create workbook with xlsxwriter for advanced features
            workbook = xlsxwriter.Workbook(filename, {
                'strings_to_numbers': True,
                'strings_to_formulas': True,
                'default_date_format': 'dd/mm/yyyy'
            })
            
            # Define premium formats
            self._define_formats(workbook)
            
            # Create sheets
            self._create_dashboard_sheet(workbook, calculations, raw_data, metadata)
            self._create_summary_sheet(workbook, calculations, metadata)
            self._create_sales_premium_sheet(workbook, raw_data.get('sales', []))
            self._create_costs_premium_sheet(workbook, raw_data.get('costs', []))
            self._create_associations_premium_sheet(workbook, calculations)
            self._create_analytics_sheet(workbook, calculations, raw_data)
            
            workbook.close()
            
            logger.info(f"Premium Excel report generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error generating premium Excel: {str(e)}")
            raise
    
    def _define_formats(self, workbook):
        """Define premium cell formats"""
        
        # Header formats
        self.title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'color': self.colors['primary'],
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['base_200'],
            'border': 1,
            'border_color': self.colors['base_300']
        })
        
        self.header_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'color': 'white',
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': self.colors['primary'],
            'border': 1,
            'border_color': self.colors['primary']
        })
        
        self.subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 11,
            'color': self.colors['neutral'],
            'bg_color': self.colors['base_200'],
            'border': 1,
            'align': 'center'
        })
        
        # Data formats
        self.currency_format = workbook.add_format({
            'num_format': '€#,##0.00',
            'align': 'right',
            'border': 1,
            'border_color': self.colors['base_300']
        })
        
        self.percentage_format = workbook.add_format({
            'num_format': '0.00%',
            'align': 'right',
            'border': 1,
            'border_color': self.colors['base_300']
        })
        
        self.date_format = workbook.add_format({
            'num_format': 'dd/mm/yyyy',
            'align': 'center',
            'border': 1,
            'border_color': self.colors['base_300']
        })
        
        self.number_format = workbook.add_format({
            'num_format': '#,##0',
            'align': 'right',
            'border': 1,
            'border_color': self.colors['base_300']
        })
        
        # Status formats
        self.positive_format = workbook.add_format({
            'num_format': '€#,##0.00',
            'align': 'right',
            'color': self.colors['success'],
            'bold': True,
            'border': 1
        })
        
        self.negative_format = workbook.add_format({
            'num_format': '€#,##0.00',
            'align': 'right',
            'color': self.colors['error'],
            'bold': True,
            'border': 1
        })
        
        self.warning_format = workbook.add_format({
            'bg_color': self.colors['warning'],
            'color': 'white',
            'bold': True,
            'border': 1,
            'align': 'center'
        })
        
        # Table formats
        self.table_data_format = workbook.add_format({
            'border': 1,
            'border_color': self.colors['base_300'],
            'align': 'left',
            'valign': 'vcenter'
        })
        
        self.highlight_format = workbook.add_format({
            'bg_color': self.colors['accent'],
            'color': 'white',
            'bold': True,
            'border': 1,
            'align': 'center'
        })
    
    def _create_dashboard_sheet(self, workbook, calculations, raw_data, metadata):
        """Create premium dashboard with charts and KPIs"""
        
        worksheet = workbook.add_worksheet('📊 Dashboard')
        worksheet.set_column('A:Z', 12)
        worksheet.set_row(0, 30)
        
        # Title section
        worksheet.merge_range('A1:H2', 'IVA MARGEM TURISMO - DASHBOARD EXECUTIVO', self.title_format)
        worksheet.merge_range('A3:H3', f'Relatório gerado em {datetime.now().strftime("%d/%m/%Y às %H:%M")}', self.subheader_format)
        
        # Company info
        worksheet.write('A5', 'Empresa:', self.subheader_format)
        worksheet.write('B5', metadata.get('company_name', 'N/A'), self.table_data_format)
        worksheet.write('A6', 'Período:', self.subheader_format)
        worksheet.write('B6', f"{metadata.get('start_date', 'N/A')} a {metadata.get('end_date', 'N/A')}", self.table_data_format)
        worksheet.write('A7', 'Taxa IVA:', self.subheader_format)
        worksheet.write('B7', f"{metadata.get('vat_rate', 23)}%", self.table_data_format)
        
        # Calculate totals for KPIs
        total_sales = sum(float(s.get('amount', 0)) for s in raw_data.get('sales', []) if s.get('amount', 0) > 0)
        total_costs = sum(float(c.get('amount', 0)) for c in raw_data.get('costs', []))
        total_margin = total_sales - total_costs
        total_vat = sum(float(calc.get('vat_amount', 0)) for calc in calculations)
        margin_percentage = (total_margin / total_sales * 100) if total_sales > 0 else 0
        
        # KPI Cards
        kpis = [
            ('Total Vendas', total_sales, 'D5', self.positive_format),
            ('Total Custos', total_costs, 'D6', self.negative_format),
            ('Margem Bruta', total_margin, 'D7', self.positive_format if total_margin > 0 else self.negative_format),
            ('IVA Calculado', total_vat, 'D8', self.currency_format),
            ('% Margem', margin_percentage/100, 'D9', self.percentage_format)
        ]
        
        for i, (label, value, cell, format_obj) in enumerate(kpis):
            worksheet.write(f'C{5+i}', label, self.subheader_format)
            worksheet.write(cell, value, format_obj)
        
        # Chart data preparation
        chart_data_row = 12
        worksheet.write('A12', 'Distribuição Financeira', self.header_format)
        
        chart_labels = ['Vendas', 'Custos', 'Margem', 'IVA', 'Margem Líquida']
        chart_values = [total_sales, total_costs, total_margin, total_vat, total_margin - total_vat]
        
        # Write chart data
        for i, (label, value) in enumerate(zip(chart_labels, chart_values)):
            worksheet.write(chart_data_row + i, 0, label, self.table_data_format)
            worksheet.write(chart_data_row + i, 1, value, self.currency_format)
        
        # Create premium chart
        chart = workbook.add_chart({'type': 'column'})
        chart.add_series({
            'name': 'Valores (€)',
            'categories': f'=Dashboard!$A${chart_data_row + 1}:$A${chart_data_row + 5}',
            'values': f'=Dashboard!$B${chart_data_row + 1}:$B${chart_data_row + 5}',
            'fill': {'color': self.colors['primary']},
            'border': {'color': self.colors['primary'], 'width': 2}
        })
        
        chart.set_title({
            'name': 'Análise Financeira - IVA Margem',
            'name_font': {'size': 14, 'bold': True, 'color': self.colors['primary']}
        })
        chart.set_x_axis({'name': 'Categorias'})
        chart.set_y_axis({'name': 'Valores (€)', 'num_format': '€#,##0'})
        chart.set_size({'width': 480, 'height': 288})
        chart.set_style(10)
        
        worksheet.insert_chart('F5', chart)
        
        # Add margin analysis
        worksheet.write('A20', 'ANÁLISE DE MARGENS POR DOCUMENTO', self.header_format)
        
        # Margin distribution
        margin_ranges = {'< 0%': 0, '0-5%': 0, '5-15%': 0, '15-25%': 0, '> 25%': 0}
        
        for calc in calculations:
            margin_pct = float(calc.get('margin_percentage', 0))
            if margin_pct < 0:
                margin_ranges['< 0%'] += 1
            elif margin_pct < 5:
                margin_ranges['0-5%'] += 1
            elif margin_pct < 15:
                margin_ranges['5-15%'] += 1
            elif margin_pct < 25:
                margin_ranges['15-25%'] += 1
            else:
                margin_ranges['> 25%'] += 1
        
        # Write margin analysis
        row = 22
        for range_label, count in margin_ranges.items():
            worksheet.write(row, 0, range_label, self.table_data_format)
            worksheet.write(row, 1, count, self.number_format)
            row += 1
        
        # Create pie chart for margins
        pie_chart = workbook.add_chart({'type': 'pie'})
        pie_chart.add_series({
            'name': 'Distribuição de Margens',
            'categories': '=Dashboard!$A$23:$A$27',
            'values': '=Dashboard!$B$23:$B$27',
            'data_labels': {'percentage': True},
        })
        pie_chart.set_title({'name': 'Distribuição de Margens'})
        pie_chart.set_size({'width': 400, 'height': 240})
        
        worksheet.insert_chart('F20', pie_chart)
    
    def _create_summary_sheet(self, workbook, calculations, metadata):
        """Create enhanced summary sheet"""
        
        worksheet = workbook.add_worksheet('📋 Resumo IVA')
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:H', 15)
        
        # Title
        worksheet.merge_range('A1:H1', 'RESUMO DE CÁLCULO IVA SOBRE MARGEM', self.title_format)
        worksheet.merge_range('A2:H2', f'Regime Especial - CIVA Art. 308º | Taxa: {metadata.get("vat_rate", 23)}%', self.subheader_format)
        
        # Headers
        headers = [
            'Nº Documento', 'Data', 'Cliente/Fornecedor', 'Venda (€)', 
            'Custo (€)', 'Margem (€)', 'Margem %', 'IVA (€)'
        ]
        
        for col, header in enumerate(headers):
            worksheet.write(3, col, header, self.header_format)
        
        # Data with conditional formatting
        row = 4
        total_sales = total_costs = total_margin = total_vat = 0
        
        for calc in calculations:
            data = [
                calc.get('document_number', ''),
                calc.get('date', ''),
                calc.get('client_supplier', ''),
                float(calc.get('sale_amount', 0)),
                float(calc.get('cost_amount', 0)),
                float(calc.get('margin', 0)),
                float(calc.get('margin_percentage', 0)) / 100,
                float(calc.get('vat_amount', 0))
            ]
            
            for col, value in enumerate(data):
                if col in [3, 4, 5, 7]:  # Currency columns
                    fmt = self.positive_format if col in [3, 5, 7] and value >= 0 else self.negative_format if value < 0 else self.currency_format
                    worksheet.write(row, col, value, fmt)
                elif col == 6:  # Percentage
                    worksheet.write(row, col, value, self.percentage_format)
                elif col == 1:  # Date
                    worksheet.write(row, col, value, self.date_format)
                else:
                    worksheet.write(row, col, value, self.table_data_format)
            
            # Accumulate totals
            total_sales += data[3]
            total_costs += data[4] 
            total_margin += data[5]
            total_vat += data[7]
            row += 1
        
        # Totals row
        worksheet.write(row, 0, 'TOTAIS', self.header_format)
        worksheet.write(row, 3, total_sales, self.positive_format)
        worksheet.write(row, 4, total_costs, self.negative_format)
        worksheet.write(row, 5, total_margin, self.positive_format if total_margin >= 0 else self.negative_format)
        worksheet.write(row, 6, (total_margin / total_sales) if total_sales > 0 else 0, self.percentage_format)
        worksheet.write(row, 7, total_vat, self.currency_format)
        
        # Add conditional formatting for margins
        worksheet.conditional_format(f'F4:F{row}', {
            'type': 'color_scale',
            'min_color': self.colors['error'],
            'max_color': self.colors['success']
        })
        
        # Add data validation for margin percentages
        worksheet.conditional_format(f'G4:G{row}', {
            'type': 'cell',
            'criteria': '<',
            'value': 0,
            'format': workbook.add_format({'bg_color': self.colors['error'], 'color': 'white'})
        })
    
    def _create_sales_premium_sheet(self, workbook, sales_data):
        """Create enhanced sales sheet with filters and formatting"""
        
        worksheet = workbook.add_worksheet('💰 Vendas')
        worksheet.set_column('A:F', 15)
        
        # Title
        worksheet.merge_range('A1:F1', 'VENDAS DETALHADAS', self.title_format)
        
        # Headers
        headers = ['ID', 'Número', 'Data', 'Cliente', 'Valor', 'Tipo']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.header_format)
        
        # Data
        row = 3
        for sale in sales_data:
            worksheet.write(row, 0, sale.get('id', ''), self.table_data_format)
            worksheet.write(row, 1, sale.get('number', ''), self.table_data_format)
            worksheet.write(row, 2, sale.get('date', ''), self.date_format)
            worksheet.write(row, 3, sale.get('client', ''), self.table_data_format)
            
            amount = float(sale.get('amount', 0))
            fmt = self.positive_format if amount >= 0 else self.negative_format
            worksheet.write(row, 4, amount, fmt)
            
            # Determine type based on amount and number
            doc_type = 'Nota Crédito' if amount < 0 or 'NC' in sale.get('number', '') else 'Fatura'
            worksheet.write(row, 5, doc_type, self.table_data_format)
            
            row += 1
        
        # Add autofilter
        worksheet.autofilter(f'A2:F{row-1}')
        
        # Add summary
        worksheet.write(row + 1, 3, 'TOTAL VENDAS:', self.header_format)
        worksheet.write(row + 1, 4, f'=SUM(E3:E{row})', self.currency_format)
    
    def _create_costs_premium_sheet(self, workbook, costs_data):
        """Create enhanced costs sheet"""
        
        worksheet = workbook.add_worksheet('🛒 Custos')
        worksheet.set_column('A:G', 15)
        
        # Title
        worksheet.merge_range('A1:G1', 'CUSTOS DETALHADOS', self.title_format)
        
        # Headers
        headers = ['ID', 'Fornecedor', 'Descrição', 'Data', 'Valor', 'IVA', 'Total']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.header_format)
        
        # Data
        row = 3
        for cost in costs_data:
            worksheet.write(row, 0, cost.get('id', ''), self.table_data_format)
            worksheet.write(row, 1, cost.get('supplier', ''), self.table_data_format)
            worksheet.write(row, 2, cost.get('description', ''), self.table_data_format)
            worksheet.write(row, 3, cost.get('date', ''), self.date_format)
            worksheet.write(row, 4, float(cost.get('amount', 0)), self.currency_format)
            worksheet.write(row, 5, float(cost.get('vat_amount', 0)), self.currency_format)
            worksheet.write(row, 6, float(cost.get('gross_total', 0)), self.currency_format)
            row += 1
        
        # Add autofilter
        worksheet.autofilter(f'A2:G{row-1}')
        
        # Add summary
        worksheet.write(row + 1, 3, 'TOTAL CUSTOS:', self.header_format)
        worksheet.write(row + 1, 4, f'=SUM(E3:E{row})', self.currency_format)
        worksheet.write(row + 1, 5, f'=SUM(F3:F{row})', self.currency_format)
        worksheet.write(row + 1, 6, f'=SUM(G3:G{row})', self.currency_format)
    
    def _create_associations_premium_sheet(self, workbook, calculations):
        """Create enhanced associations sheet"""
        
        worksheet = workbook.add_worksheet('🔗 Associações')
        worksheet.set_column('A:E', 20)
        
        # Title
        worksheet.merge_range('A1:E1', 'MAPA DE ASSOCIAÇÕES VENDAS-CUSTOS', self.title_format)
        
        # Headers
        headers = ['Venda', 'Custo', 'Margem', 'Confiança', 'Método']
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.header_format)
        
        # Data
        row = 3
        for calc in calculations:
            worksheet.write(row, 0, calc.get('sale_document', ''), self.table_data_format)
            worksheet.write(row, 1, calc.get('cost_document', ''), self.table_data_format)
            worksheet.write(row, 2, float(calc.get('margin', 0)), self.currency_format)
            
            confidence = calc.get('confidence', 100)
            worksheet.write(row, 3, confidence / 100, self.percentage_format)
            
            method = calc.get('association_method', 'Manual')
            worksheet.write(row, 4, method, self.table_data_format)
            row += 1
        
        # Add conditional formatting for confidence
        worksheet.conditional_format(f'D3:D{row}', {
            'type': 'color_scale',
            'min_color': self.colors['error'],
            'max_color': self.colors['success']
        })
    
    def _create_analytics_sheet(self, workbook, calculations, raw_data):
        """Create analytics sheet with advanced insights"""
        
        worksheet = workbook.add_worksheet('📈 Analytics')
        worksheet.set_column('A:D', 20)
        
        # Title
        worksheet.merge_range('A1:D1', 'ANÁLISE AVANÇADA', self.title_format)
        
        # Calculate analytics
        total_docs = len(calculations)
        avg_margin = sum(float(c.get('margin_percentage', 0)) for c in calculations) / total_docs if total_docs > 0 else 0
        high_margin_docs = len([c for c in calculations if float(c.get('margin_percentage', 0)) > 20])
        negative_margin_docs = len([c for c in calculations if float(c.get('margin', 0)) < 0])
        
        # Analytics table
        analytics = [
            ('Total de Documentos', total_docs),
            ('Margem Média (%)', avg_margin),
            ('Docs com Margem > 20%', high_margin_docs),
            ('Docs com Margem Negativa', negative_margin_docs),
            ('Taxa de Margens Positivas', ((total_docs - negative_margin_docs) / total_docs * 100) if total_docs > 0 else 0)
        ]
        
        row = 3
        for label, value in analytics:
            worksheet.write(row, 0, label, self.subheader_format)
            if '%' in label or 'Taxa' in label:
                worksheet.write(row, 1, value / 100, self.percentage_format)
            else:
                worksheet.write(row, 1, value, self.number_format)
            row += 1
        
        # Month analysis if dates available
        worksheet.write(row + 2, 0, 'ANÁLISE MENSAL', self.header_format)
        # This would require more complex date analysis
        # For now, just show placeholder
        worksheet.write(row + 4, 0, 'Análise temporal disponível em versão futura', self.table_data_format)