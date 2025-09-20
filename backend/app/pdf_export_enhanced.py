"""
Enhanced Professional PDF Export module for IVA Margem Turismo
Legal compliance and professional validation ready
Expert-level data visualization with 30 years of experience + Legal requirements
"""
import io
import math
import hashlib
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class EnhancedReportGenerator:
    """Enhanced professional report generator with legal compliance"""

    def __init__(self):
        self.colors = {
            'primary': '#1e40af',      # Deep blue
            'success': '#16a34a',      # Green
            'danger': '#dc2626',       # Red
            'warning': '#d97706',      # Orange
            'info': '#2563eb',         # Blue
            'purple': '#7c3aed',       # Purple
            'teal': '#0891b2',         # Teal
            'gray': '#6b7280',         # Gray
            'light': '#f3f4f6',        # Light gray
            'dark': '#1f2937',         # Dark gray
            'legal': '#0f766e'         # Teal for legal sections
        }
        self.system_version = "1.2.5"

    def generate_report_hash(self, content: str) -> str:
        """Generate SHA256 hash for report traceability"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def generate_advanced_bar_chart(self, data: Dict[str, float], title: str = "Análise Financeira Completa") -> str:
        """Generate professional bar chart with proper scaling and annotations"""
        # Check if we're in period mode
        is_period_mode = data.get('calculationType') == 'period'
        margin_label = 'Margem Compensada' if is_period_mode else 'Margem Bruta'

        values = [
            ('Total Vendas', data.get('totalSales', 0), self.colors["success"], True),
            ('Total Custos', data.get('totalCosts', 0), self.colors["danger"], False),
            (margin_label, data.get('grossMargin', 0), self.colors["info"], True),
            ('IVA s/ Margem', data.get('totalVAT', 0), self.colors["purple"], False),
            ('Margem Líquida', data.get('netMargin', 0), self.colors["primary"], True)
        ]

        # Calculate dimensions
        width = 800
        height = 500
        margin = {'top': 60, 'right': 40, 'bottom': 80, 'left': 80}
        chart_width = width - margin["left"] - margin["right"]
        chart_height = height - margin["top"] - margin["bottom"]

        # Find max value for scaling
        max_val = max(abs(v[1]) for v in values)
        if max_val == 0:
            max_val = 1000

        # Round up to nice number
        scale_max = math.ceil(max_val / 1000) * 1000

        bar_width = chart_width / len(values) * 0.7
        spacing = chart_width / len(values) * 0.3

        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">
            <defs>
                <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                    <feOffset dx="0" dy="2" result="offsetblur"/>
                    <feComponentTransfer>
                        <feFuncA type="linear" slope="0.2"/>
                    </feComponentTransfer>
                    <feMerge>
                        <feMergeNode/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
                <linearGradient id="gridGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#f3f4f6;stop-opacity:0.5" />
                    <stop offset="100%" style="stop-color:#f3f4f6;stop-opacity:0" />
                </linearGradient>
            </defs>

            <!-- Background -->
            <rect width="{width}" height="{height}" fill="white"/>
            <rect x="{margin["left"]}" y="{margin["top"]}" width="{chart_width}" height="{chart_height}" fill="url(#gridGradient)" opacity="0.5"/>

            <!-- Title -->
            <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="{self.colors["dark"]}">{title}</text>

            <!-- Grid lines -->
            <g stroke="{self.colors["light"]}" stroke-width="1" stroke-dasharray="3,3">
        '''

        # Y-axis grid lines and labels
        grid_steps = 5
        for i in range(grid_steps + 1):
            y = margin["top"] + chart_height - (i * chart_height / grid_steps)
            value = i * scale_max / grid_steps

            svg += f'<line x1="{margin["left"]}" y1="{y}" x2="{width - margin["right"]}" y2="{y}"/>'
            svg += f'<text x="{margin["left"] - 10}" y="{y + 5}" text-anchor="end" font-family="Arial" font-size="12" fill="{self.colors["gray"]}">€{value:,.0f}</text>'

        svg += '</g>'

        # Draw bars with animations
        for i, (label, value, color, is_positive) in enumerate(values):
            x = margin["left"] + i * (bar_width + spacing) + spacing/2
            bar_height = abs(value) / scale_max * chart_height
            y = margin["top"] + chart_height - bar_height

            # Create gradient for each bar
            svg += f'''
            <defs>
                <linearGradient id="grad{i}" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{color};stop-opacity:0.7" />
                </linearGradient>
            </defs>
            '''

            # Bar with rounded corners and shadow
            svg += f'''
            <g>
                <rect x="{x}" y="{y}" width="{bar_width}" height="{bar_height}"
                      fill="url(#grad{i})" rx="4" ry="4" filter="url(#shadow)">
                    <animate attributeName="height" from="0" to="{bar_height}" dur="0.5s" begin="{i*0.1}s" fill="freeze"/>
                    <animate attributeName="y" from="{margin["top"] + chart_height}" to="{y}" dur="0.5s" begin="{i*0.1}s" fill="freeze"/>
                </rect>

                <!-- Value label on top of bar -->
                <text x="{x + bar_width/2}" y="{y - 10}" text-anchor="middle"
                      font-family="Arial" font-size="14" font-weight="bold" fill="{color}">
                    €{value:,.2f}
                </text>

                <!-- Category label -->
                <text x="{x + bar_width/2}" y="{margin["top"] + chart_height + 25}"
                      text-anchor="middle" font-family="Arial" font-size="12" fill="{self.colors["dark"]}">
                    {label}
                </text>

                <!-- Percentage of sales -->
                <text x="{x + bar_width/2}" y="{margin["top"] + chart_height + 45}"
                      text-anchor="middle" font-family="Arial" font-size="10" fill="{self.colors["gray"]}">
                    ({value / data.get('totalSales', 1) * 100:.1f}% vendas)
                </text>
            </g>
            '''

        # X and Y axes
        svg += f'''
            <line x1="{margin["left"]}" y1="{margin["top"]}" x2="{margin["left"]}" y2="{margin["top"] + chart_height}"
                  stroke="{self.colors["dark"]}" stroke-width="2"/>
            <line x1="{margin["left"]}" y1="{margin["top"] + chart_height}" x2="{width - margin["right"]}" y2="{margin["top"] + chart_height}"
                  stroke="{self.colors["dark"]}" stroke-width="2"/>
        </svg>
        '''

        return svg

    def generate_margin_waterfall_chart(self, data: Dict[str, float]) -> str:
        """Generate a waterfall chart highlighting how sales convert into net margin."""
        total_sales = float(data.get('totalSales', 0) or 0)
        total_costs = float(data.get('totalCosts', 0) or 0)
        gross_margin = float(data.get('grossMargin', total_sales - total_costs) or 0)
        total_vat = float(data.get('totalVAT', 0) or 0)
        net_margin = data.get('netMargin')
        if net_margin is None:
            net_margin = gross_margin - total_vat
        net_margin = float(net_margin or 0)

        steps = [
            {"label": "Total de Vendas", "type": "total", "amount": total_sales, "color": self.colors["success"]},
            {"label": "(-) Custos Diretos", "type": "delta", "amount": -total_costs, "color": self.colors["danger"]},
            {"label": "Margem Bruta", "type": "subtotal", "amount": gross_margin, "color": self.colors["info"]},
            {"label": "(-) IVA Regime Margem", "type": "delta", "amount": -total_vat, "color": self.colors["purple"]},
            {"label": "Margem Líquida", "type": "total", "amount": net_margin, "color": self.colors["primary"]},
        ]

        width = 1024
        height = 520
        margin = {"top": 70, "right": 60, "bottom": 110, "left": 120}
        chart_width = width - margin["left"] - margin["right"]
        chart_height = height - margin["top"] - margin["bottom"]

        step_spacing = chart_width / max(len(steps), 1)
        bar_width = step_spacing * 0.52
        gap = (step_spacing - bar_width) / 2

        chart_points = []
        running_total = 0.0
        for step in steps:
            if step["type"] in {"total", "subtotal"}:
                start_value = 0.0
                end_value = step["amount"]
                running_total = end_value
            else:
                start_value = running_total
                end_value = running_total + step["amount"]
                running_total = end_value
            chart_points.append({
                "step": step,
                "start": start_value,
                "end": end_value,
            })

        values_for_scale = [0.0]
        for point in chart_points:
            values_for_scale.extend([point["start"], point["end"]])
        min_value = min(values_for_scale)
        max_value = max(values_for_scale)
        if min_value == max_value:
            max_value = min_value + 1.0

        def value_to_y(value: float) -> float:
            return margin["top"] + (max_value - value) / (max_value - min_value) * chart_height

        baseline_y = value_to_y(0.0)

        svg_parts = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
            '<defs>',
            '    <filter id="wfShadow" x="-30%" y="-30%" width="160%" height="160%">',
            '        <feGaussianBlur in="SourceAlpha" stdDeviation="2"/>',
            '        <feOffset dx="0" dy="2" result="offsetblur"/>',
            '        <feComponentTransfer>',
            '            <feFuncA type="linear" slope="0.18"/>',
            '        </feComponentTransfer>',
            '        <feMerge>',
            '            <feMergeNode/>',
            '            <feMergeNode in="SourceGraphic"/>',
            '        </feMerge>',
            '    </filter>',
            '</defs>',
            f'<rect width="{width}" height="{height}" fill="white"/>',
            f'<text x="{width/2}" y="38" text-anchor="middle" font-family="Arial" font-size="22" font-weight="bold" fill="{self.colors["dark"]}">Formação da Margem (Waterfall)</text>',
        ]

        grid_steps = 6
        for i in range(grid_steps + 1):
            value = min_value + (max_value - min_value) * i / grid_steps
            y = value_to_y(value)
            svg_parts.append(
                f'<line x1="{margin["left"]}" y1="{y}" x2="{width - margin["right"]}" y2="{y}" stroke="{self.colors["light"]}" stroke-dasharray="3,3" stroke-width="1"/>'
            )
            svg_parts.append(
                f'<text x="{margin["left"] - 16}" y="{y + 5}" text-anchor="end" font-family="Arial" font-size="12" fill="{self.colors["gray"]}">€{value:,.0f}</text>'
            )

        svg_parts.append(
            f'<line x1="{margin["left"]}" y1="{baseline_y}" x2="{width - margin["right"]}" y2="{baseline_y}" stroke="{self.colors["dark"]}" stroke-width="2" opacity="0.8"/>'
        )

        for index, point in enumerate(chart_points):
            step = point["step"]
            start_value = point["start"]
            end_value = point["end"]
            x = margin["left"] + index * step_spacing + gap
            label_x = x + bar_width / 2

            top_value = max(start_value, end_value)
            bottom_value = min(start_value, end_value)
            top_y = value_to_y(top_value)
            bottom_y = value_to_y(bottom_value)
            bar_height = abs(bottom_y - top_y)
            if bar_height < 2:
                bar_height = 2
            bar_y = top_y

            svg_parts.append(
                f'<rect x="{x}" y="{bar_y}" width="{bar_width}" height="{bar_height}" fill="{step["color"]}" rx="6" ry="6" filter="url(#wfShadow)" opacity="0.92"/>'
            )

            if step["type"] == "delta":
                value_label = f"Δ €{step['amount']:,.2f}"
                if step["amount"] < 0:
                    label_y = max(bottom_y + 26, baseline_y + 26)
                    svg_parts.append(
                        f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="{self.colors["danger"]}">{value_label}</text>'
                    )
                else:
                    label_y = top_y - 12
                    svg_parts.append(
                        f'<text x="{label_x}" y="{label_y}" text-anchor="middle" font-family="Arial" font-size="13" font-weight="bold" fill="{self.colors["success"]}">{value_label}</text>'
                    )

                svg_parts.append(
                    f'<line x1="{label_x}" y1="{baseline_y}" x2="{label_x}" y2="{bottom_y}" stroke="{self.colors["gray"]}" stroke-dasharray="2,2" stroke-width="1" opacity="0.5"/>'
                )
            else:
                svg_parts.append(
                    f'<text x="{label_x}" y="{top_y - 16}" text-anchor="middle" font-family="Arial" font-size="14" font-weight="bold" fill="{self.colors["dark"]}">€{end_value:,.2f}</text>'
                )

            svg_parts.append(
                f'<text x="{label_x}" y="{margin["top"] + chart_height + 44}" text-anchor="middle" font-family="Arial" font-size="12" fill="{self.colors["dark"]}">{step["label"]}</text>'
            )

        svg_parts.append('</svg>')
        return ''.join(f"{part}\n" for part in svg_parts)

    def generate_comparison_chart(self, data: Dict[str, float], vat_rate: float) -> str:
        """Generate comparison chart between normal VAT and margin VAT"""
        normal_vat = data.get('totalSales', 0) * vat_rate / 100
        margin_vat = data.get('totalVAT', 0)
        savings = normal_vat - margin_vat

        width = 600
        height = 300
        bar_height = 60

        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{width}" height="{height}" fill="white"/>

            <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="{self.colors["dark"]}">
                Comparação: IVA Normal vs IVA Margem
            </text>

            <!-- Normal VAT -->
            <g transform="translate(50, 70)">
                <text x="0" y="0" font-family="Arial" font-size="14" fill="{self.colors["dark"]}">IVA Regime Normal ({vat_rate}%)</text>
                <rect x="0" y="10" width="{(normal_vat / normal_vat) * 400}" height="{bar_height}"
                      fill="{self.colors["danger"]}" opacity="0.8" rx="4"/>
                <text x="{(normal_vat / normal_vat) * 400 + 10}" y="{10 + bar_height/2 + 5}"
                      font-family="Arial" font-size="14" font-weight="bold" fill="{self.colors["danger"]}">
                    €{normal_vat:,.2f}
                </text>
            </g>

            <!-- Margin VAT -->
            <g transform="translate(50, 150)">
                <text x="0" y="0" font-family="Arial" font-size="14" fill="{self.colors["dark"]}">IVA Regime Margem</text>
                <rect x="0" y="10" width="{(margin_vat / normal_vat) * 400}" height="{bar_height}"
                      fill="{self.colors["success"]}" opacity="0.8" rx="4"/>
                <text x="{(margin_vat / normal_vat) * 400 + 10}" y="{10 + bar_height/2 + 5}"
                      font-family="Arial" font-size="14" font-weight="bold" fill="{self.colors["success"]}">
                    €{margin_vat:,.2f}
                </text>
            </g>

            <!-- Savings -->
            <rect x="50" y="240" width="500" height="40" fill="{self.colors["success"]}" opacity="0.1" rx="20"/>
            <text x="{width/2}" y="265" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="{self.colors["success"]}">
                Poupança: €{savings:,.2f} ({(savings/normal_vat*100):.1f}%)
            </text>
        </svg>
        '''

        return svg

    def generate_report(self, session_data: Dict[str, Any], calculation_results: List[Dict],
                       vat_rate: float, final_results: Dict[str, float],
                       company_info: Optional[Dict[str, str]] = None,
                       saft_hash: Optional[str] = None) -> bytes:
        """Generate enhanced professional PDF report with legal compliance"""

        # Generate report metadata
        report_timestamp = datetime.now()
        report_id = str(uuid.uuid4())

        # Company information defaults
        company_info = company_info or {}
        company_name = company_info.get('name', '[Nome da Empresa]')
        company_nif = company_info.get('nif', '[NIF da Empresa]')
        company_cae = company_info.get('cae', '[CAE da Empresa]')

        # Check if period calculation mode
        is_period_mode = final_results.get('calculationType') == 'period'

        # Adjust chart data for period mode
        chart_data = final_results.copy()
        if is_period_mode:
            chart_data["grossMargin"] = final_results.get('compensatedMargin', final_results.get('grossMargin', 0))
            chart_data["calculationType"] = 'period'

        # Generate all charts
        bar_chart = self.generate_advanced_bar_chart(chart_data)
        waterfall_chart = self.generate_margin_waterfall_chart(chart_data)
        comparison_chart = self.generate_comparison_chart(chart_data, vat_rate)

        # Calculate key metrics
        total_documents = len(session_data.get('sales', []))
        total_costs_docs = len(session_data.get('costs', []))
        margin_percentage = (final_results.get('grossMargin', 0) / final_results.get('totalSales', 1) * 100) if final_results.get('totalSales', 0) > 0 else 0

        # Start building HTML content
        # Detect data source
        meta = session_data.get('metadata', {}) if isinstance(session_data, dict) else {}
        data_source = str(meta.get('source') or 'Importação Manual')
        is_saft = 'SAF' in data_source.upper()
        is_efatura = 'E-FATURA' in data_source.upper()



        period_info = final_results.get('period', {})
        period_quarter_html = ""
        quarter = period_info.get('quarter')
        if quarter:
            period_quarter_html = (
                "<div style='font-size: 0.85em; color: #0891b2; margin-top: 4px;'>"
                f"Trimestre {quarter}/{period_info.get('year', '')}"
                "</div>"
            )

        saft_disclaimer_html = ""
        if is_saft:
            saft_disclaimer_html = (
                "<div class=\"disclaimer\">\n"
                "    <h4>🗄️ SAF‑T e Portaria 302/2016</h4>\n"
                "    <p>Os dados utilizados neste relatório foram extraídos do ficheiro SAF‑T (Standard Audit File for Tax), em conformidade com a Portaria n.º 302/2016. A integridade dos dados pode ser comprovada por hash (SHA‑256) quando disponível.</p>\n"
                "</div>"
            )

        efatura_disclaimer_html = ""
        if is_efatura:
            efatura_disclaimer_html = (
                "<div class=\"disclaimer\">\n"
                "    <h4>📑 e‑Fatura — Exportação CSV</h4>\n"
                "    <p>Os dados utilizados neste relatório foram importados do Portal e‑Fatura (exportação CSV de Vendas e Compras). Foram aplicadas rotinas de normalização (datas, valores PT, entidades) e validações de integridade de associações.</p>\n"
                "</div>"
            )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-PT">
        <head>
            <meta charset="UTF-8">
            <title>Relatório IVA sobre Margem - {company_name}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #1f2937;
                    background-color: #ffffff;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}

                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }}

                @media print {{
                    .container {{
                        max-width: 100%;
                        padding: 10px;
                    }}
                    .no-print {{
                        display: none !important;
                    }}
                    .page-break {{
                        page-break-after: always;
                    }}
                    body {{
                        font-size: 11pt;
                    }}
                    .toc, .executive-summary {{
                        page-break-after: always;
                    }}
                    /* Keep table headers and avoid splitting rows */
                    .data-table thead {{
                        display: table-header-group;
                    }}
                    .data-table tfoot {{
                        display: table-footer-group;
                    }}
                    .data-table tr {{
                        page-break-inside: avoid;
                    }}
                    svg, img {{
                        page-break-inside: avoid;
                    }}
                }}

                /* Table of Contents Styles */
                .toc {{
                    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
                    border: 2px solid #cbd5e1;
                    border-radius: 12px;
                    padding: 32px;
                    margin-bottom: 40px;
                    page-break-inside: avoid;
                }}

                .toc h2 {{
                    color: #1e40af;
                    font-size: 2em;
                    font-weight: 700;
                    margin-bottom: 24px;
                    text-align: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                }}

                .toc-list {{
                    display: grid;
                    gap: 12px;
                    max-width: 800px;
                    margin: 0 auto;
                }}

                .toc-item {{
                    display: grid;
                    grid-template-columns: auto 1fr auto;
                    gap: 16px;
                    align-items: center;
                    padding: 12px 16px;
                    background: rgba(255, 255, 255, 0.8);
                    border-radius: 8px;
                    border-left: 4px solid;
                    transition: background 0.2s ease;
                }}

                .toc-item.level-1 {{
                    border-left-color: #1e40af;
                    font-weight: 600;
                    font-size: 1.1em;
                }}

                .toc-item.level-2 {{
                    border-left-color: #3b82f6;
                    margin-left: 20px;
                }}

                .toc-item.level-3 {{
                    border-left-color: #60a5fa;
                    margin-left: 40px;
                    font-size: 0.95em;
                }}

                .toc-item:hover {{
                    background: rgba(255, 255, 255, 1);
                    transform: translateX(4px);
                }}

                .toc-number {{
                    color: #1e40af;
                    font-weight: 700;
                    font-size: 0.9em;
                    min-width: 24px;
                }}

                .toc-title {{
                    color: #1f2937;
                }}

                .toc-page {{
                    color: #6b7280;
                    font-size: 0.9em;
                }}

                .toc-link {{
                    text-decoration: none;
                    color: inherit;
                    display: contents;
                }}

                /* Executive Summary Styles */
                .executive-summary {{
                    background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
                    border: 3px solid #f59e0b;
                    border-radius: 12px;
                    padding: 40px;
                    margin-bottom: 40px;
                    page-break-inside: avoid;
                }}

                .executive-summary h2 {{
                    color: #92400e;
                    font-size: 2.2em;
                    font-weight: 700;
                    margin-bottom: 24px;
                    text-align: center;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                }}

                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                    gap: 24px;
                    margin-bottom: 32px;
                }}

                .summary-card {{
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 12px;
                    padding: 24px;
                    border-left: 6px solid;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }}

                .summary-card.primary {{
                    border-left-color: #1e40af;
                }}

                .summary-card.success {{
                    border-left-color: #16a34a;
                }}

                .summary-card.warning {{
                    border-left-color: #f59e0b;
                }}

                .summary-card.danger {{
                    border-left-color: #dc2626;
                }}

                .summary-card h4 {{
                    margin-bottom: 12px;
                    font-size: 1.1em;
                    font-weight: 600;
                }}

                .summary-value {{
                    font-size: 2.2em;
                    font-weight: 700;
                    margin-bottom: 8px;
                    letter-spacing: -0.02em;
                }}

                .summary-description {{
                    color: #6b7280;
                    font-size: 0.9em;
                    line-height: 1.4;
                }}

                .summary-highlights {{
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 12px;
                    padding: 24px;
                    margin-top: 24px;
                }}

                .summary-highlights h4 {{
                    color: #92400e;
                    margin-bottom: 16px;
                    font-size: 1.2em;
                    font-weight: 600;
                }}

                .highlight-list {{
                    display: grid;
                    gap: 12px;
                }}

                .highlight-item {{
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    padding: 12px;
                    background: rgba(255, 255, 255, 0.7);
                    border-radius: 8px;
                    border-left: 3px solid #f59e0b;
                }}

                .highlight-icon {{
                    color: #f59e0b;
                    font-weight: 700;
                    min-width: 20px;
                }}

                /* Call-out Boxes */
                .call-out {{
                    padding: 20px;
                    border-radius: 12px;
                    margin: 20px 0;
                    border-left: 6px solid;
                    position: relative;
                    overflow: hidden;
                }}

                .call-out::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    right: 0;
                    bottom: 0;
                    width: 4px;
                    opacity: 0.3;
                }}

                .call-out.critical {{
                    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
                    border-left-color: #dc2626;
                    color: #7f1d1d;
                }}

                .call-out.critical::before {{
                    background: #dc2626;
                }}

                .call-out.success {{
                    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                    border-left-color: #16a34a;
                    color: #14532d;
                }}

                .call-out.success::before {{
                    background: #16a34a;
                }}

                .call-out.warning {{
                    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
                    border-left-color: #f59e0b;
                    color: #92400e;
                }}

                .call-out.warning::before {{
                    background: #f59e0b;
                }}

                .call-out.info {{
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border-left-color: #0ea5e9;
                    color: #0c4a6e;
                }}

                .call-out.info::before {{
                    background: #0ea5e9;
                }}

                .call-out h4 {{
                    font-weight: 700;
                    margin-bottom: 8px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}

                .call-out-icon {{
                    font-size: 1.2em;
                }}

                /* Compliance Badge */
                .compliance-badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 8px 16px;
                    background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
                    border: 2px solid #16a34a;
                    border-radius: 20px;
                    color: #14532d;
                    font-weight: 600;
                    font-size: 0.9em;
                    box-shadow: 0 2px 4px rgba(22, 163, 74, 0.2);
                }}

                /* Status Indicators */
                .status-indicator {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 6px 12px;
                    border-radius: 16px;
                    font-size: 0.85em;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                }}

                .status-indicator.validated {{
                    background: #dcfce7;
                    color: #16a34a;
                }}

                .status-indicator.pending {{
                    background: #fef3c7;
                    color: #d97706;
                }}

                .status-indicator.critical {{
                    background: #fecaca;
                    color: #dc2626;
                }}

                /* Section Anchors */
                .section-anchor {{
                    display: block;
                    position: relative;
                    top: -80px;
                    visibility: hidden;
                }}

                /* Hierarchical Section Numbering */
                .section-number {{
                    color: #1e40af;
                    font-weight: 700;
                    margin-right: 12px;
                }}

                /* Enhanced Section Headers */
                .section-header {{
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    margin-bottom: 24px;
                    padding-bottom: 12px;
                    border-bottom: 3px solid #e5e7eb;
                }}

                .section-icon {{
                    width: 48px;
                    height: 48px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    color: white;
                }}

                /* Bookmarks for PDF */
                .bookmark {{
                    position: absolute;
                    left: -9999px;
                    visibility: hidden;
                }}

                /* Key Metrics Highlight */
                .key-metrics-highlight {{
                    background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%);
                    border: 3px solid #2563eb;
                    border-radius: 16px;
                    padding: 32px;
                    margin: 32px 0;
                    text-align: center;
                }}

                .key-metrics-highlight h3 {{
                    color: #1e40af;
                    font-size: 1.8em;
                    font-weight: 700;
                    margin-bottom: 20px;
                }}

                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 24px;
                    margin-top: 24px;
                }}

                .metric-highlight {{
                    background: rgba(255, 255, 255, 0.9);
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                }}

                .metric-highlight .value {{
                    font-size: 2em;
                    font-weight: 700;
                    margin-bottom: 4px;
                }}

                .metric-highlight .label {{
                    color: #6b7280;
                    font-size: 0.9em;
                    font-weight: 500;
                }}

                /* Legal Document Header */
                .legal-header {{
                    background: linear-gradient(135deg, {self.colors["legal"]} 0%, #0f766e 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 12px;
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }}

                .company-info {{
                    display: grid;
                    grid-template-columns: 2fr 1fr;
                    gap: 30px;
                    align-items: start;
                }}

                .company-details h1 {{
                    font-size: 2.2em;
                    font-weight: 700;
                    margin-bottom: 8px;
                }}

                .company-details .subtitle {{
                    font-size: 1.1em;
                    opacity: 0.9;
                    margin-bottom: 20px;
                }}

                .company-meta {{
                    display: grid;
                    grid-template-columns: auto 1fr;
                    gap: 8px 16px;
                    font-size: 0.95em;
                }}

                .company-meta strong {{
                    opacity: 0.8;
                }}

                .report-meta {{
                    text-align: right;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 8px;
                }}

                .report-meta .big-number {{
                    font-size: 2em;
                    font-weight: 700;
                    margin: 8px 0;
                }}

                /* Legal Compliance Section */
                .legal-compliance {{
                    background: linear-gradient(135deg, #fefce8 0%, #fef3c7 100%);
                    border: 2px solid #d97706;
                    border-radius: 12px;
                    padding: 30px;
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }}

                .legal-compliance h2 {{
                    color: #92400e;
                    margin-bottom: 20px;
                    font-size: 1.5em;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}

                .disclaimers {{
                    display: grid;
                    gap: 16px;
                    margin-bottom: 24px;
                }}

                .disclaimer {{
                    background: rgba(255,255,255,0.7);
                    padding: 16px;
                    border-radius: 8px;
                    border-left: 4px solid #d97706;
                }}

                .disclaimer h4 {{
                    color: #92400e;
                    margin-bottom: 8px;
                    font-size: 1em;
                }}

                .disclaimer p {{
                    color: #78350f;
                    font-size: 0.9em;
                    line-height: 1.5;
                }}

                /* Professional Validation Section */
                .validation-section {{
                    background: #f8fafc;
                    border: 2px solid #cbd5e1;
                    border-radius: 12px;
                    padding: 30px;
                    margin: 30px 0;
                    page-break-inside: avoid;
                }}

                .validation-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    margin-top: 20px;
                }}

                .validation-box {{
                    background: white;
                    border: 2px dashed #cbd5e1;
                    border-radius: 8px;
                    padding: 24px;
                    text-align: center;
                    min-height: 120px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}

                .validation-box h4 {{
                    color: #475569;
                    margin-bottom: 12px;
                }}

                .signature-line {{
                    border-bottom: 2px solid #cbd5e1;
                    margin: 20px 0 8px 0;
                    height: 30px;
                }}

                .checklist {{
                    background: white;
                    border-radius: 8px;
                    padding: 20px;
                    margin-top: 20px;
                }}

                .checklist h4 {{
                    color: #475569;
                    margin-bottom: 16px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }}

                .checklist-items {{
                    display: grid;
                    gap: 12px;
                }}

                .checklist-item {{
                    display: grid;
                    grid-template-columns: 30px 1fr auto;
                    gap: 12px;
                    align-items: center;
                    padding: 8px;
                    border-radius: 4px;
                    transition: background 0.2s ease;
                }}

                .checklist-item:hover {{
                    background: #f1f5f9;
                }}

                .checkbox {{
                    width: 20px;
                    height: 20px;
                    border: 2px solid #cbd5e1;
                    border-radius: 4px;
                    justify-self: center;
                }}

                /* Traceability Section */
                .traceability {{
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border: 1px solid #0ea5e9;
                    border-radius: 12px;
                    padding: 24px;
                    margin-bottom: 30px;
                    font-family: 'Courier New', monospace;
                }}

                .traceability h3 {{
                    color: #0369a1;
                    margin-bottom: 16px;
                    font-family: 'Inter', sans-serif;
                }}

                .trace-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 16px;
                }}

                .trace-item {{
                    background: rgba(255,255,255,0.8);
                    padding: 12px;
                    border-radius: 6px;
                    font-size: 0.85em;
                }}

                .trace-item strong {{
                    color: #0369a1;
                    display: block;
                    margin-bottom: 4px;
                    font-family: 'Inter', sans-serif;
                }}

                /* Header Styles */
                .header {{
                    text-align: center;
                    padding: 40px 0;
                    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
                    color: white;
                    border-radius: 12px;
                    margin-bottom: 40px;
                }}

                .header h1 {{
                    font-size: 2.5em;
                    font-weight: 700;
                    margin-bottom: 10px;
                    letter-spacing: -0.02em;
                }}

                .header .subtitle {{
                    font-size: 1.1em;
                    opacity: 0.9;
                    font-weight: 300;
                }}

                /* Key Metrics Dashboard */
                .metrics-dashboard {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                }}

                .metric-card {{
                    background: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 12px;
                    padding: 24px;
                    text-align: center;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                    transition: transform 0.2s ease;
                }}

                .metric-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                }}

                .metric-card .icon {{
                    width: 48px;
                    height: 48px;
                    margin: 0 auto 12px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                }}

                .metric-card .value {{
                    font-size: 2em;
                    font-weight: 700;
                    margin-bottom: 4px;
                    letter-spacing: -0.02em;
                }}

                .metric-card .label {{
                    font-size: 0.9em;
                    color: #6b7280;
                    font-weight: 500;
                }}

                .metric-card .change {{
                    font-size: 0.85em;
                    margin-top: 8px;
                    font-weight: 600;
                }}

                /* Section Styles */
                .section {{
                    background: white;
                    border-radius: 12px;
                    padding: 32px;
                    margin-bottom: 32px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }}

                .section-title {{
                    font-size: 1.75em;
                    font-weight: 700;
                    margin-bottom: 24px;
                    color: #1f2937;
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}

                .section-title::before {{
                    content: '';
                    width: 4px;
                    height: 24px;
                    background: #3b82f6;
                    border-radius: 2px;
                }}

                /* Chart Containers */
                .chart-container {{
                    background: #f9fafb;
                    border-radius: 12px;
                    padding: 24px;
                    margin-bottom: 24px;
                    text-align: center;
                }}

                .chart-container svg {{
                    max-width: 600px;
                    width: 100%;
                    height: auto;
                    margin: 0 auto;
                    display: block;
                }}

                .waterfall-legend {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    justify-content: center;
                    margin-top: 16px;
                    font-size: 0.85em;
                    color: #475569;
                }}

                .waterfall-legend span {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                }}

                .waterfall-legend .swatch {{
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    display: inline-block;
                }}

                .chart-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
                    gap: 24px;
                    align-items: stretch;
                }}

                /* Tables */
                .data-table {{
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    margin-top: 20px;
                    font-size: 0.9em;
                }}

                .data-table th {{
                    background: #f3f4f6;
                    padding: 12px 16px;
                    text-align: left;
                    font-weight: 600;
                    color: #374151;
                    border-bottom: 2px solid #e5e7eb;
                }}

                .data-table td {{
                    padding: 12px 16px;
                    border-bottom: 1px solid #f3f4f6;
                }}

                .data-table tr:hover {{
                    background: #f9fafb;
                }}

                .data-table .value {{
                    text-align: right;
                    font-weight: 500;
                }}

                /* Highlights */
                .highlight-box {{
                    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
                    border: 1px solid #86efac;
                    border-radius: 12px;
                    padding: 24px;
                    margin: 24px 0;
                }}

                .highlight-box h3 {{
                    color: #16a34a;
                    margin-bottom: 12px;
                    font-size: 1.3em;
                }}

                /* Print Button */
                .print-btn {{
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
                    transition: all 0.2s ease;
                    z-index: 1000;
                }}

                .print-btn:hover {{
                    background: #2563eb;
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
                }}

                /* Professional touches */
                .badge {{
                    display: inline-block;
                    padding: 4px 12px;
                    border-radius: 20px;
                    font-size: 0.85em;
                    font-weight: 600;
                }}

                .badge-success {{
                    background: #dcfce7;
                    color: #16a34a;
                }}

                .badge-info {{
                    background: #dbeafe;
                    color: #2563eb;
                }}

                .badge-warning {{
                    background: #fef3c7;
                    color: #d97706;
                }}
            </style>
        </head>
        <body>
            <button class="print-btn no-print" onclick="window.print()">
                🖨️ Imprimir / Guardar PDF
            </button>

            <div class="container">
                <!-- Table of Contents -->
                <div class="toc">
                    <div class="bookmark" id="toc">Índice</div>
                    <h2>📋 Índice</h2>
                    <div class="toc-list">
                        <a href="#executive-summary" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">1.</span>
                                <span class="toc-title">Sumário Executivo</span>
                                <span class="toc-page">p. 2</span>
                            </div>
                        </a>

                        <a href="#legal-header" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">2.</span>
                                <span class="toc-title">Identificação da Empresa</span>
                                <span class="toc-page">p. 3</span>
                            </div>
                        </a>

                        <a href="#legal-compliance" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">3.</span>
                                <span class="toc-title">Conformidade Legal e Disclaimers</span>
                                <span class="toc-page">p. 4</span>
                            </div>
                        </a>

                        <a href="#validation-section" class="toc-link">
                            <div class="toc-item level-2">
                                <span class="toc-number">3.1</span>
                                <span class="toc-title">Validação Profissional</span>
                                <span class="toc-page">p. 5</span>
                            </div>
                        </a>

                        <a href="#traceability" class="toc-link">
                            <div class="toc-item level-2">
                                <span class="toc-number">3.2</span>
                                <span class="toc-title">Sistema de Rastreabilidade</span>
                                <span class="toc-page">p. 6</span>
                            </div>
                        </a>

                        <a href="#key-metrics" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">4.</span>
                                <span class="toc-title">Indicadores Chave de Performance</span>
                                <span class="toc-page">p. 7</span>
                            </div>
                        </a>

                        {('<a href="#period-calculation" class="toc-link">'
                         '<div class="toc-item level-1">'
                         '<span class="toc-number">5.</span>'
                         '<span class="toc-title">Cálculo por Período Fiscal</span>'
                         '<span class="toc-page">p. 8</span>'
                         '</div>'
                         '</a>') if is_period_mode else ""}

                        <a href="#financial-analysis" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">{6 if is_period_mode else 5}.</span>
                                <span class="toc-title">Análise Financeira Completa</span>
                                <span class="toc-page">p. {9 if is_period_mode else 8}</span>
                            </div>
                        </a>

                        <a href="#comparison-analysis" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">{7 if is_period_mode else 6}.</span>
                                <span class="toc-title">Comparação de Regimes Fiscais</span>
                                <span class="toc-page">p. {10 if is_period_mode else 9}</span>
                            </div>
                        </a>

                        <a href="#savings-analysis" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">{8 if is_period_mode else 7}.</span>
                                <span class="toc-title">Análise de Poupança Fiscal</span>
                                <span class="toc-page">p. {11 if is_period_mode else 10}</span>
                            </div>
                        </a>

                        <a href="#detailed-results" class="toc-link">
                            <div class="toc-item level-1">
                                <span class="toc-number">{9 if is_period_mode else 8}.</span>
                                <span class="toc-title">Análise Detalhada por Documento</span>
                                <span class="toc-page">p. {12 if is_period_mode else 11}</span>
                            </div>
                        </a>
                    </div>
                </div>

                <!-- Executive Summary -->
                <div class="executive-summary">
                    <div class="bookmark" id="executive-summary">Sumário Executivo</div>
                    <div class="section-anchor" id="executive-summary"></div>
                    <h2>📊 Sumário Executivo</h2>

                    <div class="summary-grid">
                        <div class="summary-card primary">
                            <h4>🏢 Volume Total de Negócios</h4>
                            <div class="summary-value" style="color: #1e40af;">€{final_results.get('totalSales', 0):,.2f}</div>
                            <div class="summary-description">
                                Faturação total processada no período de análise, base para cálculo do IVA sobre margem.
                            </div>
                        </div>

                        <div class="summary-card success">
                            <h4>💰 Margem {'Compensada' if is_period_mode else 'Bruta'} Total</h4>
                            <div class="summary-value" style="color: #16a34a;">€{final_results.get('compensatedMargin' if is_period_mode else 'grossMargin', 0):,.2f}</div>
                            <div class="summary-description">
                                {'Margem após compensação de períodos anteriores' if is_period_mode else 'Diferença entre vendas e custos diretos associados'} - base tributável IVA.
                            </div>
                        </div>

                        <div class="summary-card warning">
                            <h4>💶 IVA a Pagar ({vat_rate}%)</h4>
                            <div class="summary-value" style="color: #f59e0b;">€{final_results.get('totalVAT', 0):,.2f}</div>
                            <div class="summary-description">
                                Montante de IVA calculado sobre a margem, conforme Artigo 308º do CIVA. <br><em>Método:</em> margem bruta (IVA incluído) → IVA = margem × taxa/(100+taxa)
                            </div>
                        </div>

                        <div class="summary-card success">
                            <h4>📈 Poupança Fiscal</h4>
                            <div class="summary-value" style="color: #16a34a;">€{((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)):,.2f}</div>
                            <div class="summary-description">
                                Economia obtida com regime de margem vs. regime normal de IVA.
                            </div>
                        </div>

                        <div class="summary-card primary">
                            <h4>📊 Taxa de Margem</h4>
                            <div class="summary-value" style="color: #1e40af;">{margin_percentage:.1f}%</div>
                            <div class="summary-description">
                                Percentual de margem sobre o volume total de vendas processado.
                            </div>
                        </div>

                        <div class="summary-card danger">
                            <h4>📋 Documentos Processados</h4>
                            <div class="summary-value" style="color: #dc2626;">{total_documents + total_costs_docs}</div>
                            <div class="summary-description">
                                {total_documents} vendas + {total_costs_docs} custos analisados e associados.
                            </div>
                        </div>
                    </div>

                    <div class="summary-highlights">
                        <h4>🎯 Principais Conclusões</h4>
                        <div class="highlight-list">
                            <div class="highlight-item">
                                <span class="highlight-icon">✅</span>
                                <span>
                                    <strong>Regime de Margem Aplicável:</strong> A empresa está enquadrada no regime especial de tributação da margem (Art. 308º CIVA),
                                    permitindo significativa otimização fiscal.
                                </span>
                            </div>

                            <div class="highlight-item">
                                <span class="highlight-icon">💰</span>
                                <span>
                                    <strong>Poupança de {(((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)) / (final_results.get('totalSales', 0) * vat_rate / 100) * 100):.1f}%:</strong>
                                    Em comparação com o regime normal, a empresa economiza €{((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)):,.2f}
                                    em IVA no período analisado.
                                </span>
                            </div>

                            <div class="highlight-item">
                                <span class="highlight-icon">⚖️</span>
                                <span>
                                    <strong>Conformidade Legal:</strong> Todos os cálculos seguem rigorosamente as disposições legais e orientações da AT
                                    para o setor do turismo.
                                </span>
                            </div>

                            {(
                                "<div class='highlight-item'>"
                                "<span class='highlight-icon'>📅</span>"
                                "<span>"
                                f"<strong>Compensação Períodos Anteriores:</strong> Margem negativa de €{final_results.get('previousNegative', 0):,.2f} "
                                f"foi adequadamente compensada, restando €{abs(final_results.get('carryForward', 0)):,.2f} para transportar."
                                "</span>"
                                "</div>"
                            ) if is_period_mode and final_results.get('previousNegative', 0) > 0 else ""}

                            <div class="highlight-item">
                                <span class="highlight-icon">📊</span>
                                <span>
                                    <strong>Margem Saudável:</strong> Taxa de margem de {margin_percentage:.1f}% indica operação sustentável
                                    {"acima da média do setor" if margin_percentage > 15 else "dentro dos padrões do setor turístico"}.
                                </span>
                            </div>

                            <div class="highlight-item">
                                <span class="highlight-icon">🔍</span>
                                <span>
                                    <strong>Validação Necessária:</strong> Este relatório requer validação por ROC/TOC habilitado
                                    antes da submissão às autoridades fiscais.
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="call-out critical">
                        <h4><span class="call-out-icon">⚠️</span> Ação Requerida</h4>
                        <p>
                            <strong>Validação Profissional Obrigatória:</strong> Este documento tem caráter informativo.
                            É obrigatória a validação por Revisor Oficial de Contas (ROC) ou Técnico Oficial de Contas (TOC)
                            antes de qualquer submissão fiscal oficial.
                        </p>
                    </div>

                    <div style="text-align: center; margin-top: 24px;">
                        <span class="compliance-badge">
                            ✅ Conforme Art. 308º CIVA
                        </span>
                        <span class="status-indicator validated" style="margin-left: 16px;">
                            📋 Documentação Completa
                        </span>
                        <span class="status-indicator pending" style="margin-left: 16px;">
                            👤 Validação ROC/TOC Pendente
                        </span>
                    </div>
                </div>

                <!-- Legal Document Header -->
                <div class="legal-header">
                    <div class="bookmark" id="legal-header">Identificação da Empresa</div>
                    <div class="section-anchor" id="legal-header"></div>
                    <div class="company-info">
                        <div class="company-details">
                            <h1>Relatório IVA sobre Margem</h1>
                            <p class="subtitle">Regime Especial de Tributação - Artigo 308º do CIVA</p>

                            <div class="company-meta">
                                <strong>Empresa:</strong>
                                <span>{company_name}</span>
                                <strong>NIF:</strong>
                                <span>{company_nif}</span>
                                <strong>CAE:</strong>
                                <span>{company_cae}</span>
                                <strong>Período Fiscal:</strong>
                                <span>{final_results.get('period', {}).get('start', 'N/A')} - {final_results.get('period', {}).get('end', 'N/A')}</span>
                            </div>
                        </div>

                        <div class="report-meta">
                            <div style="font-size: 0.9em; opacity: 0.8; margin-bottom: 8px;">Relatório Nº</div>
                            <div class="big-number">{report_id[:8].upper()}</div>
                            <div style="font-size: 0.85em; opacity: 0.8; margin-top: 8px;">
                                {report_timestamp.strftime('%d/%m/%Y às %H:%M')}
                            </div>
                            <div style="font-size: 0.8em; opacity: 0.7; margin-top: 12px;">Origem:<br>{data_source}</div>
                            {"<div style='font-size: 0.8em; opacity: 0.7; margin-top: 8px;'>Hash SAF-T:<br>" + str(saft_hash[:16] + "..." if saft_hash else "N/A") + "</div>" if (saft_hash and is_saft) else ""}
                        </div>
                    </div>
                </div>

                <!-- Legal Compliance and Disclaimers -->
                <div class="legal-compliance">
                    <div class="bookmark" id="legal-compliance">Conformidade Legal</div>
                    <div class="section-anchor" id="legal-compliance"></div>
                    <h2>⚖️ Conformidade Legal e Disclaimers Obrigatórios</h2>

                    <div class="disclaimers">
                        <div class="disclaimer">
                            <h4>📋 Artigo 308º do CIVA - Regime de Tributação da Margem</h4>
                            <p>Este relatório foi elaborado com base no regime especial de tributação sobre a margem, aplicável a agências de viagem e operadores turísticos, conforme previsto no Artigo 308º do Código do IVA. O IVA incide apenas sobre a margem de lucro das operações.</p>
                        </div>

                        {saft_disclaimer_html}
                        {efatura_disclaimer_html}
                        <div class="disclaimer">
                            <h4>ℹ️ Caráter Informativo</h4>
                            <p>Este documento tem caráter puramente informativo e não substitui a declaração oficial de IVA. Os cálculos apresentados devem ser validados pelo contabilista certificado ou ROC da empresa antes da submissão às autoridades fiscais.</p>
                        </div>

                        <div class="disclaimer">
                            <h4>✅ Validação Profissional Obrigatória</h4>
                            <p>É obrigatória a validação por Revisor Oficial de Contas (ROC) ou Técnico Oficial de Contas (TOC) habilitado. Este relatório não substitui o parecer técnico profissional nem a responsabilidade fiscal da empresa.</p>
                        </div>

                    </div>
                </div>

                <!-- Professional Validation Section -->
                <div class="validation-section">
                    <div class="bookmark" id="validation-section">Validação Profissional</div>
                    <div class="section-anchor" id="validation-section"></div>
                    <h2 style="color: #475569; margin-bottom: 20px; display: flex; align-items: center; gap: 12px;">
                        👥 Validação e Certificação Profissional
                    </h2>

                    <div class="validation-grid">
                        <div class="validation-box">
                            <div>
                                <h4>ROC/TOC Responsável</h4>
                                <p style="font-size: 0.85em; color: #6b7280; margin: 8px 0;">Nome completo e número de inscrição</p>
                                <div class="signature-line"></div>
                                <p style="font-size: 0.8em; color: #6b7280;">Assinatura e Data</p>
                            </div>
                            <div style="margin-top: 16px; padding: 8px; border: 2px dashed #cbd5e1; border-radius: 4px; text-align: center; color: #6b7280; font-size: 0.8em;">
                                Espaço para Carimbo Oficial
                            </div>
                        </div>

                        <div class="validation-box">
                            <div>
                                <h4>Representante da Empresa</h4>
                                <p style="font-size: 0.85em; color: #6b7280; margin: 8px 0;">Gerente ou administrador autorizado</p>
                                <div class="signature-line"></div>
                                <p style="font-size: 0.8em; color: #6b7280;">Assinatura e Data</p>
                            </div>
                            <div style="margin-top: 16px; padding: 8px; border: 2px dashed #cbd5e1; border-radius: 4px; text-align: center; color: #6b7280; font-size: 0.8em;">
                                Espaço para Carimbo da Empresa
                            </div>
                        </div>
                    </div>

                    <div class="checklist">
                        <h4>📋 Checklist de Conformidade</h4>
                        <div class="checklist-items">
                            <div class="checklist-item">
                                <div class="checkbox"></div>
                                <span>Verificação da aplicabilidade do Art. 308º do CIVA</span>
                                <span style="font-size: 0.8em; color: #6b7280;">ROC/TOC</span>
                            </div>
                            <div class="checklist-item">
                                <div class="checkbox"></div>
                                <span>Validação da integridade do ficheiro SAF-T</span>
                                <span style="font-size: 0.8em; color: #6b7280;">ROC/TOC</span>
                            </div>
                            <div class="checklist-item">
                                <div class="checkbox"></div>
                                <span>Conferência dos cálculos de margem</span>
                                <span style="font-size: 0.8em; color: #6b7280;">ROC/TOC</span>
                            </div>
                            <div class="checklist-item">
                                <div class="checkbox"></div>
                                <span>Verificação das associações vendas-custos</span>
                                <span style="font-size: 0.8em; color: #6b7280;">Empresa</span>
                            </div>
                            <div class="checklist-item">
                                <div class="checkbox"></div>
                                <span>Revisão dos documentos fonte</span>
                                <span style="font-size: 0.8em; color: #6b7280;">Empresa</span>
                            </div>
                            <div class="checklist-item">
                                <div class="checkbox"></div>
                                <span>Aprovação para submissão fiscal</span>
                                <span style="font-size: 0.8em; color: #6b7280;">ROC/TOC</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Traceability Section -->
                <div class="traceability">
                    <div class="bookmark" id="traceability">Sistema de Rastreabilidade</div>
                    <div class="section-anchor" id="traceability"></div>
                    <h3>🔍 Sistema de Rastreabilidade</h3>
                    <div class="trace-grid">
                        <div class="trace-item">
                            <strong>Hash do Relatório (SHA-256):</strong>
                            <span id="reportHash">Será calculado após geração</span>
                        </div>
                        <div class="trace-item">
                            <strong>Timestamp ISO 8601:</strong>
                            {report_timestamp.isoformat()}
                        </div>
                        <div class="trace-item">
                            <strong>Versão do Sistema:</strong>
                            IVA Margem Pro v{self.system_version}
                        </div>
                        <div class="trace-item">
                            <strong>Origem dos Dados:</strong>
                            {data_source}{(" (Hash: " + str(saft_hash[:16]) + "...)") if (is_saft and saft_hash) else ''}
                        </div>
                        <div class="trace-item">
                            <strong>ID da Sessão:</strong>
                            {session_data.get('session_id', 'N/A')}
                        </div>
                        <div class="trace-item">
                            <strong>Total de Documentos:</strong>
                            {total_documents} vendas + {total_costs_docs} custos
                        </div>
                    </div>
                </div>

                <!-- Key Metrics Dashboard -->
                <div class="key-metrics-highlight">
                    <div class="bookmark" id="key-metrics">Indicadores Chave</div>
                    <div class="section-anchor" id="key-metrics"></div>
                    <h3>📈 Indicadores Chave de Performance</h3>
                    <div class="metrics-grid">
                        <div class="metric-highlight">
                            <div class="value" style="color: #16a34a;">€{final_results.get('totalVAT', 0):,.2f}</div>
                            <div class="label">IVA a Pagar</div>
                        </div>
                        <div class="metric-highlight">
                            <div class="value" style="color: #1e40af;">{margin_percentage:.1f}%</div>
                            <div class="label">Taxa de Margem</div>
                        </div>
                        <div class="metric-highlight">
                            <div class="value" style="color: #16a34a;">€{((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)):,.2f}</div>
                            <div class="label">Poupança Total</div>
                        </div>
                        <div class="metric-highlight">
                            <div class="value" style="color: #2563eb;">{total_documents + total_costs_docs}</div>
                            <div class="label">Docs Processados</div>
                        </div>
                    </div>
                </div>

                <div class="metrics-dashboard">
                    <div class="metric-card">
                        <div class="icon" style="background: #dcfce7;">📄</div>
                        <div class="value">{total_documents}</div>
                        <div class="label">Documentos de Venda</div>
                        <div class="change" style="color: #16a34a;">Processados</div>
                    </div>

                    <div class="metric-card">
                        <div class="icon" style="background: #fee2e2;">📋</div>
                        <div class="value">{total_costs_docs}</div>
                        <div class="label">Documentos de Custo</div>
                        <div class="change" style="color: #dc2626;">Importados</div>
                    </div>

                    <div class="metric-card">
                        <div class="icon" style="background: #dbeafe;">💰</div>
                        <div class="value">€{final_results.get('totalSales', 0):,.2f}</div>
                        <div class="label">Volume Total de Vendas</div>
                        <div class="change" style="color: #2563eb;">+IVA incluído</div>
                    </div>

                    <div class="metric-card">
                        <div class="icon" style="background: #e9d5ff;">📊</div>
                        <div class="value">{margin_percentage:.1f}%</div>
                        <div class="label">Margem sobre Vendas</div>
                        <div class="change" style="color: #7c3aed;">Taxa de lucro</div>
                    </div>

                    <div class="metric-card">
                        <div class="icon" style="background: #dcfce7;">💶</div>
                        <div class="value">€{final_results.get('totalVAT', 0):,.2f}</div>
                        <div class="label">IVA a Pagar</div>
                        <div class="change" style="color: #16a34a;">Regime margem</div>
                    </div>
                </div>
                """

        # Period Calculation Details (if applicable)
        if is_period_mode:
            html_content += f"""
                <div class="section" style="background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border: 2px solid #0ea5e9;">
                    <div class="bookmark" id="period-calculation">Cálculo por Período</div>
                    <div class="section-anchor" id="period-calculation"></div>
                    <div class="section-header">
                        <div class="section-icon" style="background: #0ea5e9;">📅</div>
                        <div>
                            <span class="section-number">5.</span>
                            <h2 class="section-title" style="color: #0369a1; margin: 0;">Cálculo por Período Fiscal</h2>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">Período de Análise</div>
                            <div style="font-size: 1.3em; font-weight: 700; color: #0369a1;">
                                {final_results.get('period', {}).get('start', '')} a {final_results.get('period', {}).get('end', '')}
                            </div>
                            {period_quarter_html}
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">Margem Bruta do Período</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: {'#16a34a' if final_results.get('grossMargin', 0) >= 0 else '#dc2626'};">
                                €{final_results.get('grossMargin', 0):,.2f}
                            </div>
                            <div style="font-size: 0.85em; color: #6b7280; margin-top: 4px;">
                                Vendas - Custos
                            </div>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">(-) Margem Negativa Anterior</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: #dc2626;">
                                €{final_results.get('previousNegative', 0):,.2f}
                            </div>
                            <div style="font-size: 0.85em; color: #6b7280; margin-top: 4px;">
                                Compensação períodos anteriores
                            </div>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">(=) Margem Compensada</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: {'#16a34a' if final_results.get('compensatedMargin', 0) >= 0 else '#dc2626'};">
                                €{final_results.get('compensatedMargin', 0):,.2f}
                            </div>
                            <div style="font-size: 0.85em; color: #6b7280; margin-top: 4px;">
                                Base tributável após compensação
                            </div>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">IVA a Pagar ({vat_rate}%)</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: #7c3aed;">
                                €{final_results.get('totalVAT', 0):,.2f}
                            </div>
                            <div style="font-size: 0.85em; color: #6b7280; margin-top: 4px;">
                                Sobre margem {"positiva" if final_results.get('compensatedMargin', 0) > 0 else "zero (negativa)"}
                            </div>
                        </div>

                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">Margem a Transportar</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: {'#dc2626' if final_results.get('carryForward', 0) < 0 else '#16a34a'};">
                                €{abs(final_results.get('carryForward', 0)):,.2f}
                            </div>
                            <div style="font-size: 0.85em; color: #6b7280; margin-top: 4px;">
                                Para próximo período
                            </div>
                        </div>
                    </div>

                    <div style="margin-top: 24px; padding: 16px; background: #fef3c7; border-radius: 8px; border-left: 4px solid #f59e0b;">
                        <h4 style="margin: 0 0 8px 0; color: #92400e;">⚖️ Conformidade Legal</h4>
                        <p style="margin: 0; color: #78350f; font-size: 0.9em;">
                            Cálculo realizado conforme <strong>Artigo 308º do CIVA</strong> - Regime especial de tributação da margem.<br>
                            A compensação de margens negativas entre períodos está em conformidade com as orientações da AT.
                        </p>
                    </div>
                </div>
                """

        html_content += f"""
                <!-- Main Analysis Section -->
                <div class="section">
                    <div class="bookmark" id="financial-analysis">Análise Financeira</div>
                    <div class="section-anchor" id="financial-analysis"></div>
                    <div class="section-header">
                        <div class="section-icon" style="background: #1e40af;">📊</div>
                        <div>
                            <span class="section-number">{6 if is_period_mode else 5}.</span>
                            <h2 class="section-title" style="margin: 0;">Análise Financeira Completa</h2>
                        </div>
                    </div>
                    <div class="chart-container">
                        {bar_chart}
                    </div>
                </div>

                <!-- Comparison and Distribution -->
                <div class="chart-grid">
                    <div class="section">
                        <div class="bookmark" id="comparison-analysis">Comparação de Regimes</div>
                        <div class="section-anchor" id="comparison-analysis"></div>
                        <div class="section-header">
                            <div class="section-icon" style="background: #dc2626;">⚖️</div>
                            <div>
                                <span class="section-number">{7 if is_period_mode else 6}.</span>
                                <h2 class="section-title" style="margin: 0;">Comparação de Regimes Fiscais</h2>
                            </div>
                        </div>
                        <div class="chart-container">
                            {comparison_chart}
                        </div>
                    </div>

                    <div class="section">
                        <div class="section-header">
                            <div class="section-icon" style="background: #1e40af;">📈</div>
                            <div>
                                <span class="section-number">{7 if is_period_mode else 6}.1</span>
                                <h2 class="section-title" style="margin: 0;">Evolução da Margem (Waterfall)</h2>
                            </div>
                        </div>
                        <div class="chart-container">
                            {waterfall_chart}
                            <div class="waterfall-legend">
                                <span><span class="swatch" style="background: {self.colors["success"]};"></span>Total de Vendas</span>
                                <span><span class="swatch" style="background: {self.colors["danger"]};"></span>Custos Diretos</span>
                                <span><span class="swatch" style="background: {self.colors["info"]};"></span>Margem Bruta</span>
                                <span><span class="swatch" style="background: {self.colors["purple"]};"></span>IVA Regime Margem</span>
                                <span><span class="swatch" style="background: {self.colors["primary"]};"></span>Margem Líquida</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Savings Highlight -->
                <div class="highlight-box">
                    <div class="bookmark" id="savings-analysis">Análise de Poupança</div>
                    <div class="section-anchor" id="savings-analysis"></div>

                    <div class="call-out success">
                        <h4><span class="call-out-icon">💰</span> Análise de Poupança Fiscal - Seção {8 if is_period_mode else 7}</h4>
                        <p style="font-size: 1.1em; margin-bottom: 16px;">
                            <strong>Vantagem Significativa do Regime de Margem:</strong> A aplicação do Artigo 308º do CIVA
                            resulta numa poupança fiscal substancial para a sua empresa.
                        </p>
                    </div>

                    <h3>💰 Análise de Poupança Fiscal</h3>
                    <p style="font-size: 1.1em; margin-bottom: 12px;">
                        Ao utilizar o <strong>Regime de IVA sobre Margem</strong>, a sua empresa obtém uma poupança significativa:
                    </p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                        <div>
                            <div style="font-size: 0.9em; color: #6b7280;">IVA no Regime Normal</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: #dc2626;">€{(final_results.get('totalSales', 0) * vat_rate / 100):,.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9em; color: #6b7280;">IVA no Regime Margem</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: #16a34a;">€{final_results.get('totalVAT', 0):,.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9em; color: #6b7280;">Poupança Total</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: #16a34a;">€{((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)):,.2f}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.9em; color: #6b7280;">Redução Percentual</div>
                            <div style="font-size: 1.5em; font-weight: 700; color: #16a34a;">{(((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)) / (final_results.get('totalSales', 0) * vat_rate / 100) * 100):.1f}%</div>
                        </div>
                    </div>
                </div>

                <!-- Detailed Results Table -->
                <div class="section page-break">
                    <div class="bookmark" id="detailed-results">Análise Detalhada</div>
                    <div class="section-anchor" id="detailed-results"></div>
                    <div class="section-header">
                        <div class="section-icon" style="background: #059669;">📋</div>
                        <div>
                            <span class="section-number">{9 if is_period_mode else 8}.</span>
                            <h2 class="section-title" style="margin: 0;">Análise Detalhada por Documento</h2>
                        </div>
                    </div>
                    <div class="call-out info">
                        <h4><span class="call-out-icon">ℹ️</span> Resumo de Documentos</h4>
                        <p>
                            Apresentamos os primeiros {min(30, len(calculation_results))} documentos de um total de <strong>{len(calculation_results)} processados</strong>.
                            Para a lista completa com todos os detalhes, consulte o <strong>ficheiro Excel exportado</strong> que acompanha este relatório.
                        </p>
                    </div>

                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Documento</th>
                                <th>Data</th>
                                <th>Cliente</th>
                                <th class="value">Venda (€)</th>
                                <th class="value">Custos (€)</th>
                                <th class="value">Margem (€)</th>
                                <th class="value">IVA (€)</th>
                                <th class="value">Margem %</th>
                            </tr>
                        </thead>
                        <tbody>
        """

        # Add detailed results (limit to 30)
        for i, result in enumerate(calculation_results[:min(30, len(calculation_results))]):
            margin_pct = (result.get('gross_margin', 0) / result.get('sale_amount', 1) * 100) if result.get('sale_amount', 0) > 0 else 0
            row_class = 'style="background: #f9fafb;"' if i % 2 == 0 else ''

            html_content += f"""
                <tr {row_class}>
                    <td><strong>{result.get('invoice_number', '')}</strong></td>
                    <td>{result.get('date', '')}</td>
                    <td>{result.get('client', '')[:35]}{'...' if len(result.get('client', '')) > 35 else ''}</td>
                    <td class="value">{result.get('sale_amount', 0):,.2f}</td>
                    <td class="value">{result.get('total_allocated_costs', 0):,.2f}</td>
                    <td class="value" style="color: {'#16a34a' if result.get('gross_margin', 0) > 0 else '#dc2626'};">
                        {result.get('gross_margin', 0):,.2f}
                    </td>
                    <td class="value">{result.get('vat_amount', 0):,.2f}</td>
                    <td class="value">
                        <span class="badge {'badge-success' if margin_pct > 20 else 'badge-warning' if margin_pct > 10 else 'badge-info'}">
                            {margin_pct:.1f}%
                        </span>
                    </td>
                </tr>
            """

        html_content += f"""
                        </tbody>
                    </table>
                </div>

                <!-- Critical Information Highlights -->
                <div class="call-out critical">
                    <h4><span class="call-out-icon">⚠️</span> Informações Críticas</h4>
                    <div style="display: grid; gap: 12px; margin-top: 16px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #dc2626; font-weight: 700;">•</span>
                            <span><strong>Validação ROC/TOC obrigatória</strong> antes de submissão fiscal</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #dc2626; font-weight: 700;">•</span>
                            <span>Este documento tem <strong>caráter puramente informativo</strong></span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #dc2626; font-weight: 700;">•</span>
                            <span>Cálculos baseados no <strong>Art. 308º do CIVA</strong> - Regime Margem</span>
                        </div>
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="color: #dc2626; font-weight: 700;">•</span>
                            <span>Poupança fiscal: <strong>€{((final_results.get('totalSales', 0) * vat_rate / 100) - final_results.get('totalVAT', 0)):,.2f}</strong> vs regime normal</span>
                        </div>
                    </div>
                </div>

                <div class="call-out success">
                    <h4><span class="call-out-icon">✅</span> Certificação de Conformidade</h4>
                    <p style="text-align: center; font-size: 1.1em; margin: 16px 0;">
                        <strong>Sistema Certificado:</strong> Todos os cálculos seguem rigorosamente as disposições legais<br>
                        do Código do IVA e orientações da Autoridade Tributária para o setor do turismo.<br><br>
                        <span class="compliance-badge" style="font-size: 1em; padding: 12px 20px;">
                            ✅ Conforme Art. 308º CIVA - Regime Especial de Tributação da Margem
                        </span>
                    </p>
                </div>

                <!-- Enhanced Footer -->
                <div style="background: linear-gradient(135deg, #1f2937 0%, #374151 100%); color: white; padding: 40px; border-radius: 12px; margin-top: 40px; text-align: center;">
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 32px; margin-bottom: 32px;">
                        <div>
                            <h4 style="color: #e5e7eb; margin-bottom: 16px; font-size: 1.1em;">📊 Sistema</h4>
                            <p style="color: #d1d5db; font-size: 0.9em; line-height: 1.5;">
                                <strong>IVA Margem Pro v{self.system_version}</strong><br>
                                Sistema Profissional de Cálculo<br>
                                Com Conformidade Legal Total
                            </p>
                        </div>

                        <div>
                            <h4 style="color: #e5e7eb; margin-bottom: 16px; font-size: 1.1em;">🔒 Rastreabilidade</h4>
                            <p style="color: #d1d5db; font-size: 0.9em; line-height: 1.5; font-family: monospace;">
                                Hash: <span id="finalHash">Calculando...</span><br>
                                Timestamp: {report_timestamp.isoformat()}<br>
                                ID: {report_id[:8].upper()}
                            </p>
                        </div>

                        <div>
                            <h4 style="color: #e5e7eb; margin-bottom: 16px; font-size: 1.1em;">⚖️ Disclaimer Legal</h4>
                            <p style="color: #d1d5db; font-size: 0.9em; line-height: 1.5;">
                                Documento informativo<br>
                                <strong style="color: #fbbf24;">Validação ROC/TOC obrigatória</strong><br>
                                Não substitui aconselhamento fiscal
                            </p>
                        </div>
                    </div>

                    <div style="border-top: 1px solid #4b5563; padding-top: 20px; color: #9ca3af; font-size: 0.85em;">
                        <p>
                            Relatório gerado em <strong>{report_timestamp.strftime('%d/%m/%Y às %H:%M:%S')}</strong><br>
                            © 2025 IVA Margem Pro - Todos os direitos reservados
                        </p>
                    </div>
                </div>
            </div>

            <script>
                // Enhanced Navigation and PDF functionality
                document.addEventListener('DOMContentLoaded', function() {{
                    // Calculate and display report hash
                    const content = document.documentElement.outerHTML;
                    const encoder = new TextEncoder();
                    const data = encoder.encode(content);

                    crypto.subtle.digest('SHA-256', data).then(hashBuffer => {{
                        const hashArray = Array.from(new Uint8Array(hashBuffer));
                        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                        const reportHashEl = document.getElementById('reportHash');
                        const finalHashEl = document.getElementById('finalHash');

                        if (reportHashEl) reportHashEl.textContent = hashHex.substring(0, 32) + '...';
                        if (finalHashEl) finalHashEl.textContent = hashHex.substring(0, 16) + '...';
                    }}).catch(err => {{
                        console.log('Hash calculation not available in this environment');
                        const reportHashEl = document.getElementById('reportHash');
                        const finalHashEl = document.getElementById('finalHash');
                        if (reportHashEl) reportHashEl.textContent = 'Hash não disponível';
                        if (finalHashEl) finalHashEl.textContent = 'N/A';
                    }});

                    // Enhanced smooth scroll with offset
                    document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
                        anchor.addEventListener('click', function (e) {{
                            e.preventDefault();
                            const targetId = this.getAttribute('href').substring(1);
                            const targetElement = document.getElementById(targetId);

                            if (targetElement) {{
                                // Calculate offset to account for fixed headers
                                const offset = 80;
                                const elementPosition = targetElement.getBoundingClientRect().top;
                                const offsetPosition = elementPosition + window.pageYOffset - offset;

                                window.scrollTo({{
                                    top: offsetPosition,
                                    behavior: 'smooth'
                                }});

                                // Highlight the target section temporarily
                                targetElement.style.transition = 'box-shadow 0.3s ease';
                                targetElement.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.3)';
                                setTimeout(() => {{
                                    targetElement.style.boxShadow = '';
                                }}, 2000);
                            }}
                        }});
                    }});

                    // Add hover effects to TOC items
                    document.querySelectorAll('.toc-item').forEach(item => {{
                        item.addEventListener('mouseenter', function() {{
                            this.style.backgroundColor = 'rgba(255, 255, 255, 1)';
                            this.style.transform = 'translateX(4px)';
                            this.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
                        }});

                        item.addEventListener('mouseleave', function() {{
                            this.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
                            this.style.transform = 'translateX(0)';
                            this.style.boxShadow = '';
                        }});
                    }});

                    // Add print preparation
                    window.addEventListener('beforeprint', function() {{
                        // Expand all collapsed sections for printing
                        document.querySelectorAll('.collapsed').forEach(el => {{
                            el.classList.remove('collapsed');
                        }});

                        // Ensure all charts and images are visible
                        document.querySelectorAll('svg, img').forEach(el => {{
                            el.style.pageBreakInside = 'avoid';
                        }});
                    }});

                    // Add keyboard navigation
                    document.addEventListener('keydown', function(e) {{
                        // Ctrl+P for print
                        if (e.ctrlKey && e.key === 'p') {{
                            e.preventDefault();
                            window.print();
                        }}

                        // Ctrl+Home to go to top
                        if (e.ctrlKey && e.key === 'Home') {{
                            e.preventDefault();
                            window.scrollTo({{ top: 0, behavior: 'smooth' }});
                        }}
                    }});

                    // Add section visibility tracking for better navigation
                    const observer = new IntersectionObserver((entries) => {{
                        entries.forEach(entry => {{
                            if (entry.isIntersecting) {{
                                // Update active TOC item
                                const id = entry.target.id;
                                document.querySelectorAll('.toc-item').forEach(item => {{
                                    item.classList.remove('active');
                                }});

                                const activeItem = document.querySelector(`a[href="#${{id}}"] .toc-item`);
                                if (activeItem) {{
                                    activeItem.classList.add('active');
                                    activeItem.style.backgroundColor = 'rgba(59, 130, 246, 0.1)';
                                    activeItem.style.borderLeftColor = '#1e40af';
                                }}
                            }}
                        }});
                    }}, {{ rootMargin: '-20% 0px -70% 0px' }});

                    // Observe all sections with anchors
                    document.querySelectorAll('.section-anchor').forEach(section => {{
                        observer.observe(section);
                    }});

                    // Auto print dialog
                    if (window.location.search.includes('autoprint=true')) {{
                        setTimeout(() => window.print(), 500);
                    }}

                    // Add loading animation completion
                    setTimeout(() => {{
                        document.body.classList.add('loaded');
                        // Animate metric cards
                        document.querySelectorAll('.metric-card, .summary-card').forEach((card, index) => {{
                            setTimeout(() => {{
                                card.style.transform = 'translateY(0)';
                                card.style.opacity = '1';
                            }}, index * 100);
                        }});
                    }}, 100);

                    console.log('📊 IVA Margem Pro v{self.system_version} - PDF Enhanced Navigation Loaded');
                }});

                // Add CSS for active states and animations
                const style = document.createElement('style');
                style.textContent = `
                    .toc-item.active {{
                        background-color: rgba(59, 130, 246, 0.1) !important;
                        border-left-color: #1e40af !important;
                        font-weight: 600;
                    }}

                    .metric-card, .summary-card {{
                        transform: translateY(20px);
                        opacity: 0;
                        transition: all 0.3s ease;
                    }}

                    body.loaded .metric-card,
                    body.loaded .summary-card {{
                        transform: translateY(0);
                        opacity: 1;
                    }}

                    @keyframes pulse {{
                        0% {{ opacity: 1; }}
                        50% {{ opacity: 0.7; }}
                        100% {{ opacity: 1; }}
                    }}

                    .compliance-badge {{
                        animation: pulse 3s infinite;
                    }}

                    /* Print optimizations */
                    @media print {{
                        .toc-item:hover {{
                            transform: none !important;
                            background: transparent !important;
                        }}

                        .section-anchor {{
                            page-break-before: auto;
                        }}

                        .call-out {{
                            page-break-inside: avoid;
                        }}

                        .chart-container {{
                            page-break-inside: avoid;
                        }}
                    }}
                `;
                document.head.appendChild(style);
            </script>
        </body>
        </html>
        """

        # Generate hash of final content
        content_hash = self.generate_report_hash(html_content)
        logger.info(f"Generated enhanced PDF report with hash: {content_hash[:16]}...")

        return html_content.encode('utf-8')


def generate_enhanced_pdf_report(session_data: Dict[str, Any], calculation_results: List[Dict],
                               vat_rate: float, final_results: Dict[str, float],
                               company_info: Optional[Dict[str, str]] = None,
                               saft_hash: Optional[str] = None) -> bytes:
    """Generate enhanced professional PDF report with legal compliance and traceability"""
    generator = EnhancedReportGenerator()
    return generator.generate_report(
        session_data=session_data,
        calculation_results=calculation_results,
        vat_rate=vat_rate,
        final_results=final_results,
        company_info=company_info,
        saft_hash=saft_hash
    )
