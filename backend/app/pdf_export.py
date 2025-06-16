"""
PDF Export module for IVA Margem Turismo
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
import io
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """Generate professional PDF reports for IVA Margem Turismo"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoStyle',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#6b7280'),
            alignment=TA_LEFT
        ))
        
        # Number style
        self.styles.add(ParagraphStyle(
            name='NumberStyle',
            parent=self.styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            alignment=TA_RIGHT,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, session_data: Dict[str, Any], calculation_results: List[Dict], 
                       vat_rate: float, final_results: Dict[str, float]) -> bytes:
        """Generate PDF report"""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Header
        story.extend(self._create_header())
        
        # Summary section
        story.extend(self._create_summary_section(final_results, vat_rate))
        
        # Charts section
        story.extend(self._create_charts_section(final_results))
        
        # Detailed results table
        story.append(PageBreak())
        story.extend(self._create_detailed_results(calculation_results))
        
        # Footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _create_header(self) -> List:
        """Create report header"""
        elements = []
        
        # Title
        elements.append(Paragraph(
            "Relatório IVA sobre Margem - Regime Especial",
            self.styles['CustomTitle']
        ))
        
        # Subtitle with date
        elements.append(Paragraph(
            f"Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}",
            self.styles['InfoStyle']
        ))
        
        elements.append(Spacer(1, 20))
        
        # Legal reference
        elements.append(Paragraph(
            "<b>Base Legal:</b> Artigo 308º do CIVA - Regime especial das agências de viagens",
            self.styles['InfoStyle']
        ))
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_summary_section(self, results: Dict[str, float], vat_rate: float) -> List:
        """Create summary section with key metrics"""
        elements = []
        
        elements.append(Paragraph("Resumo Executivo", self.styles['CustomSubtitle']))
        
        # Create summary table
        summary_data = [
            ['Métrica', 'Valor (€)'],
            ['Total de Vendas', f"{results.get('totalSales', 0):,.2f}"],
            ['Total de Custos Associados', f"{results.get('totalCosts', 0):,.2f}"],
            ['Margem Bruta', f"{results.get('grossMargin', 0):,.2f}"],
            [f'IVA sobre Margem ({vat_rate}%)', f"{results.get('totalVAT', 0):,.2f}"],
            ['Margem Líquida', f"{results.get('netMargin', 0):,.2f}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            
            # Highlight total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#eff6ff')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 30))
        
        # Savings calculation
        normal_vat = results.get('totalSales', 0) * vat_rate / 100
        savings = normal_vat - results.get('totalVAT', 0)
        
        elements.append(Paragraph("Análise de Poupança", self.styles['CustomSubtitle']))
        elements.append(Paragraph(
            f"<b>IVA no regime normal:</b> €{normal_vat:,.2f}<br/>"
            f"<b>IVA no regime de margem:</b> €{results.get('totalVAT', 0):,.2f}<br/>"
            f"<b>Poupança fiscal:</b> <font color='green'>€{savings:,.2f}</font>",
            self.styles['Normal']
        ))
        
        elements.append(Spacer(1, 40))
        
        return elements
    
    def _create_charts_section(self, results: Dict[str, float]) -> List:
        """Create charts section"""
        elements = []
        
        elements.append(Paragraph("Análise Gráfica", self.styles['CustomSubtitle']))
        
        # Create bar chart
        drawing = Drawing(400, 200)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 125
        bc.width = 300
        bc.data = [[
            results.get('totalSales', 0),
            results.get('totalCosts', 0),
            results.get('grossMargin', 0),
            results.get('totalVAT', 0),
            results.get('netMargin', 0)
        ]]
        bc.categoryAxis.categoryNames = ['Vendas', 'Custos', 'M. Bruta', 'IVA', 'M. Líquida']
        bc.valueAxis.valueMin = 0
        bc.valueAxis.valueMax = max(results.get('totalSales', 0) * 1.1, 1000)
        bc.bars[0].fillColor = colors.HexColor('#3b82f6')
        
        drawing.add(bc)
        elements.append(drawing)
        
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _create_detailed_results(self, calculation_results: List[Dict]) -> List:
        """Create detailed results table"""
        elements = []
        
        elements.append(Paragraph("Detalhes por Documento", self.styles['CustomSubtitle']))
        
        # Table headers
        headers = ['Documento', 'Cliente', 'Venda (€)', 'Custos (€)', 'Margem (€)', 'IVA (€)']
        
        # Prepare data
        data = [headers]
        for result in calculation_results[:20]:  # Limit to first 20 for PDF size
            data.append([
                result.get('invoice_number', ''),
                result.get('client', '')[:30],  # Truncate long names
                f"{result.get('sale_amount', 0):,.2f}",
                f"{result.get('total_allocated_costs', 0):,.2f}",
                f"{result.get('gross_margin', 0):,.2f}",
                f"{result.get('vat_amount', 0):,.2f}"
            ])
        
        # Create table
        detail_table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        detail_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            
            # Alternate row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        
        elements.append(detail_table)
        
        if len(calculation_results) > 20:
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(
                f"<i>Nota: Apresentados os primeiros 20 de {len(calculation_results)} documentos. "
                f"Consulte o ficheiro Excel para a lista completa.</i>",
                self.styles['InfoStyle']
            ))
        
        return elements
    
    def _create_footer(self) -> List:
        """Create report footer"""
        elements = []
        
        elements.append(Spacer(1, 40))
        
        # Line separator
        drawing = Drawing(400, 1)
        line = Line(0, 0, 400, 0)
        line.strokeColor = colors.HexColor('#e5e7eb')
        drawing.add(line)
        elements.append(drawing)
        
        elements.append(Spacer(1, 20))
        
        # Footer text
        elements.append(Paragraph(
            "<b>Accounting Advantage</b><br/>"
            "Sistema Profissional de Cálculo de IVA sobre Margem<br/>"
            "Este relatório foi gerado automaticamente e não substitui aconselhamento fiscal profissional.",
            ParagraphStyle(
                name='FooterStyle',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.HexColor('#6b7280'),
                alignment=TA_CENTER
            )
        ))
        
        return elements


def generate_pdf_report(session_data: Dict[str, Any], calculation_results: List[Dict], 
                       vat_rate: float, final_results: Dict[str, float]) -> bytes:
    """Generate PDF report for IVA Margem calculations"""
    try:
        generator = PDFReportGenerator()
        return generator.generate_report(session_data, calculation_results, vat_rate, final_results)
    except Exception as e:
        logger.error(f"Error generating PDF report: {str(e)}")
        raise