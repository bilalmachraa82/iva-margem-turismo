"""
Professional Chart Generator for PDF Reports
Industry-standard financial charts with proper formatting
"""

import io
import base64
from typing import Dict, List, Any, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Wedge
import numpy as np
import seaborn as sns
from pathlib import Path
import logging

# Configure matplotlib for high-quality output
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'font.size': 10,
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.5,
    'patch.linewidth': 0.5,
    'xtick.major.width': 0.8,
    'ytick.major.width': 0.8,
    'xtick.minor.width': 0.4,
    'ytick.minor.width': 0.4,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})

logger = logging.getLogger(__name__)

class ProfessionalChartGenerator:
    """Generate publication-quality financial charts"""

    # Professional color schemes
    FINANCIAL_COLORS = {
        'primary': '#2563eb',      # Professional blue
        'secondary': '#1e40af',    # Dark blue
        'success': '#10b981',      # Green for positive
        'warning': '#f59e0b',      # Amber for attention
        'danger': '#ef4444',       # Red for negative
        'neutral': '#6b7280',      # Gray for neutral
        'background': '#f8fafc',   # Light background
        'text': '#1f2937'          # Dark text
    }

    CHART_STYLE = {
        'figure_size': (12, 8),
        'title_size': 16,
        'label_size': 12,
        'tick_size': 10,
        'legend_size': 11,
        'grid_alpha': 0.3,
        'bar_alpha': 0.8
    }

    def __init__(self, company_colors: Optional[Dict[str, str]] = None):
        """Initialize with optional company branding colors"""
        if company_colors:
            self.colors = {**self.FINANCIAL_COLORS, **company_colors}
        else:
            self.colors = self.FINANCIAL_COLORS.copy()

    def create_waterfall_chart(self, data: Dict[str, float], title: str = "Análise Financeira") -> str:
        """Create professional waterfall chart for financial analysis"""

        fig, ax = plt.subplots(figsize=self.CHART_STYLE['figure_size'])

        # Prepare data
        categories = list(data.keys())
        values = list(data.values())

        # Calculate cumulative positions for waterfall
        cumulative = []
        running_total = 0

        for i, value in enumerate(values):
            if i == 0:  # First bar starts at 0
                cumulative.append(0)
                running_total = value
            else:
                # For negative values, position them correctly below previous total
                if value < 0:
                    cumulative.append(running_total + value)  # Start from below
                else:
                    cumulative.append(running_total)  # Start from current total
                running_total += value

        # Create bars
        colors = []
        for i, value in enumerate(values):
            if i == 0 or i == len(values) - 1:  # First and last bars
                colors.append(self.colors['primary'])
            elif value >= 0:
                colors.append(self.colors['success'])
            else:
                colors.append(self.colors['danger'])

        bars = ax.bar(range(len(categories)), values,
                     bottom=cumulative,
                     color=colors,
                     alpha=self.CHART_STYLE['bar_alpha'],
                     edgecolor='white',
                     linewidth=1)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()

            # Position label correctly for positive and negative values
            if value >= 0:
                label_y = bar.get_y() + height / 2
            else:
                label_y = bar.get_y() + height / 2  # Center in negative bar

            # Format value
            if abs(value) >= 1000:
                label = f"€{value/1000:.1f}K"
            else:
                label = f"€{value:.0f}"

            # Choose text color based on bar size and value
            max_abs_value = max(abs(v) for v in values)
            text_color = 'white' if abs(value) > max_abs_value * 0.1 else self.colors['text']

            ax.text(bar.get_x() + bar.get_width()/2, label_y,
                   label, ha='center', va='center',
                   fontweight='bold', fontsize=self.CHART_STYLE['label_size'],
                   color=text_color)

        # Add connecting lines
        for i in range(len(values) - 1):
            x1 = i + 0.4
            x2 = i + 0.6
            # Connect from top of current bar to start of next bar
            y_from = cumulative[i] + values[i]  # Top of current bar
            y_to = cumulative[i+1]  # Start of next bar
            ax.plot([x1, x2], [y_from, y_to], 'k--', alpha=0.5, linewidth=1)

        # Add zero line for reference
        ax.axhline(y=0, color=self.colors['neutral'], linestyle='-', linewidth=2, alpha=0.8)

        # Styling
        ax.set_title(title, fontsize=self.CHART_STYLE['title_size'],
                    fontweight='bold', pad=20, color=self.colors['text'])
        ax.set_xticks(range(len(categories)))
        ax.set_xticklabels(categories, rotation=45, ha='right',
                          fontsize=self.CHART_STYLE['tick_size'])

        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x/1000:.0f}K'))
        ax.tick_params(axis='y', labelsize=self.CHART_STYLE['tick_size'])

        # Grid and styling
        ax.grid(True, alpha=self.CHART_STYLE['grid_alpha'], linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.colors['neutral'])
        ax.spines['bottom'].set_color(self.colors['neutral'])

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_donut_chart(self, data: Dict[str, float], title: str = "Distribuição") -> str:
        """Create professional donut chart with modern styling"""

        fig, ax = plt.subplots(figsize=(10, 10))

        labels = list(data.keys())
        sizes = list(data.values())
        total = sum(sizes)

        # Professional color palette
        chart_colors = [
            self.colors['danger'],    # Costs (red)
            self.colors['warning'],   # IVA (amber)
            self.colors['success']    # Net margin (green)
        ]

        # Create donut chart
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%',
                                         colors=chart_colors,
                                         startangle=90,
                                         pctdistance=0.85,
                                         explode=(0.05, 0.05, 0.05),
                                         wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2))

        # Center circle for donut effect
        centre_circle = plt.Circle((0,0), 0.70, fc='white', linewidth=2, edgecolor=self.colors['neutral'])
        ax.add_artist(centre_circle)

        # Add total in center
        ax.text(0, 0.1, 'Total', ha='center', va='center',
               fontsize=14, fontweight='bold', color=self.colors['text'])
        ax.text(0, -0.1, f'€{total:,.0f}', ha='center', va='center',
               fontsize=18, fontweight='bold', color=self.colors['primary'])

        # Style percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')

        # Style labels
        for text in texts:
            text.set_fontsize(12)
            text.set_color(self.colors['text'])

        ax.set_title(title, fontsize=self.CHART_STYLE['title_size'],
                    fontweight='bold', pad=20, color=self.colors['text'])

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_comparison_chart(self, normal_iva: float, margin_iva: float,
                               title: str = "Comparação IVA") -> str:
        """Create horizontal bar chart comparing IVA regimes"""

        fig, ax = plt.subplots(figsize=(12, 6))

        categories = ['IVA Regime Normal', 'IVA Regime Margem']
        values = [normal_iva, margin_iva]
        savings = normal_iva - margin_iva
        savings_pct = (savings / normal_iva) * 100 if normal_iva > 0 else 0

        # Create horizontal bars
        bars = ax.barh(categories, values,
                      color=[self.colors['danger'], self.colors['success']],
                      alpha=self.CHART_STYLE['bar_alpha'],
                      edgecolor='white',
                      linewidth=2)

        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            ax.text(width + max(values) * 0.01, bar.get_y() + bar.get_height()/2,
                   f'€{value:,.0f}', ha='left', va='center',
                   fontweight='bold', fontsize=self.CHART_STYLE['label_size'])

        # Add savings annotation
        if savings > 0:
            ax.annotate(f'Poupança: €{savings:,.0f} ({savings_pct:.1f}%)',
                       xy=(margin_iva, 0), xytext=(normal_iva * 0.7, 0.5),
                       arrowprops=dict(arrowstyle='->', color=self.colors['success'], lw=2),
                       fontsize=14, fontweight='bold', color=self.colors['success'],
                       bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['success'], alpha=0.1))

        # Styling
        ax.set_title(title, fontsize=self.CHART_STYLE['title_size'],
                    fontweight='bold', pad=20, color=self.colors['text'])

        ax.set_xlabel('Valor de IVA (€)', fontsize=self.CHART_STYLE['label_size'])
        ax.tick_params(axis='both', labelsize=self.CHART_STYLE['tick_size'])

        # Format x-axis
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'€{x:,.0f}'))

        # Grid and styling
        ax.grid(True, alpha=self.CHART_STYLE['grid_alpha'], axis='x')
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color(self.colors['neutral'])

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def create_kpi_dashboard(self, kpis: Dict[str, Any]) -> str:
        """Create professional KPI dashboard with cards layout"""

        fig = plt.figure(figsize=(16, 10))

        # Create grid layout
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        # Define KPI cards
        kpi_configs = [
            {"key": "total_sales", "title": "Volume Total Vendas", "format": "currency", "color": "primary"},
            {"key": "total_costs", "title": "Custos Diretos", "format": "currency", "color": "danger"},
            {"key": "gross_margin", "title": "Margem Bruta", "format": "currency", "color": "success"},
            {"key": "vat_amount", "title": "IVA s/ Margem", "format": "currency", "color": "warning"},
            {"key": "net_margin", "title": "Margem Líquida", "format": "currency", "color": "success"},
            {"key": "margin_percentage", "title": "Margem %", "format": "percentage", "color": "primary"},
        ]

        positions = [(0,0), (0,1), (0,2), (1,0), (1,1), (1,2)]

        for i, (config, pos) in enumerate(zip(kpi_configs, positions)):
            if config["key"] in kpis:
                ax = fig.add_subplot(gs[pos[0], pos[1]])
                self._create_kpi_card(ax, kpis[config["key"]], config)

        # Add overall title
        fig.suptitle('Dashboard Executivo - KPIs Principais',
                    fontsize=20, fontweight='bold', y=0.95, color=self.colors['text'])

        plt.tight_layout()
        return self._fig_to_base64(fig)

    def _create_kpi_card(self, ax, value: float, config: Dict[str, str]):
        """Create individual KPI card"""

        # Format value
        if config["format"] == "currency":
            if abs(value) >= 1000000:
                display_value = f"€{value/1000000:.1f}M"
            elif abs(value) >= 1000:
                display_value = f"€{value/1000:.1f}K"
            else:
                display_value = f"€{value:.0f}"
        elif config["format"] == "percentage":
            display_value = f"{value:.1f}%"
        else:
            display_value = f"{value:,.0f}"

        # Create card background
        card_color = self.colors[config["color"]]
        ax.add_patch(patches.Rectangle((0, 0), 1, 1,
                                      facecolor=card_color, alpha=0.1,
                                      edgecolor=card_color, linewidth=2))

        # Add value (large)
        ax.text(0.5, 0.6, display_value, ha='center', va='center',
               fontsize=24, fontweight='bold', color=card_color)

        # Add title (smaller)
        ax.text(0.5, 0.3, config["title"], ha='center', va='center',
               fontsize=12, color=self.colors['text'], wrap=True)

        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight',
                   dpi=300, facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return img_base64

# Convenience function for easy integration
def generate_financial_charts(calculations: Dict[str, Any],
                             company_colors: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Generate all financial charts for PDF report"""

    generator = ProfessionalChartGenerator(company_colors)

    # Extract data for charts
    waterfall_data = {
        "Total Vendas": calculations.get("total_sales", 0),
        "Total Custos": -calculations.get("total_costs", 0),
        "Margem Bruta": calculations.get("gross_margin", 0),
        "IVA s/ Margem": -calculations.get("vat_amount", 0),
        "Margem Líquida": calculations.get("net_margin", 0)
    }

    donut_data = {
        "Custos Diretos": calculations.get("total_costs", 0),
        "IVA a Pagar": calculations.get("vat_amount", 0),
        "Margem Líquida": calculations.get("net_margin", 0)
    }

    kpi_data = {
        "total_sales": calculations.get("total_sales", 0),
        "total_costs": calculations.get("total_costs", 0),
        "gross_margin": calculations.get("gross_margin", 0),
        "vat_amount": calculations.get("vat_amount", 0),
        "net_margin": calculations.get("net_margin", 0),
        "margin_percentage": calculations.get("margin_percentage", 0)
    }

    return {
        "waterfall_chart": generator.create_waterfall_chart(waterfall_data),
        "donut_chart": generator.create_donut_chart(donut_data),
        "comparison_chart": generator.create_comparison_chart(
            calculations.get("normal_vat", 0),
            calculations.get("vat_amount", 0)
        ),
        "kpi_dashboard": generator.create_kpi_dashboard(kpi_data)
    }