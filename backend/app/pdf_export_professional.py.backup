"""
Professional PDF Export module for IVA Margem Turismo
Expert-level data visualization with 30 years of experience
"""
import io
import math
from datetime import datetime
from typing import Dict, List, Any
import logging

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
    
    def generate_report(self, session_data: Dict[str, Any], calculation_results: List[Dict], 
                       vat_rate: float, final_results: Dict[str, float]) -> bytes:
        """Generate professional PDF report with multiple visualizations"""
        
        # Check if period calculation mode
        is_period_mode = final_results.get('calculationType') == 'period'
        
        # Adjust chart data for period mode
        chart_data = final_results.copy()
        if is_period_mode:
            # For period mode, show compensated margin in charts
            chart_data['grossMargin'] = final_results.get('compensatedMargin', final_results.get('grossMargin', 0))
            chart_data['calculationType'] = 'period'
        
        # Generate all charts
        bar_chart = self.generate_advanced_bar_chart(chart_data)
        pie_chart = self.generate_pie_chart(chart_data)
        comparison_chart = self.generate_comparison_chart(chart_data, vat_rate)
        # trend_chart = self.generate_trend_chart(calculation_results)  # Removido conforme solicitado
        
        # Calculate key metrics
        total_documents = len(session_data.get('sales', []))
        total_costs_docs = len(session_data.get('costs', []))
        margin_percentage = (final_results.get('grossMargin', 0) / final_results.get('totalSales', 1) * 100) if final_results.get('totalSales', 0) > 0 else 0
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="pt-PT">
        <head>
            <meta charset="UTF-8">
            <title>Relatório Profissional - IVA sobre Margem</title>
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
                
                .chart-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 24px;
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
                <!-- Header -->
                <div class="header">
                    <h1>Relatório IVA sobre Margem</h1>
                    <p class="subtitle">Regime Especial - Artigo 308º do CIVA</p>
                    <p class="subtitle">{datetime.now().strftime('%d de %B de %Y às %H:%M')}</p>
                </div>
                
                <!-- Key Metrics Dashboard -->
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
                    <h2 class="section-title" style="color: #0369a1;">📅 Cálculo por Período Fiscal</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div style="background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 8px;">Período de Análise</div>
                            <div style="font-size: 1.3em; font-weight: 700; color: #0369a1;">
                                {final_results.get('period', {}).get('start', '')} a {final_results.get('period', {}).get('end', '')}
                            </div>
                            {"<div style='font-size: 0.85em; color: #0891b2; margin-top: 4px;'>Trimestre " + str(final_results.get('period', {}).get('quarter', '')) + "/" + str(final_results.get('period', {}).get('year', '')) + "</div>" if final_results.get('period', {}).get('quarter') else ""}
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
                    <h2 class="section-title">Análise Financeira Completa</h2>
                    <div class="chart-container">
                        {bar_chart}
                    </div>
                </div>
                
                <!-- Comparison and Distribution -->
                <div class="chart-grid">
                    <div class="section">
                        <h2 class="section-title">Comparação de Regimes</h2>
                        <div class="chart-container">
                            {comparison_chart}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2 class="section-title">Distribuição de Valores</h2>
                        <div class="chart-container">
                            {pie_chart}
                        </div>
                    </div>
                </div>
                
                <!-- Savings Highlight -->
                <div class="highlight-box">
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
                    <h2 class="section-title">Análise Detalhada por Documento</h2>
                    <p style="color: #6b7280; margin-bottom: 20px;">
                        Apresentamos os primeiros {min(30, len(calculation_results))} documentos de um total de {len(calculation_results)} processados.
                        Para a lista completa, consulte o ficheiro Excel exportado.
                    </p>
                    
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
        
        html_content += """
                        </tbody>
                    </table>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 60px; padding: 40px; background: #f9fafb; border-radius: 12px;">
                    <h3 style="margin-bottom: 12px; color: #1f2937;">Accounting Advantage</h3>
                    <p style="color: #6b7280; max-width: 600px; margin: 0 auto;">
                        Sistema Profissional de Cálculo de IVA sobre Margem<br>
                        Este relatório foi gerado automaticamente e não substitui aconselhamento fiscal profissional.<br>
                        <strong>Consulte sempre o seu contabilista certificado.</strong>
                    </p>
                </div>
            </div>
            
            <script>
                // Auto print dialog
                if (window.location.search.includes('autoprint=true')) {
                    window.print();
                }
                
                // Smooth scroll
                document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                    anchor.addEventListener('click', function (e) {
                        e.preventDefault();
                        document.querySelector(this.getAttribute('href')).scrollIntoView({
                            behavior: 'smooth'
                        });
                    });
                });
            </script>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')


def generate_pdf_report(session_data: Dict[str, Any], calculation_results: List[Dict], 
                       vat_rate: float, final_results: Dict[str, float]) -> bytes:
    """Generate professional PDF report with expert-level visualizations"""
    generator = ProfessionalReportGenerator()
    return generator.generate_report(session_data, calculation_results, vat_rate, final_results)