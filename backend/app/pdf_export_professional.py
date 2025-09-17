"""
Professional PDF Export module for IVA Margem Turismo
Expert-level data visualization with 30 years of experience
"""
import io
import math
import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProfessionalReportGenerator:
    """Professional report generator with advanced visualizations"""
    
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
            'dark': '#1f2937'          # Dark gray
        }
        self._font_cache: Optional[str] = None

    # ---------------------------------------------------------------------
    # Utility helpers
    # ---------------------------------------------------------------------
    def _font_face_block(self) -> str:
        """Return optional @font-face block when REPORT_FONT_BASE64 is set."""
        if self._font_cache is not None:
            return self._font_cache

        base64_font = os.getenv("REPORT_FONT_BASE64", "").strip()
        if not base64_font:
            self._font_cache = ""
        else:
            self._font_cache = f"""
            @font-face {{
                font-family: 'ReportPrimary';
                src: url(data:font/ttf;base64,{base64_font}) format('truetype');
                font-weight: 400;
                font-style: normal;
            }}

            @font-face {{
                font-family: 'ReportPrimary';
                src: url(data:font/ttf;base64,{base64_font}) format('truetype');
                font-weight: 600;
                font-style: normal;
            }}
            """
        return self._font_cache

    def _format_currency(self, value: Optional[float]) -> str:
        value = value or 0.0
        return f"€{value:,.2f}"

    def _format_percentage(self, numerator: float, denominator: float) -> str:
        if denominator == 0:
            return "0.0%"
        return f"{(numerator / denominator) * 100:.1f}%"

    def _normalize_company_info(self, session_data: Dict[str, Any], company_info: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Merge company info from session metadata and request payload."""
        metadata = session_data.get('metadata', {}) if session_data else {}
        session_company = metadata.get('company_info', {}) if isinstance(metadata, dict) else {}
        payload_company = company_info or {}

        def pick(key: str, default: str = "") -> str:
            return str(payload_company.get(key) or session_company.get(key) or metadata.get(key) or default)

        name = pick('name', metadata.get('company_name', 'Empresa de Turismo Lda.'))
        return {
            'name': name,
            'nif': pick('nif', metadata.get('company_nif', 'NIF não definido')),
            'address': pick('address', metadata.get('company_address', 'Morada não definida')),
            'city': pick('city', metadata.get('company_city', '')),
            'postal_code': pick('postal_code', metadata.get('company_postal_code', '')),
            'phone': pick('phone', metadata.get('company_phone', '')),
            'email': pick('email', metadata.get('company_email', '')),
        }

    def _compute_report_hash(self, session_data: Dict[str, Any], final_results: Dict[str, Any], vat_rate: float) -> str:
        payload = {
            'vat_rate': vat_rate,
            'final_results': final_results,
            'metadata': session_data.get('metadata', {}),
            'timestamp': datetime.now(timezone.utc).isoformat(),
        }
        payload_bytes = json.dumps(payload, default=str, sort_keys=True).encode('utf-8')
        return hashlib.sha256(payload_bytes).hexdigest()[:16]

    def _summarize_data_quality(self, session_data: Dict[str, Any], calculation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        sales = session_data.get('sales', []) if session_data else []
        costs = session_data.get('costs', []) if session_data else []
        unlinked_costs = [cost for cost in costs if not cost.get('linked_sales')]
        unmatched_sales = [sale for sale in sales if not sale.get('linked_costs')]

        return {
            'sales_count': len(sales),
            'cost_count': len(costs),
            'calculation_count': len(calculation_results),
            'unlinked_costs_count': len(unlinked_costs),
            'unlinked_sales_count': len(unmatched_sales),
            'unlinked_costs_total': sum(cost.get('amount', 0) or 0 for cost in unlinked_costs),
        }
    
    def generate_advanced_bar_chart(self, data: Dict[str, float], title: str = "Análise Financeira Completa") -> str:
        """Generate professional bar chart with proper scaling and annotations"""
        # Check if we're in period mode
        is_period_mode = data.get('calculationType') == 'period'
        margin_label = 'Margem Compensada' if is_period_mode else 'Margem Bruta'
        
        values = [
            ('Total Vendas', data.get('totalSales', 0), self.colors['success'], True),
            ('Total Custos', data.get('totalCosts', 0), self.colors['danger'], False),
            (margin_label, data.get('grossMargin', 0), self.colors['info'], True),
            ('IVA s/ Margem', data.get('totalVAT', 0), self.colors['purple'], False),
            ('Margem Líquida', data.get('netMargin', 0), self.colors['primary'], True)
        ]
        
        # Calculate dimensions
        width = 800
        height = 500
        margin = {'top': 60, 'right': 40, 'bottom': 80, 'left': 80}
        chart_width = width - margin['left'] - margin['right']
        chart_height = height - margin['top'] - margin['bottom']
        
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
            <rect x="{margin['left']}" y="{margin['top']}" width="{chart_width}" height="{chart_height}" fill="url(#gridGradient)" opacity="0.5"/>
            
            <!-- Title -->
            <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="20" font-weight="bold" fill="{self.colors['dark']}">{title}</text>
            
            <!-- Grid lines -->
            <g stroke="{self.colors['light']}" stroke-width="1" stroke-dasharray="3,3">
        '''
        
        # Y-axis grid lines and labels
        grid_steps = 5
        for i in range(grid_steps + 1):
            y = margin['top'] + chart_height - (i * chart_height / grid_steps)
            value = i * scale_max / grid_steps
            
            svg += f'<line x1="{margin["left"]}" y1="{y}" x2="{width - margin["right"]}" y2="{y}"/>'
            svg += f'<text x="{margin["left"] - 10}" y="{y + 5}" text-anchor="end" font-family="Arial" font-size="12" fill="{self.colors["gray"]}">€{value:,.0f}</text>'
        
        svg += '</g>'
        
        # Draw bars with animations
        for i, (label, value, color, is_positive) in enumerate(values):
            x = margin['left'] + i * (bar_width + spacing) + spacing/2
            bar_height = abs(value) / scale_max * chart_height
            y = margin['top'] + chart_height - bar_height
            
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
                    <animate attributeName="y" from="{margin['top'] + chart_height}" to="{y}" dur="0.5s" begin="{i*0.1}s" fill="freeze"/>
                </rect>
                
                <!-- Value label on top of bar -->
                <text x="{x + bar_width/2}" y="{y - 10}" text-anchor="middle" 
                      font-family="Arial" font-size="14" font-weight="bold" fill="{color}">
                    €{value:,.2f}
                </text>
                
                <!-- Category label -->
                <text x="{x + bar_width/2}" y="{margin['top'] + chart_height + 25}" 
                      text-anchor="middle" font-family="Arial" font-size="12" fill="{self.colors['dark']}">
                    {label}
                </text>
                
                <!-- Percentage of sales -->
                <text x="{x + bar_width/2}" y="{margin['top'] + chart_height + 45}" 
                      text-anchor="middle" font-family="Arial" font-size="10" fill="{self.colors['gray']}">
                    ({value / data.get('totalSales', 1) * 100:.1f}% vendas)
                </text>
            </g>
            '''
        
        # X and Y axes
        svg += f'''
            <line x1="{margin['left']}" y1="{margin['top']}" x2="{margin['left']}" y2="{margin['top'] + chart_height}" 
                  stroke="{self.colors['dark']}" stroke-width="2"/>
            <line x1="{margin['left']}" y1="{margin['top'] + chart_height}" x2="{width - margin['right']}" y2="{margin['top'] + chart_height}" 
                  stroke="{self.colors['dark']}" stroke-width="2"/>
        </svg>
        '''
        
        return svg
    
    def generate_pie_chart(self, data: Dict[str, float], title: str = "Distribuição de Valores") -> str:
        """Generate professional pie chart with labels and percentages"""
        total = data.get('totalSales', 0)
        if total == 0:
            return ''
        
        segments = [
            ('Custos Diretos', data.get('totalCosts', 0), self.colors['danger']),
            ('IVA a Pagar', data.get('totalVAT', 0), self.colors['purple']),
            ('Margem Líquida', data.get('netMargin', 0), self.colors['success'])
        ]
        
        size = 400
        center = size / 2
        radius = 120
        
        svg = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}">
            <defs>
                <filter id="pieShadow">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="3"/>
                    <feOffset dx="0" dy="3" result="offsetblur"/>
                    <feComponentTransfer>
                        <feFuncA type="linear" slope="0.3"/>
                    </feComponentTransfer>
                    <feMerge> 
                        <feMergeNode/>
                        <feMergeNode in="SourceGraphic"/> 
                    </feMerge>
                </filter>
            </defs>
            
            <!-- Background circle -->
            <circle cx="{center}" cy="{center}" r="{radius + 10}" fill="{self.colors['light']}" opacity="0.3"/>
            
            <!-- Title -->
            <text x="{center}" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="{self.colors['dark']}">{title}</text>
        '''
        
        # Calculate angles
        current_angle = -90  # Start at top
        for i, (label, value, color) in enumerate(segments):
            if value <= 0:
                continue
                
            percentage = value / total * 100
            angle = value / total * 360
            
            # Calculate path
            start_rad = math.radians(current_angle)
            end_rad = math.radians(current_angle + angle)
            
            large_arc = 1 if angle > 180 else 0
            
            start_x = center + radius * math.cos(start_rad)
            start_y = center + radius * math.sin(start_rad)
            end_x = center + radius * math.cos(end_rad)
            end_y = center + radius * math.sin(end_rad)
            
            # Create gradient
            svg += f'''
            <defs>
                <radialGradient id="pieGrad{i}">
                    <stop offset="0%" style="stop-color:{color};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{color};stop-opacity:0.7" />
                </radialGradient>
            </defs>
            '''
            
            # Draw segment
            svg += f'''
            <path d="M {center} {center} L {start_x} {start_y} A {radius} {radius} 0 {large_arc} 1 {end_x} {end_y} Z"
                  fill="url(#pieGrad{i})" stroke="white" stroke-width="2" filter="url(#pieShadow)">
                <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="{i*0.2}s" fill="freeze"/>
            </path>
            '''
            
            # Label with line
            label_angle = current_angle + angle / 2
            label_rad = math.radians(label_angle)
            
            # Line from center to label
            line_end_x = center + (radius + 20) * math.cos(label_rad)
            line_end_y = center + (radius + 20) * math.sin(label_rad)
            label_x = center + (radius + 60) * math.cos(label_rad)
            label_y = center + (radius + 60) * math.sin(label_rad)
            
            svg += f'''
            <line x1="{center + radius * 0.8 * math.cos(label_rad)}" 
                  y1="{center + radius * 0.8 * math.sin(label_rad)}"
                  x2="{line_end_x}" y2="{line_end_y}"
                  stroke="{color}" stroke-width="1" opacity="0.5"/>
            
            <text x="{label_x}" y="{label_y - 5}" text-anchor="middle" 
                  font-family="Arial" font-size="12" font-weight="bold" fill="{color}">
                {label}
            </text>
            <text x="{label_x}" y="{label_y + 10}" text-anchor="middle" 
                  font-family="Arial" font-size="11" fill="{self.colors['gray']}">
                €{value:,.2f}
            </text>
            <text x="{label_x}" y="{label_y + 25}" text-anchor="middle" 
                  font-family="Arial" font-size="10" fill="{self.colors['dark']}">
                ({percentage:.1f}%)
            </text>
            '''
            
            current_angle += angle
        
        # Center text
        svg += f'''
            <circle cx="{center}" cy="{center}" r="40" fill="white" opacity="0.9"/>
            <text x="{center}" y="{center - 5}" text-anchor="middle" 
                  font-family="Arial" font-size="14" font-weight="bold" fill="{self.colors['dark']}">
                Total
            </text>
            <text x="{center}" y="{center + 15}" text-anchor="middle" 
                  font-family="Arial" font-size="12" fill="{self.colors['gray']}">
                €{total:,.2f}
            </text>
        </svg>
        '''
        
        return svg
    
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
            
            <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="{self.colors['dark']}">
                Comparação: IVA Normal vs IVA Margem
            </text>
            
            <!-- Normal VAT -->
            <g transform="translate(50, 70)">
                <text x="0" y="0" font-family="Arial" font-size="14" fill="{self.colors['dark']}">IVA Regime Normal ({vat_rate}%)</text>
                <rect x="0" y="10" width="{(normal_vat / normal_vat) * 400}" height="{bar_height}" 
                      fill="{self.colors['danger']}" opacity="0.8" rx="4"/>
                <text x="{(normal_vat / normal_vat) * 400 + 10}" y="{10 + bar_height/2 + 5}" 
                      font-family="Arial" font-size="14" font-weight="bold" fill="{self.colors['danger']}">
                    €{normal_vat:,.2f}
                </text>
            </g>
            
            <!-- Margin VAT -->
            <g transform="translate(50, 150)">
                <text x="0" y="0" font-family="Arial" font-size="14" fill="{self.colors['dark']}">IVA Regime Margem</text>
                <rect x="0" y="10" width="{(margin_vat / normal_vat) * 400}" height="{bar_height}" 
                      fill="{self.colors['success']}" opacity="0.8" rx="4"/>
                <text x="{(margin_vat / normal_vat) * 400 + 10}" y="{10 + bar_height/2 + 5}" 
                      font-family="Arial" font-size="14" font-weight="bold" fill="{self.colors['success']}">
                    €{margin_vat:,.2f}
                </text>
            </g>
            
            <!-- Savings -->
            <rect x="50" y="240" width="500" height="40" fill="{self.colors['success']}" opacity="0.1" rx="20"/>
            <text x="{width/2}" y="265" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="{self.colors['success']}">
                Poupança: €{savings:,.2f} ({(savings/normal_vat*100):.1f}%)
            </text>
        </svg>
        '''
        
        return svg
    
    def generate_trend_chart(self, calculation_results: List[Dict]) -> str:
        """Generate professional trend chart showing monthly margin evolution"""
        if not calculation_results:
            return ''
        
        # Group data by month for proper trend analysis
        monthly_data = {}
        
        for calc in calculation_results:
            # Get date from the calculation
            date_str = calc.get('date', calc.get('invoice_date', ''))
            if not date_str:
                continue
                
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
            except:
                continue
                
            month_key = date.strftime('%Y-%m')
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    'sales': 0,
                    'costs': 0,
                    'margin': 0,
                    'count': 0,
                    'margin_percentages': []
                }
            
            monthly_data[month_key]['sales'] += calc.get('sale_amount', 0)
            monthly_data[month_key]['costs'] += calc.get('total_allocated_costs', 0)
            monthly_data[month_key]['margin'] += calc.get('gross_margin', 0)
            monthly_data[month_key]['count'] += 1
            
            # Calculate margin percentage
            if calc.get('sale_amount', 0) > 0:
                margin_pct = (calc.get('gross_margin', 0) / calc.get('sale_amount', 0)) * 100
                monthly_data[month_key]['margin_percentages'].append(margin_pct)
        
        # Convert to sorted list
        months = sorted(monthly_data.items())
        
        if not months:
            return ''
        
        # SVG setup
        width = 800
        height = 400
        margin = {'top': 60, 'right': 120, 'bottom': 80, 'left': 80}
        chart_width = width - margin['left'] - margin['right']
        chart_height = height - margin['top'] - margin['bottom']
        
        # Calculate scales
        max_value = max(max(m[1]['sales'], m[1]['margin']) for m in months)
        max_pct = max(
            sum(m[1]['margin_percentages']) / len(m[1]['margin_percentages']) 
            if m[1]['margin_percentages'] else 0 
            for m in months
        )
        
        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
            <rect width="{width}" height="{height}" fill="white"/>
            
            <!-- Title -->
            <text x="{width/2}" y="30" text-anchor="middle" font-family="Arial" font-size="18" font-weight="bold" fill="{self.colors['dark']}">
                Análise de Tendências Mensais
            </text>
            <text x="{width/2}" y="50" text-anchor="middle" font-family="Arial" font-size="12" fill="{self.colors['gray']}">
                Período: {months[0][0]} a {months[-1][0]}
            </text>
            
            <!-- Grid -->
            <g stroke="{self.colors['light']}" stroke-width="1" stroke-dasharray="2,2">
        '''
        
        # Y-axis grid and labels (left - values)
        for i in range(6):
            y = margin['top'] + chart_height - (i * chart_height / 5)
            value = i * max_value / 5
            svg += f'<line x1="{margin["left"]}" y1="{y}" x2="{width - margin["right"]}" y2="{y}"/>'
            svg += f'''<text x="{margin["left"] - 10}" y="{y + 5}" text-anchor="end" 
                        font-family="Arial" font-size="11" fill="{self.colors['gray']}">
                        €{value:,.0f}
                    </text>'''
        
        # Y-axis labels (right - percentages)
        for i in range(6):
            y = margin['top'] + chart_height - (i * chart_height / 5)
            pct = i * max_pct / 5
            svg += f'''<text x="{width - margin["right"] + 10}" y="{y + 5}" text-anchor="start" 
                        font-family="Arial" font-size="11" fill="{self.colors['purple']}">
                        {pct:.0f}%
                    </text>'''
        
        svg += '</g>'
        
        # Draw data
        if len(months) > 1:
            # Create path data for each metric
            sales_path = []
            margin_path = []
            pct_points = []
            
            for i, (month_key, data) in enumerate(months):
                x = margin['left'] + (i * chart_width / (len(months) - 1))
                
                # Sales line
                y_sales = margin['top'] + chart_height - (data['sales'] / max_value * chart_height)
                sales_path.append(f"{x},{y_sales}")
                
                # Margin line
                y_margin = margin['top'] + chart_height - (data['margin'] / max_value * chart_height)
                margin_path.append(f"{x},{y_margin}")
                
                # Margin percentage points
                avg_pct = sum(data['margin_percentages']) / len(data['margin_percentages']) if data['margin_percentages'] else 0
                y_pct = margin['top'] + chart_height - (avg_pct / max_pct * chart_height)
                pct_points.append((x, y_pct, avg_pct))
                
                # X-axis labels
                if i % max(1, len(months) // 8) == 0:
                    month_name = datetime.strptime(month_key, '%Y-%m').strftime('%b %Y')
                    svg += f'''
                    <text x="{x}" y="{margin['top'] + chart_height + 20}" text-anchor="middle" 
                          font-family="Arial" font-size="10" fill="{self.colors['gray']}">
                        {month_name}
                    </text>
                    '''
            
            # Draw filled areas
            svg += f'''
            <!-- Sales area -->
            <path d="M {sales_path[0]} L {' L '.join(sales_path)} L {margin['left'] + chart_width},{margin['top'] + chart_height} L {margin['left']},{margin['top'] + chart_height} Z"
                  fill="{self.colors['success']}" opacity="0.1"/>
            
            <!-- Margin area -->
            <path d="M {margin_path[0]} L {' L '.join(margin_path)} L {margin['left'] + chart_width},{margin['top'] + chart_height} L {margin['left']},{margin['top'] + chart_height} Z"
                  fill="{self.colors['info']}" opacity="0.2"/>
            '''
            
            # Draw lines
            svg += f'''
            <!-- Sales line -->
            <polyline points="{' '.join(sales_path)}" 
                      stroke="{self.colors['success']}" stroke-width="3" fill="none"/>
            
            <!-- Margin line -->
            <polyline points="{' '.join(margin_path)}" 
                      stroke="{self.colors['info']}" stroke-width="3" fill="none"/>
            '''
            
            # Draw percentage line and points
            for i, (x, y, pct) in enumerate(pct_points):
                if i > 0:
                    prev_x, prev_y, _ = pct_points[i-1]
                    svg += f'''<line x1="{prev_x}" y1="{prev_y}" x2="{x}" y2="{y}" 
                               stroke="{self.colors['purple']}" stroke-width="2" stroke-dasharray="5,5"/>'''
                
                # Percentage points with values
                svg += f'''
                <circle cx="{x}" cy="{y}" r="5" fill="{self.colors['purple']}" stroke="white" stroke-width="2"/>
                <text x="{x}" y="{y - 10}" text-anchor="middle" font-family="Arial" font-size="9" 
                      fill="{self.colors['purple']}" font-weight="bold">{pct:.1f}%</text>
                '''
        
        # Legend
        svg += f'''
            <g transform="translate({width - 110}, {margin['top'] + 20})">
                <rect x="0" y="0" width="100" height="80" fill="white" stroke="{self.colors['light']}" rx="5"/>
                
                <line x1="10" y1="15" x2="30" y2="15" stroke="{self.colors['success']}" stroke-width="3"/>
                <text x="35" y="19" font-family="Arial" font-size="11" fill="{self.colors['dark']}">Vendas</text>
                
                <line x1="10" y1="35" x2="30" y2="35" stroke="{self.colors['info']}" stroke-width="3"/>
                <text x="35" y="39" font-family="Arial" font-size="11" fill="{self.colors['dark']}">Margem</text>
                
                <line x1="10" y1="55" x2="30" y2="55" stroke="{self.colors['purple']}" stroke-width="2" stroke-dasharray="5,5"/>
                <text x="35" y="59" font-family="Arial" font-size="11" fill="{self.colors['dark']}">Margem %</text>
            </g>
        '''
        
        # Axes
        svg += f'''
            <line x1="{margin['left']}" y1="{margin['top']}" x2="{margin['left']}" y2="{margin['top'] + chart_height}" 
                  stroke="{self.colors['dark']}" stroke-width="2"/>
            <line x1="{margin['left']}" y1="{margin['top'] + chart_height}" x2="{width - margin['right']}" y2="{margin['top'] + chart_height}" 
                  stroke="{self.colors['dark']}" stroke-width="2"/>
            
            <!-- Y-axis titles -->
            <text x="25" y="{height/2}" transform="rotate(-90 25 {height/2})" text-anchor="middle"
                  font-family="Arial" font-size="12" fill="{self.colors['dark']}">Valores (€)</text>
            <text x="{width - 25}" y="{height/2}" transform="rotate(90 {width - 25} {height/2})" text-anchor="middle"
                  font-family="Arial" font-size="12" fill="{self.colors['purple']}">Margem %</text>
        </svg>
        '''
        
        return svg
    

    def generate_html_report(
        self,
        session_data: Dict[str, Any],
        calculation_results: List[Dict],
        vat_rate: float,
        final_results: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build premium HTML report that serves as preview and PDF template."""
        final_results = final_results or {}

        if company_info and not isinstance(company_info, dict):
            if hasattr(company_info, "model_dump"):
                company_info = company_info.model_dump()
            elif hasattr(company_info, "dict"):
                company_info = company_info.dict()
            else:
                company_info = {}

        company = self._normalize_company_info(session_data, company_info)
        report_title = f"Relatório IVA sobre Margem - {company['name']}"

        is_period_mode = final_results.get('calculationType') == 'period'
        chart_data = final_results.copy()
        if is_period_mode:
            chart_data['grossMargin'] = final_results.get('compensatedMargin', final_results.get('grossMargin', 0))
            chart_data['calculationType'] = 'period'

        bar_chart = self.generate_advanced_bar_chart(chart_data)
        pie_chart = self.generate_pie_chart(chart_data)
        comparison_chart = self.generate_comparison_chart(chart_data, vat_rate)

        total_sales = final_results.get('totalSales', 0.0) or 0.0
        total_costs = final_results.get('totalCosts', 0.0) or 0.0
        gross_margin = final_results.get('grossMargin', 0.0) or 0.0
        net_margin = final_results.get('netMargin', gross_margin - (gross_margin * (vat_rate / 100))) or 0.0
        total_vat = final_results.get('totalVAT', max(gross_margin, 0) * vat_rate / 100)
        normal_vat = total_sales * vat_rate / 100
        vat_savings = normal_vat - total_vat
        margin_percentage = (gross_margin / total_sales * 100) if total_sales else 0.0

        period_info = final_results.get('period', {}) if is_period_mode else {}
        compensated_margin = final_results.get('compensatedMargin', gross_margin) if is_period_mode else gross_margin
        previous_negative = final_results.get('previousNegative', 0.0)
        carry_forward = final_results.get('carryForward', 0.0)

        data_quality = self._summarize_data_quality(session_data, calculation_results)

        timestamp_local = datetime.now().strftime('%d/%m/%Y %H:%M')
        timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
        report_hash = self._compute_report_hash(session_data, final_results, vat_rate)

        summary_metrics = [
            {
                'label': 'Volume Total de Vendas',
                'value': self._format_currency(total_sales),
                'icon': '💶',
                'tone': '#dbeafe',
                'description': 'Total de receitas sujeitas ao regime de margem',
            },
            {
                'label': 'Custos Diretos Afetos',
                'value': self._format_currency(total_costs),
                'icon': '💼',
                'tone': '#fee2e2',
                'description': 'Custos diretos afetos às vendas analisadas',
            },
            {
                'label': 'Margem Bruta',
                'value': self._format_currency(gross_margin),
                'icon': '📊',
                'tone': '#ede9fe',
                'description': 'Vendas menos custos diretos afetos',
            },
            {
                'label': f'IVA sobre Margem ({vat_rate:.0f}%)',
                'value': self._format_currency(total_vat),
                'icon': '🧾',
                'tone': '#dcfce7',
                'description': 'Imposto devido segundo o regime especial',
            },
            {
                'label': 'Margem Líquida',
                'value': self._format_currency(net_margin),
                'icon': '🏦',
                'tone': '#fef3c7',
                'description': 'Resultado após liquidação de IVA sobre a margem',
            },
            {
                'label': 'Margem / Vendas',
                'value': f"{margin_percentage:.1f}%",
                'icon': '📈',
                'tone': '#cffafe',
                'description': 'Indicador de performance comercial',
            },
        ]

        summary_cards = ''.join(
            f"""
            <div class="metric-card" style="border-top: 4px solid {self.colors['primary']};">
                <div class="icon" style="background:{metric['tone']};">{metric['icon']}</div>
                <div class="value">{metric['value']}</div>
                <div class="label">{metric['label']}</div>
                <div class="description">{metric['description']}</div>
            </div>
            """
            for metric in summary_metrics
        )

        detailed_rows = []
        max_rows = min(30, len(calculation_results))
        for index, result in enumerate(calculation_results[:max_rows]):
            sale_amount = result.get('sale_amount', 0.0) or 0.0
            gross_margin_item = result.get('gross_margin', 0.0) or 0.0
            margin_pct = (gross_margin_item / sale_amount * 100) if sale_amount else 0.0
            badge_class = 'badge-success' if margin_pct > 20 else 'badge-warning' if margin_pct > 10 else 'badge-info'
            row_class = 'row-alt' if index % 2 else ''
            detailed_rows.append(
                f"""
                <tr class="{row_class}">
                    <td><strong>{result.get('invoice_number', '')}</strong></td>
                    <td>{result.get('date', '')}</td>
                    <td>{(result.get('client', '') or '')[:35]}{'...' if len(result.get('client', '') or '') > 35 else ''}</td>
                    <td class="value">{self._format_currency(sale_amount)}</td>
                    <td class="value">{self._format_currency(result.get('total_allocated_costs', 0.0))}</td>
                    <td class="value" style="color: {'#16a34a' if gross_margin_item > 0 else '#dc2626'};">{self._format_currency(gross_margin_item)}</td>
                    <td class="value">{self._format_currency(result.get('vat_amount', 0.0))}</td>
                    <td class="value"><span class="badge {badge_class}">{margin_pct:.1f}%</span></td>
                </tr>
                """
            )

        detailed_rows_html = "\n".join(detailed_rows) or (
            '<tr><td colspan="8" class="value">Sem documentos processados.</td></tr>'
        )

        if is_period_mode:
            period_section = f"""
            <section class="section highlighted" id="period-summary">
                <h2 class="section-title">📅 Síntese do Período Fiscal</h2>
                <div class="period-grid">
                    <div class="period-card">
                        <span class="label">Período de análise</span>
                        <span class="value">{period_info.get('start', '') or 'Sem data'} a {period_info.get('end', '') or 'Sem data'}</span>
                        <span class="caption">Quarter {period_info.get('quarter', '') or '-'} / {period_info.get('year', '') or '-'}</span>
                    </div>
                    <div class="period-card">
                        <span class="label">Margem bruta do período</span>
                        <span class="value">{self._format_currency(gross_margin)}</span>
                        <span class="caption">Antes de compensações</span>
                    </div>
                    <div class="period-card">
                        <span class="label">(-) Margem negativa anterior</span>
                        <span class="value negative">{self._format_currency(previous_negative)}</span>
                        <span class="caption">Transporte de períodos anteriores</span>
                    </div>
                    <div class="period-card">
                        <span class="label">(=) Margem compensada</span>
                        <span class="value">{self._format_currency(compensated_margin)}</span>
                        <span class="caption">Base tributável após compensação</span>
                    </div>
                    <div class="period-card">
                        <span class="label">IVA a pagar ({vat_rate:.0f}%)</span>
                        <span class="value">{self._format_currency(total_vat)}</span>
                        <span class="caption">Valor devido no período</span>
                    </div>
                    <div class="period-card">
                        <span class="label">Margem a transportar</span>
                        <span class="value">{self._format_currency(carry_forward)}</span>
                        <span class="caption">Saldo para período seguinte</span>
                    </div>
                </div>
                <div class="compliance-box">
                    <strong>⚖️ Conformidade legal:</strong>
                    Cálculo efetuado segundo o Art.º 308.º do Código do IVA e orientações da Autoridade Tributária para o regime de margem.
                </div>
            </section>
            """
        else:
            period_section = ""

        data_quality_cards = f"""
        <div class="quality-grid">
            <div class="quality-card">
                <span class="label">Documentos de venda</span>
                <span class="value">{data_quality['sales_count']}</span>
            </div>
            <div class="quality-card">
                <span class="label">Documentos de custo</span>
                <span class="value">{data_quality['cost_count']}</span>
            </div>
            <div class="quality-card">
                <span class="label">Cálculos gerados</span>
                <span class="value">{data_quality['calculation_count']}</span>
            </div>
            <div class="quality-card">
                <span class="label">Custos sem associação</span>
                <span class="value">{data_quality['unlinked_costs_count']}</span>
                <span class="caption">{self._format_currency(data_quality['unlinked_costs_total'])}</span>
            </div>
            <div class="quality-card">
                <span class="label">Vendas sem custos atribuídos</span>
                <span class="value">{data_quality['unlinked_sales_count']}</span>
            </div>
        </div>
        """

        savings_percentage = (vat_savings / normal_vat * 100) if normal_vat else 0.0
        currency_formatter = self._format_currency
        keywords = ", ".join(
            [value for value in [
                "IVA",
                "Margem",
                "Regime Especial",
                company.get('name'),
                str(company.get('nif')) if company.get('nif') else None,
            ] if value]
        )

        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-PT">
        <head>
            <meta charset="UTF-8" />
            <meta name="author" content="{company['name']}" />
            <meta name="description" content="Relatório premium gerado em {timestamp_local} sobre o regime especial de IVA na margem." />
            <meta name="created" content="{timestamp_utc}" />
            <meta name="keywords" content="{keywords}" />
            <title>{report_title}</title>
            <style>
                {self._font_face_block()}

                :root {{
                    --color-primary: {self.colors['primary']};
                    --color-accent: {self.colors['info']};
                    --color-success: {self.colors['success']};
                    --color-danger: {self.colors['danger']};
                    --color-muted: {self.colors['gray']};
                    --font-family: 'ReportPrimary', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
                }}

                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}

                body {{
                    font-family: var(--font-family);
                    line-height: 1.6;
                    color: #1f2937;
                    background-color: #ffffff;
                    -webkit-print-color-adjust: exact;
                    print-color-adjust: exact;
                }}

                .print-btn {{
                    position: fixed;
                    bottom: 32px;
                    right: 32px;
                    background: var(--color-primary);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 9999px;
                    font-size: 0.95rem;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 10px 25px rgba(30, 64, 175, 0.25);
                    z-index: 10;
                }}

                .print-btn:hover {{
                    background: #1d4ed8;
                }}

                .cover {{
                    background: linear-gradient(140deg, #0f172a 0%, var(--color-primary) 50%, #3b82f6 100%);
                    color: white;
                    padding: 64px 72px;
                    border-radius: 0 0 24px 24px;
                    margin-bottom: 48px;
                }}

                .cover h1 {{
                    font-size: 2.8rem;
                    margin-bottom: 16px;
                    letter-spacing: -0.02em;
                }}

                .cover .company {{
                    margin-top: 24px;
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                    font-size: 0.95rem;
                    opacity: 0.9;
                }}

                .cover .meta {{
                    margin-top: 32px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 16px;
                    font-size: 0.9rem;
                    opacity: 0.85;
                }}

                .container {{
                    max-width: 1160px;
                    margin: 0 auto;
                    padding: 0 40px 60px 40px;
                }}

                .section {{
                    background: white;
                    border-radius: 16px;
                    padding: 32px;
                    margin-bottom: 32px;
                    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.06);
                }}

                .section.highlighted {{
                    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                    border: 1px solid #bae6fd;
                }}

                .section-title {{
                    font-size: 1.6rem;
                    font-weight: 700;
                    margin-bottom: 24px;
                    color: var(--color-primary);
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }}

                .section-title::before {{
                    content: '';
                    width: 4px;
                    height: 24px;
                    background: var(--color-accent);
                    border-radius: 999px;
                }}

                .metrics-dashboard {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 24px;
                }}

                .metric-card {{
                    background: white;
                    border-radius: 16px;
                    padding: 24px;
                    box-shadow: 0 10px 32px rgba(15, 23, 42, 0.08);
                    text-align: center;
                    transition: transform 0.2s ease;
                }}

                .metric-card .icon {{
                    width: 52px;
                    height: 52px;
                    border-radius: 14px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 26px;
                    margin: 0 auto 12px;
                }}

                .metric-card .value {{
                    font-size: 1.9rem;
                    font-weight: 700;
                    letter-spacing: -0.02em;
                }}

                .metric-card .label {{
                    margin-top: 6px;
                    font-weight: 600;
                    color: #334155;
                }}

                .metric-card .description {{
                    font-size: 0.85rem;
                    margin-top: 8px;
                    color: var(--color-muted);
                }}

                .period-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                    gap: 20px;
                    margin-bottom: 24px;
                }}

                .period-card {{
                    background: rgba(255, 255, 255, 0.9);
                    border-radius: 14px;
                    padding: 20px;
                    box-shadow: 0 6px 24px rgba(14, 165, 233, 0.18);
                }}

                .period-card .label {{
                    font-size: 0.85rem;
                    text-transform: uppercase;
                    color: var(--color-muted);
                    letter-spacing: 0.08em;
                }}

                .period-card .value {{
                    display: block;
                    font-size: 1.4rem;
                    font-weight: 700;
                    margin-top: 8px;
                }}

                .period-card .value.negative {{
                    color: var(--color-danger);
                }}

                .period-card .caption {{
                    font-size: 0.8rem;
                    margin-top: 8px;
                    color: #0f172a;
                }}

                .compliance-box {{
                    padding: 18px 22px;
                    border-radius: 12px;
                    background: rgba(14, 165, 233, 0.12);
                    color: #075985;
                    font-size: 0.95rem;
                    line-height: 1.5;
                }}

                .chart-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
                    gap: 24px;
                }}

                .chart-card {{
                    background: #f8fafc;
                    padding: 20px;
                    border-radius: 16px;
                    box-shadow: inset 0 1px 0 rgba(148, 163, 184, 0.15);
                }}

                .comparison-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin-top: 24px;
                }}

                .comparison-card {{
                    background: #f8fafc;
                    border-radius: 12px;
                    padding: 18px;
                    border: 1px solid #e2e8f0;
                }}

                .comparison-card strong {{
                    display: block;
                    font-size: 1.1rem;
                    margin-top: 8px;
                }}

                .comparison-card span {{
                    font-size: 0.9rem;
                    color: var(--color-muted);
                }}

                table.data-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                    font-size: 0.88rem;
                }}

                table.data-table th {{
                    background: #0f172a;
                    color: white;
                    padding: 12px 16px;
                    text-align: left;
                }}

                table.data-table td {{
                    padding: 12px 16px;
                    border-bottom: 1px solid #e2e8f0;
                }}

                table.data-table tr.row-alt {{
                    background: #f8fafc;
                }}

                table.data-table td.value {{
                    text-align: right;
                    font-variant-numeric: tabular-nums;
                }}

                .badge {{
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 0.75rem;
                    font-weight: 600;
                }}

                .badge-success {{
                    background: #dcfce7;
                    color: #166534;
                }}

                .badge-warning {{
                    background: #fef3c7;
                    color: #c2410c;
                }}

                .badge-info {{
                    background: #dbeafe;
                    color: #1d4ed8;
                }}

                .quality-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 16px;
                    margin-top: 16px;
                }}

                .quality-card {{
                    background: #f8fafc;
                    border-radius: 12px;
                    padding: 16px;
                    border: 1px solid #e2e8f0;
                }}

                .quality-card .label {{
                    font-size: 0.8rem;
                    color: var(--color-muted);
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                }}

                .quality-card .value {{
                    display: block;
                    font-size: 1.4rem;
                    font-weight: 700;
                    margin-top: 6px;
                }}

                .quality-card .caption {{
                    font-size: 0.8rem;
                    color: var(--color-muted);
                }}

                .footer {{
                    padding: 32px 40px 60px 40px;
                    text-align: center;
                    color: var(--color-muted);
                    font-size: 0.85rem;
                }}

                .footer .hash {{
                    margin-top: 12px;
                    font-family: 'Roboto Mono', 'Courier New', monospace;
                    color: #94a3b8;
                }}

                @media print {{
                    .print-btn {{
                        display: none;
                    }}

                    .cover {{
                        border-radius: 0;
                        margin-bottom: 24px;
                    }}

                    .section {{
                        box-shadow: none;
                        padding: 24px;
                        page-break-inside: avoid;
                    }}

                    .page-break {{
                        page-break-after: always;
                    }}
                }}
            </style>
        </head>
        <body>
            <button class="print-btn no-print" onclick="window.print()">🖨️ Imprimir / Guardar PDF</button>
            <section class="cover">
                <h1>{report_title}</h1>
                <p>Relatório premium preparado para equipas de contabilidade e consultoria financeira.</p>
                <div class="company">
                    <span><strong>Entidade:</strong> {company['name']}</span>
                    <span><strong>NIF:</strong> {company['nif']}</span>
                    <span><strong>Sede:</strong> {company['address']} {company['postal_code']} {company['city']}</span>
                    <span><strong>Contacto:</strong> {company['phone']} · {company['email']}</span>
                </div>
                <div class="meta">
                    <span>Gerado em {timestamp_local} ({timestamp_utc})</span>
                    <span>Taxa de IVA considerada: {vat_rate:.2f}%</span>
                    <span>Identificador do relatório: {report_hash}</span>
                </div>
            </section>
            <div class="container">
                <section class="section" id="executive-summary">
                    <h2 class="section-title">Resumo Executivo</h2>
                    <p>Este relatório consolida a análise de margem e IVA de acordo com o regime especial das agências de viagens (Art.º 308.º do CIVA). Os indicadores seguintes apresentam a fotografia global do período avaliado.</p>
                    <div class="metrics-dashboard">
                        {summary_cards}
                    </div>
                </section>
                {period_section}
                <section class="section" id="charts">
                    <h2 class="section-title">Visualização Analítica</h2>
                    <div class="chart-grid">
                        <div class="chart-card">
                            <h3>Distribuição Financeira</h3>
                            {bar_chart}
                        </div>
                        <div class="chart-card">
                            <h3>Composição da Margem</h3>
                            {pie_chart or '<p style="color:#64748b;">Sem dados suficientes para o gráfico.</p>'}
                        </div>
                        <div class="chart-card">
                            <h3>Comparativo Regime Margem vs. Regime Normal</h3>
                            {comparison_chart}
                        </div>
                    </div>
                    <div class="comparison-grid">
                        <div class="comparison-card">
                            <span>IVA estimado no regime normal</span>
                            <strong>{currency_formatter(normal_vat)}</strong>
                        </div>
                        <div class="comparison-card">
                            <span>IVA devido no regime de margem</span>
                            <strong>{currency_formatter(total_vat)}</strong>
                        </div>
                        <div class="comparison-card">
                            <span>Poupança fiscal estimada</span>
                            <strong style="color: var(--color-success);">{currency_formatter(vat_savings)}</strong>
                        </div>
                        <div class="comparison-card">
                            <span>Poupança percentual</span>
                            <strong>{savings_percentage:.1f}%</strong>
                        </div>
                    </div>
                </section>
                <section class="section page-break" id="detail">
                    <h2 class="section-title">Análise Detalhada por Documento</h2>
                    <p>Apresentamos os primeiros {max_rows} registos de um total de {len(calculation_results)} documentos com margem apurada. Consulte a exportação Excel para o detalhe completo.</p>
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
                            {detailed_rows_html}
                        </tbody>
                    </table>
                </section>
                <section class="section" id="data-quality">
                    <h2 class="section-title">Integridade & Observações</h2>
                    <p>Monitorizamos a integridade dos dados importados para suportar auditorias futuras e garantir rastreabilidade das decisões fiscais.</p>
                    {data_quality_cards}
                    <div class="compliance-box" style="margin-top: 24px; background: rgba(34, 197, 94, 0.12); color: #14532d;">
                        <strong>Nota profissional:</strong> Recomenda-se validar manualmente documentos sem custos afetos ou com margens negativas para assegurar correta imputação antes da submissão da declaração periódica de IVA.
                    </div>
                </section>
            </div>
            <footer class="footer">
                <p>Relatório gerado automaticamente pelo motor IVA Margem Premium. Não dispensa a análise de um contabilista certificado.</p>
                <p>Art.º 308.º do Código do IVA · Regime especial das agências de viagens · Documento preparado para utilização profissional.</p>
                <div class="hash">Trace ID: {report_hash}</div>
            </footer>
            <script>
                if (window.location.search.includes('autoprint=true')) {{
                    window.print();
                }}
            </script>
        </body>
        </html>
        """
        return html_content

    def generate_report(
        self,
        session_data: Dict[str, Any],
        calculation_results: List[Dict],
        vat_rate: float,
        final_results: Dict[str, Any],
        company_info: Optional[Dict[str, Any]] = None,
    ) -> bytes:
        html = self.generate_html_report(session_data, calculation_results, vat_rate, final_results, company_info)
        return html.encode('utf-8')


def generate_pdf_report(session_data: Dict[str, Any], calculation_results: List[Dict], 
                       vat_rate: float, final_results: Dict[str, Any],
                       company_info: Optional[Dict[str, Any]] = None) -> bytes:
    """Generate professional PDF report with expert-level visualizations"""
    generator = ProfessionalReportGenerator()
    return generator.generate_report(session_data, calculation_results, vat_rate, final_results, company_info)
