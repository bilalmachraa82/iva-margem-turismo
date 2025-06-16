"""
Simple PDF Export module for IVA Margem Turismo
Uses HTML with inline SVG charts for better visualization
"""
import io
import math
from datetime import datetime
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def generate_bar_chart_svg(data: Dict[str, float]) -> str:
    """Generate SVG bar chart"""
    values = [
        ('Vendas', data.get('totalSales', 0), '#22c55e'),
        ('Custos', -data.get('totalCosts', 0), '#ef4444'),
        ('Margem Bruta', data.get('grossMargin', 0), '#3b82f6'),
        ('IVA', -data.get('totalVAT', 0), '#9333ea'),
        ('Margem Líquida', data.get('netMargin', 0), '#3b82f6')
    ]
    
    # Find max value for scaling
    max_val = max(abs(v[1]) for v in values)
    if max_val == 0:
        max_val = 1
    
    # SVG dimensions
    width = 600
    height = 400
    margin = 40
    bar_width = 80
    chart_height = height - 2 * margin
    chart_width = width - 2 * margin
    
    svg = f'''
    <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
        <!-- Background -->
        <rect width="{width}" height="{height}" fill="#f9fafb"/>
        
        <!-- Grid lines -->
        <g stroke="#e5e7eb" stroke-width="1">
    '''
    
    # Add horizontal grid lines
    for i in range(5):
        y = margin + (i * chart_height / 4)
        svg += f'<line x1="{margin}" y1="{y}" x2="{width-margin}" y2="{y}"/>'
    
    svg += '</g>'
    
    # Add bars
    for i, (label, value, color) in enumerate(values):
        x = margin + i * (bar_width + 20) + 10
        bar_height = abs(value) / max_val * (chart_height * 0.8)
        y = margin + chart_height / 2 - (bar_height if value > 0 else 0)
        
        # Bar
        svg += f'''
        <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}" 
              fill="{color}" rx="4" opacity="0.8"/>
        '''
        
        # Value label
        svg += f'''
        <text x="{x + bar_width/2}" y="{y - 5 if value > 0 else y + bar_height + 15}" 
              text-anchor="middle" font-family="Arial" font-size="12" fill="#374151">
            €{abs(value):,.0f}
        </text>
        '''
        
        # Category label
        svg += f'''
        <text x="{x + bar_width/2}" y="{height - 15}" 
              text-anchor="middle" font-family="Arial" font-size="12" fill="#374151">
            {label}
        </text>
        '''
    
    # Add axis
    svg += f'''
        <line x1="{margin}" y1="{margin + chart_height/2}" 
              x2="{width-margin}" y2="{margin + chart_height/2}" 
              stroke="#374151" stroke-width="2"/>
    </svg>
    '''
    
    return svg


def generate_pie_chart_svg(data: Dict[str, float]) -> str:
    """Generate SVG pie chart"""
    total = data.get('totalSales', 0)
    if total == 0:
        return ''
    
    segments = [
        ('Custos', data.get('totalCosts', 0), '#ef4444'),
        ('IVA', data.get('totalVAT', 0), '#9333ea'),
        ('Margem Líquida', data.get('netMargin', 0), '#3b82f6')
    ]
    
    # SVG dimensions
    size = 300
    center_x = size / 2
    center_y = size / 2
    radius = 100
    
    svg = f'''
    <svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
        <!-- Background -->
        <rect width="{size}" height="{size}" fill="#f9fafb"/>
    '''
    
    # Calculate angles
    start_angle = 0
    for label, value, color in segments:
        percentage = value / total
        angle = percentage * 360
        end_angle = start_angle + angle
        
        # Calculate path
        large_arc = 1 if angle > 180 else 0
        start_x = center_x + radius * math.cos(math.radians(start_angle))
        start_y = center_y + radius * math.sin(math.radians(start_angle))
        end_x = center_x + radius * math.cos(math.radians(end_angle))
        end_y = center_y + radius * math.sin(math.radians(end_angle))
        
        svg += f'''
        <path d="M {center_x} {center_y} L {start_x} {start_y} 
                 A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y} Z"
              fill="{color}" stroke="white" stroke-width="2" opacity="0.8"/>
        '''
        
        # Add label
        label_angle = start_angle + angle / 2
        label_x = center_x + (radius + 30) * math.cos(math.radians(label_angle))
        label_y = center_y + (radius + 30) * math.sin(math.radians(label_angle))
        
        svg += f'''
        <text x="{label_x}" y="{label_y}" text-anchor="middle" 
              font-family="Arial" font-size="12" fill="#374151">
            {label} ({percentage*100:.1f}%)
        </text>
        '''
        
        start_angle = end_angle
    
    svg += '</svg>'
    return svg


def generate_pdf_report(session_data: Dict[str, Any], calculation_results: List[Dict], 
                       vat_rate: float, final_results: Dict[str, float]) -> bytes:
    """Generate a HTML report with inline charts that can be printed to PDF"""
    
    # Generate charts
    bar_chart = generate_bar_chart_svg(final_results)
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-PT">
    <head>
        <meta charset="UTF-8">
        <title>Relatório IVA sobre Margem - {datetime.now().strftime('%d/%m/%Y')}</title>
        <style>
            @media print {{
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0;
                    padding: 20px;
                }}
                .no-print {{ display: none; }}
                .page-break {{ page-break-after: always; }}
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #1f2937;
                text-align: center;
                margin-bottom: 10px;
            }}
            h2 {{
                color: #374151;
                margin-top: 30px;
                margin-bottom: 15px;
                border-bottom: 2px solid #e5e7eb;
                padding-bottom: 5px;
            }}
            .subtitle {{
                text-align: center;
                color: #6b7280;
                margin-bottom: 30px;
            }}
            .summary-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            .summary-table th, .summary-table td {{
                border: 1px solid #e5e7eb;
                padding: 12px;
                text-align: left;
            }}
            .summary-table th {{
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
            }}
            .summary-table tr:nth-child(even) {{
                background-color: #f9fafb;
            }}
            .summary-table tr:last-child {{
                background-color: #eff6ff;
                font-weight: bold;
            }}
            .value {{
                text-align: right;
            }}
            .chart-container {{
                text-align: center;
                margin: 30px 0;
                padding: 20px;
                background-color: #f9fafb;
                border-radius: 8px;
            }}
            .chart-grid {{
                display: flex;
                justify-content: space-around;
                gap: 30px;
                margin: 30px 0;
            }}
            .chart-box {{
                flex: 1;
                text-align: center;
                background-color: #f9fafb;
                padding: 20px;
                border-radius: 8px;
            }}
            .savings {{
                background-color: #f0fdf4;
                border: 1px solid #86efac;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                margin-top: 50px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
                text-align: center;
                color: #6b7280;
                font-size: 0.9em;
            }}
            .detail-table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 0.9em;
            }}
            .detail-table th, .detail-table td {{
                border: 1px solid #e5e7eb;
                padding: 8px;
                text-align: left;
            }}
            .detail-table th {{
                background-color: #3b82f6;
                color: white;
            }}
            .print-button {{
                background-color: #ef4444;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                margin: 20px auto;
                display: block;
            }}
            .print-button:hover {{
                background-color: #dc2626;
            }}
            .metric-card {{
                background-color: #f3f4f6;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin: 10px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #1f2937;
            }}
            .metric-label {{
                font-size: 14px;
                color: #6b7280;
                margin-top: 5px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <button class="print-button no-print" onclick="window.print()">Imprimir / Guardar como PDF</button>
        
        <h1>Relatório IVA sobre Margem - Regime Especial</h1>
        <p class="subtitle">Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        
        <p><strong>Base Legal:</strong> Artigo 308º do CIVA - Regime especial das agências de viagens</p>
        
        <h2>Resumo Executivo</h2>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value" style="color: #22c55e;">€{final_results.get('totalSales', 0):,.2f}</div>
                <div class="metric-label">Total de Vendas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #ef4444;">€{final_results.get('totalCosts', 0):,.2f}</div>
                <div class="metric-label">Total de Custos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #3b82f6;">€{final_results.get('grossMargin', 0):,.2f}</div>
                <div class="metric-label">Margem Bruta</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #9333ea;">€{final_results.get('totalVAT', 0):,.2f}</div>
                <div class="metric-label">IVA ({vat_rate}%)</div>
            </div>
            <div class="metric-card">
                <div class="metric-value" style="color: #3b82f6;">€{final_results.get('netMargin', 0):,.2f}</div>
                <div class="metric-label">Margem Líquida</div>
            </div>
        </div>
        
        <h2>Análise Gráfica</h2>
        <div class="chart-container">
            <h3>Análise Financeira - IVA sobre Margem</h3>
            {bar_chart}
        </div>
        
        <div class="savings">
            <h3>Análise de Poupança</h3>
            <p><strong>IVA no regime normal:</strong> €{(final_results.get('totalSales', 0) * vat_rate / 100):,.2f}</p>
            <p><strong>IVA no regime de margem:</strong> €{final_results.get('totalVAT', 0):,.2f}</p>
            <p><strong>Poupança fiscal:</strong> <span style="color: #16a34a; font-weight: bold;">€{((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)):,.2f}</span></p>
            <p style="margin-top: 10px;"><em>Utilizando o regime de margem, poupa {(((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)) / (final_results.get('totalSales', 0) * vat_rate / 100) * 100):.1f}% em IVA comparado com o regime normal.</em></p>
        </div>
        
        <div class="page-break"></div>
        
        <h2>Detalhes por Documento</h2>
        <table class="detail-table">
            <tr>
                <th>Documento</th>
                <th>Cliente</th>
                <th class="value">Venda (€)</th>
                <th class="value">Custos (€)</th>
                <th class="value">Margem (€)</th>
                <th class="value">IVA (€)</th>
            </tr>
    """
    
    # Add details (limit to first 20)
    for i, result in enumerate(calculation_results[:20]):
        html_content += f"""
            <tr>
                <td>{result.get('invoice_number', '')}</td>
                <td>{result.get('client', '')[:30]}</td>
                <td class="value">{result.get('sale_amount', 0):,.2f}</td>
                <td class="value">{result.get('total_allocated_costs', 0):,.2f}</td>
                <td class="value">{result.get('gross_margin', 0):,.2f}</td>
                <td class="value">{result.get('vat_amount', 0):,.2f}</td>
            </tr>
        """
    
    html_content += """
        </table>
    """
    
    if len(calculation_results) > 20:
        html_content += f"""
        <p style="font-style: italic; color: #6b7280;">
            Nota: Apresentados os primeiros 20 de {len(calculation_results)} documentos. 
            Consulte o ficheiro Excel para a lista completa.
        </p>
        """
    
    html_content += """
        <div class="footer">
            <p><strong>Accounting Advantage</strong><br>
            Sistema Profissional de Cálculo de IVA sobre Margem<br>
            Este relatório foi gerado automaticamente e não substitui aconselhamento fiscal profissional.</p>
        </div>
        
        <script>
            // Auto-print on load if requested
            const urlParams = new URLSearchParams(window.location.search);
            if (urlParams.get('print') === 'true') {
                window.print();
            }
        </script>
    </body>
    </html>
    """
    
    # Return HTML as bytes
    return html_content.encode('utf-8')


