"""
Period-based VAT Calculator for Portuguese Margin Scheme
Implements compensation of negative margins across periods
Compliant with CIVA Art. 308º and AT requirements
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, date
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PeriodVATCalculator:
    """
    Calculates VAT on margin with period-based compensation
    as required by Portuguese tax law for travel agencies
    """
    
    VAT_RATES = {
        'continental': Decimal('23'),    # Portugal Continental
        'madeira': Decimal('22'),        # Região Autónoma da Madeira
        'azores': Decimal('18'),         # Região Autónoma dos Açores
        'reduced': Decimal('6'),         # Taxa reduzida (alguns serviços)
        'intermediate': Decimal('13')    # Taxa intermédia
    }
    
    def __init__(self, region: str = 'continental'):
        """Initialize with regional VAT rate"""
        self.vat_rate = self.VAT_RATES.get(region, Decimal('23'))
        self.region = region
        
    def calculate_period_vat(
        self, 
        sales: List[Dict], 
        costs: List[Dict],
        associations: List[Dict],
        start_date: date,
        end_date: date,
        previous_negative_margin: Decimal = Decimal('0')
    ) -> Dict:
        """
        Calculate VAT for a specific period with margin compensation
        
        Args:
            sales: List of sales in the period
            costs: List of costs in the period  
            associations: Sale-cost associations
            start_date: Period start date
            end_date: Period end date
            previous_negative_margin: Negative margin from previous periods to compensate
            
        Returns:
            Dict with calculation results including VAT due and carry-forward margin
        """
        
        # Filter documents within period
        period_sales = [s for s in sales if self._in_period(s.get('date'), start_date, end_date)]
        period_costs = [c for c in costs if self._in_period(c.get('date'), start_date, end_date)]
        
        # Calculate total sales in period
        total_sales = Decimal('0')
        for sale in period_sales:
            sale_amount = Decimal(str(sale.get('amount', 0)))
            total_sales += sale_amount
        
        # Calculate total costs in period (ALL costs, not just associated ones)
        total_costs = Decimal('0')
        for cost in period_costs:
            cost_amount = Decimal(str(cost.get('amount', 0)))
            total_costs += cost_amount
        
        # Calculate period margin (can be negative)
        gross_margin = total_sales - total_costs
        
        # Track detailed margins for reporting (optional)
        sale_margins = []
        for sale in period_sales:
            sale_amount = Decimal(str(sale.get('amount', 0)))
            
            # Get associated costs
            sale_costs = self._get_sale_costs(sale, period_costs, associations)
            allocated_costs = Decimal('0')
            
            for cost in sale_costs:
                # Proportional allocation if cost is shared
                cost_amount = Decimal(str(cost.get('amount', 0)))
                num_linked_sales = len(cost.get('linked_sales', []))
                
                if num_linked_sales > 0:
                    allocated_amount = cost_amount / num_linked_sales
                    allocated_costs += allocated_amount
            
            margin = sale_amount - allocated_costs
            sale_margins.append({
                'sale_id': sale.get('id'),
                'sale_number': sale.get('number'),
                'amount': sale_amount,
                'costs': allocated_costs,
                'margin': margin
            })
        
        # Apply compensation from previous periods
        compensated_margin = gross_margin - previous_negative_margin
        
        # VAT is only due on positive margins
        vat_base = max(Decimal('0'), compensated_margin)
        vat_amount = vat_base * self.vat_rate / 100
        
        # Carry forward negative margin if any
        carry_forward = min(Decimal('0'), compensated_margin)
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            },
            'region': self.region,
            'vat_rate': float(self.vat_rate),
            'totals': {
                'sales': float(total_sales),
                'costs': float(total_costs),
                'gross_margin': float(gross_margin),
                'previous_negative': float(previous_negative_margin),
                'compensated_margin': float(compensated_margin),
                'vat_base': float(vat_base),
                'vat_amount': float(vat_amount),
                'carry_forward': float(carry_forward)
            },
            'details': sale_margins,
            'compliance': {
                'calculation_method': 'period_compensation',
                'legal_basis': 'CIVA Art. 308º',
                'allows_compensation': True,
                'negative_margin_treatment': 'carry_forward_to_next_period'
            }
        }
    
    def calculate_quarterly_vat(
        self,
        year: int,
        quarter: int,
        sales: List[Dict],
        costs: List[Dict],
        associations: List[Dict],
        previous_negative: Decimal = Decimal('0')
    ) -> Dict:
        """Calculate VAT for a specific quarter"""
        
        # Determine quarter dates
        quarter_starts = {
            1: date(year, 1, 1),
            2: date(year, 4, 1),
            3: date(year, 7, 1),
            4: date(year, 10, 1)
        }
        
        quarter_ends = {
            1: date(year, 3, 31),
            2: date(year, 6, 30),
            3: date(year, 9, 30),
            4: date(year, 12, 31)
        }
        
        start_date = quarter_starts[quarter]
        end_date = quarter_ends[quarter]
        
        result = self.calculate_period_vat(
            sales, costs, associations,
            start_date, end_date,
            previous_negative
        )
        
        result['period']['quarter'] = quarter
        result['period']['year'] = year
        
        return result
    
    def _in_period(self, date_str: str, start: date, end: date) -> bool:
        """Check if date is within period"""
        if not date_str:
            return False
            
        try:
            doc_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            return start <= doc_date <= end
        except ValueError:
            return False
    
    def _get_sale_costs(
        self, 
        sale: Dict, 
        costs: List[Dict], 
        associations: List[Dict]
    ) -> List[Dict]:
        """Get costs associated with a sale"""
        sale_id = sale.get('id')
        linked_cost_ids = sale.get('linked_costs', [])
        
        linked_costs = []
        for cost in costs:
            if cost.get('id') in linked_cost_ids:
                linked_costs.append(cost)
                
        return linked_costs
    
    def generate_anexo_o_data(self, period_result: Dict) -> Dict:
        """
        Generate data for Anexo O (mandatory margin scheme report)
        Required by Portuguese Tax Authority
        """
        return {
            'declarante': {
                'nif': '',  # To be filled with company NIF
                'periodo': period_result['period'],
                'regime': 'margem_viagens'
            },
            'quadro_06': {
                'vendas_totais': period_result['totals']['sales'],
                'custos_diretos': period_result['totals']['costs'],
                'margem_bruta': period_result['totals']['gross_margin'],
                'margem_negativa_anterior': period_result['totals']['previous_negative'],
                'margem_tributavel': period_result['totals']['vat_base'],
                'iva_liquidado': period_result['totals']['vat_amount']
            },
            'notas': {
                'margem_negativa_transitar': abs(period_result['totals']['carry_forward'])
                    if period_result['totals']['carry_forward'] < 0 else 0,
                'metodo_calculo': 'compensacao_periodos',
                'taxa_aplicada': period_result['vat_rate']
            }
        }


def validate_margin_compensation(calculations: List[Dict]) -> Dict:
    """
    Validate that margin compensation is correctly applied across periods
    """
    validation_results = {
        'valid': True,
        'errors': [],
        'warnings': []
    }
    
    carry_forward = Decimal('0')
    
    for i, calc in enumerate(calculations):
        # Check previous negative was applied
        if i > 0 and carry_forward < 0:
            if calc['totals']['previous_negative'] != float(carry_forward):
                validation_results['errors'].append(
                    f"Period {i+1}: Previous negative margin not correctly applied"
                )
                validation_results['valid'] = False
        
        # Update carry forward
        carry_forward = Decimal(str(calc['totals']['carry_forward']))
        
        # Check VAT calculation
        vat_base = Decimal(str(calc['totals']['vat_base']))
        expected_vat = vat_base * Decimal(str(calc['vat_rate'])) / 100
        actual_vat = Decimal(str(calc['totals']['vat_amount']))
        
        if abs(expected_vat - actual_vat) > Decimal('0.01'):
            validation_results['errors'].append(
                f"Period {i+1}: VAT calculation error"
            )
            validation_results['valid'] = False
    
    return validation_results