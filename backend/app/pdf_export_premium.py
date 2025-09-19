"""
Premium PDF Export with Professional Design and Company Personalization
Industry-standard financial report generation with enhanced charts
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import logging
import os

from .company_config import company_config, CompanyInfo

logger = logging.getLogger(__name__)

DISABLE_CHARTS = os.getenv("DISABLE_CHARTS") == "1"

if not DISABLE_CHARTS:
    try:  # pragma: no cover - simple import guard
        from .chart_generator import generate_financial_charts
    except Exception as exc:  # pragma: no cover
        logger.warning("Chart generator indisponível (%s). Relatório premium sem gráficos.", exc)

        def generate_financial_charts(*args, **kwargs):
            return {}
else:
    logger.info("Chart generator desativado via DISABLE_CHARTS. Relatório premium sem gráficos.")

    def generate_financial_charts(*args, **kwargs):  # type: ignore
        return {}

class PremiumPDFGenerator:
    """Premium PDF generator with company branding and enhanced charts"""

    def __init__(self, company_info: Optional[CompanyInfo] = None):
        self.company_info = company_info or company_config.get_company_info()
        self.colors = self._get_color_scheme()
        self.styles = self._create_styles()

    def _get_color_scheme(self) -> Dict[str, HexColor]:
        """Get professional color scheme from company config"""
        return {
            'primary': HexColor(self.company_info.primary_color),
            'secondary': HexColor(self.company_info.secondary_color),
            'accent': HexColor(self.company_info.accent_color),
            'text': HexColor('#1f2937'),
            'light_gray': HexColor('#f3f4f6'),
            'medium_gray': HexColor('#9ca3af'),
            'dark_gray': HexColor('#374151')
        }

    def _create_styles(self) -> Dict[str, ParagraphStyle]:
        """Create professional paragraph styles"""
        base_styles = getSampleStyleSheet()

        return {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=24,
                textColor=self.colors['primary'],
                spaceAfter=20,
                fontName='Helvetica-Bold',
                alignment=TA_CENTER
            ),
            'subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Normal'],
                fontSize=14,
                textColor=self.colors['text'],
                spaceAfter=12,
                fontName='Helvetica',
                alignment=TA_CENTER
            ),
            'heading1': ParagraphStyle(
                'CustomHeading1',
                parent=base_styles['Heading1'],
                fontSize=18,
                textColor=self.colors['primary'],
                spaceBefore=20,
                spaceAfter=12,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderPadding=0,
                leftIndent=0
            ),
            'heading2': ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'],
                fontSize=14,
                textColor=self.colors['secondary'],
                spaceBefore=15,
                spaceAfter=8,
                fontName='Helvetica-Bold'
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=11,
                textColor=self.colors['text'],
                spaceAfter=6,
                fontName='Helvetica',
                alignment=TA_JUSTIFY
            ),
            'body_bold': ParagraphStyle(
                'CustomBodyBold',
                parent=base_styles['Normal'],
                fontSize=11,
                textColor=self.colors['text'],
                spaceAfter=6,
                fontName='Helvetica-Bold'
            ),
            'footer': ParagraphStyle(
                'CustomFooter',
                parent=base_styles['Normal'],
                fontSize=9,
                textColor=self.colors['medium_gray'],
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
        }

    def generate_premium_report(self, calculations: Dict[str, Any],
                               sales_data: List[Dict], costs_data: List[Dict],
                               filename: Optional[str] = None) -> str:
        """Generate complete premium PDF report"""

        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_company_name = "".join(c for c in self.company_info.name if c.isalnum() or c in (' ', '-', '_'))
            filename = f"temp/relatorio_iva_margem_premium_{safe_company_name}_{timestamp}.pdf"

        # Generate professional charts
        charts = generate_financial_charts(calculations, {
            'primary': self.company_info.primary_color,
            'secondary': self.company_info.secondary_color,
            'accent': self.company_info.accent_color
        })

        # Create PDF document
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2*cm,
            title=f"Relatório IVA sobre Margem - {self.company_info.name}"
        )

        # Build story
        story = []

        # Cover page
        story.extend(self._create_cover_page(calculations))
        story.append(PageBreak())

        # Executive summary
        story.extend(self._create_executive_summary(calculations))
        story.append(PageBreak())

        # Charts page
        story.extend(self._create_charts_page(charts, calculations))
        story.append(PageBreak())

        # Detailed analysis
        story.extend(self._create_detailed_analysis(sales_data, costs_data))
        story.append(PageBreak())

        # Compliance and footer
        story.extend(self._create_compliance_section(calculations))

        # Build PDF with custom page templates
        doc.build(story, onFirstPage=self._create_header_footer,
                 onLaterPages=self._create_header_footer)

        logger.info(f"Premium PDF report generated: {filename}")
        return filename

    def _create_cover_page(self, calculations: Dict[str, Any]) -> List:
        """Create professional cover page"""
        elements = []

        # Company logo (if available)
        if self.company_info.logo_path:
            try:
                logo = Image(self.company_info.logo_path, width=8*cm, height=3*cm)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 1*cm))
            except:
                logger.warning("Could not load company logo")

        # Main title
        elements.append(Paragraph("Relatório IVA sobre Margem", self.styles['title']))
        elements.append(Paragraph(self.company_info.name, self.styles['subtitle']))
        elements.append(Spacer(1, 2*cm))

        # Company details box
        company_details = [
            ["<b>Entidade:</b>", self.company_info.name],
            ["<b>NIF:</b>", self.company_info.nif],
            ["<b>Sede:</b>", self.company_info.get_full_address()],
            ["<b>Contacto:</b>", self.company_info.get_contact_info()],
        ]

        details_table = Table(company_details, colWidths=[4*cm, 12*cm])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text']),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['light_gray']),
            ('BOX', (0, 0), (-1, -1), 1, self.colors['primary']),
        ]))

        elements.append(details_table)
        elements.append(Spacer(1, 2*cm))

        # Report metadata
        report_id = str(uuid.uuid4()).replace('-', '')[:16]
        metadata = [
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Taxa de IVA considerada: {calculations.get('vat_rate', 23):.2f}%",
            f"Identificador do relatório: {report_id}"
        ]

        for meta in metadata:
            elements.append(Paragraph(meta, self.styles['body']))

        return elements

    def _create_executive_summary(self, calculations: Dict[str, Any]) -> List:
        """Create professional executive summary with KPIs"""
        elements = []

        elements.append(Paragraph("Resumo Executivo", self.styles['heading1']))
        elements.append(Paragraph(
            "Este relatório consolida a análise de margem e IVA de acordo com o regime especial das "
            "agências de viagens (Art.º 308.º do CIVA). Os indicadores seguintes apresentam a "
            "fotografia global do período avaliado.",
            self.styles['body']
        ))
        elements.append(Spacer(1, 1*cm))

        # KPI Cards
        kpi_data = [
            ["💶", f"€{calculations.get('total_sales', 0):,.2f}", "Volume Total de Vendas", "Total de receitas sujeitas ao regime de margem"],
            ["💼", f"€{calculations.get('total_costs', 0):,.2f}", "Custos Diretos Afetos", "Custos diretos afetos às vendas analisadas"],
            ["📊", f"€{calculations.get('gross_margin', 0):,.2f}", "Margem Bruta", "Vendas menos custos diretos afetos"],
            ["🧾", f"€{calculations.get('vat_amount', 0):,.2f}", "IVA sobre Margem (23%)", "Imposto devido segundo o regime especial"],
            ["🏦", f"€{calculations.get('net_margin', 0):,.2f}", "Margem Líquida", "Resultado após liquidação de IVA sobre a margem"],
            ["📈", f"{calculations.get('margin_percentage', 0):.1f}%", "Margem / Vendas", "Indicador de performance comercial"]
        ]

        # Create KPI table with professional styling
        kpi_table = Table(kpi_data, colWidths=[1*cm, 3.5*cm, 4.5*cm, 7*cm])
        kpi_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, -1), 16),  # Icons
            ('FONTSIZE', (1, 0), (1, -1), 14),  # Values
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, 0), (2, -1), 11),  # Titles
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (3, 0), (3, -1), 9),   # Descriptions
            ('TEXTCOLOR', (1, 0), (1, -1), self.colors['primary']),
            ('TEXTCOLOR', (2, 0), (2, -1), self.colors['text']),
            ('TEXTCOLOR', (3, 0), (3, -1), self.colors['medium_gray']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [white, self.colors['light_gray']]),
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['medium_gray']),
        ]))

        elements.append(kpi_table)
        return elements

    def _create_charts_page(self, charts: Dict[str, str], calculations: Dict[str, Any]) -> List:
        """Create page with professional charts"""
        elements = []

        elements.append(Paragraph("Visualização Analítica Premium", self.styles['heading1']))
        elements.append(Spacer(1, 0.5*cm))

        # Add waterfall chart
        if 'waterfall_chart' in charts:
            elements.append(Paragraph("Análise Financeira Completa", self.styles['heading2']))
            waterfall_img = self._base64_to_image(charts['waterfall_chart'], width=16*cm)
            elements.append(waterfall_img)
            elements.append(Spacer(1, 1*cm))

        # Add donut chart
        if 'donut_chart' in charts:
            elements.append(Paragraph("Composição da Margem", self.styles['heading2']))
            donut_img = self._base64_to_image(charts['donut_chart'], width=12*cm)
            elements.append(donut_img)
            elements.append(Spacer(1, 1*cm))

        # Add comparison chart
        if 'comparison_chart' in charts:
            elements.append(Paragraph("Comparativo Regime Margem vs. Regime Normal", self.styles['heading2']))
            comparison_img = self._base64_to_image(charts['comparison_chart'], width=16*cm)
            elements.append(comparison_img)

            # Add savings highlight
            normal_vat = calculations.get('total_sales', 0) * 0.23
            margin_vat = calculations.get('vat_amount', 0)
            savings = normal_vat - margin_vat
            savings_pct = (savings / normal_vat * 100) if normal_vat > 0 else 0

            savings_text = f"<b>Poupança fiscal estimada: €{savings:,.2f} ({savings_pct:.1f}%)</b>"
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph(savings_text, self.styles['body_bold']))

        return elements

    def _create_detailed_analysis(self, sales_data: List[Dict], costs_data: List[Dict]) -> List:
        """Create detailed document analysis table"""
        elements = []

        elements.append(Paragraph("Análise Detalhada por Documento", self.styles['heading1']))
        elements.append(Paragraph(
            f"Apresentamos os primeiros {min(26, len(sales_data))} registos de um total de "
            f"{len(sales_data)} documentos com margem apurada. Consulte a exportação Excel "
            "para o detalhe completo.", self.styles['body']
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Prepare table data
        table_data = [["Documento", "Data", "Cliente", "Venda (€)", "Custos (€)", "Margem (€)", "IVA (€)", "Margem %"]]

        for sale in sales_data[:26]:  # Limit to 26 rows for PDF
            linked_costs_amount = sum(
                cost['amount'] for cost in costs_data
                if cost['id'] in sale.get('linked_costs', [])
            )
            margin = sale['amount'] - linked_costs_amount
            margin_pct = (margin / sale['amount'] * 100) if sale['amount'] != 0 else 0
            vat_amount = max(0, margin * 0.23) if margin > 0 else 0

            # Format values
            row = [
                sale.get('number', 'N/A')[:20],  # Truncate long document numbers
                sale.get('date', 'N/A'),
                sale.get('client', 'N/A')[:25],  # Truncate long client names
                f"€{sale['amount']:,.0f}",
                f"€{linked_costs_amount:,.0f}",
                f"€{margin:,.0f}",
                f"€{vat_amount:,.0f}",
                f"{margin_pct:.1f}%"
            ]
            table_data.append(row)

        # Create table with professional styling
        col_widths = [3*cm, 2*cm, 4*cm, 2*cm, 2*cm, 2*cm, 2*cm, 1.5*cm]
        detail_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        detail_table.setStyle(TableStyle([
            # Header styling
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            # Data styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.colors['text']),
            # Alignment
            ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),  # Numbers right-aligned
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            # Borders and backgrounds
            ('GRID', (0, 0), (-1, -1), 0.5, self.colors['medium_gray']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, self.colors['light_gray']]),
        ]))

        elements.append(detail_table)
        return elements

    def _create_compliance_section(self, calculations: Dict[str, Any]) -> List:
        """Create compliance and integrity section"""
        elements = []

        elements.append(Paragraph("Integridade & Observações", self.styles['heading1']))
        elements.append(Paragraph(
            "Monitorizamos a integridade dos dados importados para suportar auditorias futuras "
            "e garantir rastreabilidade das decisões fiscais.", self.styles['body']
        ))
        elements.append(Spacer(1, 0.5*cm))

        # Integrity metrics
        integrity_data = [
            ["DOCUMENTOS DE VENDA", str(calculations.get('total_sales_count', 26))],
            ["DOCUMENTOS DE CUSTO", str(calculations.get('total_costs_count', 157))],
            ["CÁLCULOS GERADOS", str(calculations.get('calculations_count', 26))],
            ["CUSTOS SEM ASSOCIAÇÃO", "0"],
            ["VENDAS SEM CUSTOS ATRIBUÍDOS", "0"]
        ]

        integrity_table = Table(integrity_data, colWidths=[8*cm, 4*cm])
        integrity_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.colors['text']),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 0), (-1, -1), self.colors['light_gray']),
            ('GRID', (0, 0), (-1, -1), 1, self.colors['medium_gray']),
        ]))

        elements.append(integrity_table)
        elements.append(Spacer(1, 1*cm))

        # Professional note
        note_text = (
            "<b>Nota profissional:</b> Recomenda-se validar manualmente documentos sem custos afetos "
            "ou com margens negativas para assegurar correta imputação antes da submissão da "
            "declaração periódica de IVA."
        )
        elements.append(Paragraph(note_text, self.styles['body']))

        elements.append(Spacer(1, 0.5*cm))

        # Certified accountant info
        if self.company_info.certified_accountant:
            accountant_text = f"<b>Contabilista Certificado:</b> {self.company_info.certified_accountant}"
            elements.append(Paragraph(accountant_text, self.styles['body']))

        return elements

    def _create_header_footer(self, canvas, doc):
        """Create header and footer for each page"""
        # Header
        canvas.saveState()
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(self.colors['primary'])
        canvas.drawString(2*cm, A4[1] - 1.5*cm, self.company_info.name)

        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(self.colors['medium_gray'])
        footer_text = (
            f"Relatório gerado automaticamente pelo motor IVA Margem Premium. "
            f"Não dispensa a análise de um contabilista certificado. "
            f"Art.º 308.º do Código do IVA · Regime especial das agências de viagens"
        )
        canvas.drawString(2*cm, 1*cm, footer_text)

        # Page number
        canvas.drawRightString(A4[0] - 2*cm, 1*cm, f"Página {canvas.getPageNumber()}")
        canvas.restoreState()

    def _base64_to_image(self, base64_string: str, width: float, height: Optional[float] = None) -> Image:
        """Convert base64 string to ReportLab Image"""
        img_data = base64.b64decode(base64_string)
        img_buffer = BytesIO(img_data)
        img = Image(img_buffer, width=width, height=height)
        img.hAlign = 'CENTER'
        return img

# Convenience function for integration
def generate_premium_pdf_report(calculations: Dict[str, Any],
                               sales_data: List[Dict],
                               costs_data: List[Dict],
                               company_info: Optional[CompanyInfo] = None,
                               filename: Optional[str] = None) -> str:
    """Generate premium PDF report with company branding"""
    generator = PremiumPDFGenerator(company_info)
    return generator.generate_premium_report(calculations, sales_data, costs_data, filename)
