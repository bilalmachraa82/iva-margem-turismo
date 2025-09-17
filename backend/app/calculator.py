"""
VAT Calculator for margin scheme
Calculates VAT on margin (not on total) for travel agencies
"""
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class VATCalculator:
    """
    Calculator for VAT margin scheme used by travel agencies (Portugal)
    
    Conformidade com:
    - CIVA Artº 308º (Regime especial das agências de viagens)
    - DL 221/85 (Regime do IVA sobre margem)
    
    IVA é calculado sobre a margem de lucro, não sobre o valor total da venda
    Margem = Preço de Venda - Custos Diretos
    IVA = Margem × Taxa de IVA / 100
    """
    
    def __init__(self, vat_rate: float = 23.0, fiscal_year: Optional[int] = None):
        """
        Initialize calculator with VAT rate

        Args:
            vat_rate: VAT percentage rate (default 23% for Portugal)
            fiscal_year: Fiscal year for calculations (optional)
        """
        self.vat_rate = vat_rate
        self.fiscal_year = fiscal_year
        self.validation_errors = []
        
    def calculate_all(self, sales: List[Dict], costs: List[Dict]) -> List[Dict]:
        """
        Calculate VAT on margin for all sales
        
        Args:
            sales: List of sales documents
            costs: List of cost documents
            
        Returns:
            List of calculation results with detailed breakdown
        """
        results = []
        self.validation_errors = []  # Track validation errors
        
        # Create cost map for quick lookup
        costs_map = {cost["id"]: cost for cost in costs}
        
        # First, validate all associations integrity
        self._validate_associations(sales, costs, costs_map)
        
        for sale in sales:
            try:
                result = self._calculate_sale_margin(sale, costs_map)
                if result:  # Only add if calculation was successful
                    results.append(result)
            except Exception as e:
                logger.error(f"Error calculating margin for sale {sale.get('number', 'unknown')}: {str(e)}")
                self.validation_errors.append({
                    "type": "error",
                    "sale": sale.get('number', 'unknown'),
                    "message": f"Erro no cálculo: {str(e)}"
                })
                continue
                
        return results
    
    def _validate_associations(self, sales: List[Dict], costs: List[Dict], costs_map: Dict[str, Dict]):
        """Validate bidirectional integrity of associations"""
        for sale in sales:
            for cost_id in sale.get("linked_costs", []):
                if cost_id not in costs_map:
                    logger.error(f"CRITICAL: Cost {cost_id} not found for sale {sale.get('number')}")
                    self.validation_errors.append({
                        "type": "critical",
                        "sale": sale.get('number'),
                        "message": f"Custo {cost_id} não encontrado no sistema"
                    })
                else:
                    cost = costs_map[cost_id]
                    # Check bidirectional link
                    if sale["id"] not in cost.get("linked_sales", []):
                        logger.warning(f"INTEGRITY WARNING: Sale {sale['id']} linked to cost {cost_id} but cost doesn't link back")
                        self.validation_errors.append({
                            "type": "warning",
                            "sale": sale.get('number'),
                            "message": f"Associação unidirecional com custo {cost['supplier']}"
                        })
    
    def _calculate_sale_margin(self, sale: Dict, costs_map: Dict[str, Dict]) -> Optional[Dict]:
        """Calculate margin and VAT for a single sale"""
        
        # Initialize calculation
        sale_amount = sale.get("amount", 0)
        linked_cost_details = []
        total_allocated_costs = 0
        
        # Process linked costs
        has_critical_errors = False
        for cost_id in sale.get("linked_costs", []):
            if cost_id not in costs_map:
                logger.error(f"CRITICAL: Cost {cost_id} not found for sale {sale.get('number')}")
                self.validation_errors.append({
                    "type": "critical",
                    "sale": sale.get('number'),
                    "message": f"Custo {cost_id} referenciado mas não existe"
                })
                has_critical_errors = True
                continue
                
            cost = costs_map[cost_id]
            
            # Validate bidirectional link
            if sale["id"] not in cost.get("linked_sales", []):
                logger.warning(f"Cost {cost_id} not linked back to sale {sale['id']}")
                # Auto-fix the bidirectional link
                if "linked_sales" not in cost:
                    cost["linked_sales"] = []
                cost["linked_sales"].append(sale["id"])
            
            # Calculate cost allocation
            # If cost is linked to multiple sales, distribute proportionally
            num_linked_sales = len(cost.get("linked_sales", []))
            if num_linked_sales == 0:
                logger.error(f"Cost {cost_id} has no linked sales but is referenced")
                num_linked_sales = 1  # Avoid division by zero
                
            # Validate allocation makes sense
            if num_linked_sales > 10:
                logger.warning(f"Cost {cost_id} linked to {num_linked_sales} sales - unusual")
                self.validation_errors.append({
                    "type": "warning",
                    "sale": sale.get('number'),
                    "message": f"Custo partilhado com {num_linked_sales} vendas"
                })
                
            # Simple proportional allocation
            allocated_amount = cost["amount"] / num_linked_sales
            allocated_vat = cost.get("vat_amount", 0) / num_linked_sales
            
            total_allocated_costs += allocated_amount
            
            linked_cost_details.append({
                "cost_id": cost_id,
                "supplier": cost["supplier"],
                "description": cost["description"],
                "total_amount": cost["amount"],
                "allocated_amount": round(allocated_amount, 2),
                "allocated_vat": round(allocated_vat, 2),
                "shared_with": num_linked_sales,
                "document_number": cost.get("document_number", ""),
                "date": cost.get("date", "")
            })
        
        # Don't proceed with calculation if critical errors found
        if has_critical_errors:
            logger.error(f"Skipping calculation for sale {sale.get('number')} due to critical errors")
            return None
            
        # Calculate margin
        gross_margin = sale_amount - total_allocated_costs
        
        # Calculate VAT on margin (CIVA Art. 308º - regime especial agências viagens)
        # IVA sobre margem = Margem × Taxa_IVA / 100
        if gross_margin > 0:
            vat_on_margin = gross_margin * (self.vat_rate / 100)
        else:
            # No VAT on negative margins
            vat_on_margin = 0
            
        net_margin = gross_margin - vat_on_margin
        
        # Calculate margin percentage
        margin_percentage = 0
        if sale_amount > 0:
            margin_percentage = (gross_margin / sale_amount) * 100
            
        # Determine invoice type
        invoice_type = self._get_invoice_type(sale.get("number", ""))
        
        return {
            "invoice_number": sale.get("number", ""),
            "invoice_type": invoice_type,
            "date": sale.get("date", ""),
            "client": sale.get("client", ""),
            "sale_amount": sale_amount,
            "sale_vat": sale.get("vat_amount", 0),
            "total_allocated_costs": round(total_allocated_costs, 2),
            "gross_margin": round(gross_margin, 2),
            "vat_rate": self.vat_rate,
            "vat_amount": round(vat_on_margin, 2),
            "net_margin": round(net_margin, 2),
            "margin_percentage": round(margin_percentage, 2),
            "linked_costs": linked_cost_details,
            "cost_count": len(linked_cost_details)
        }
    
    def _get_invoice_type(self, invoice_number: str) -> str:
        """Determine document type from invoice number"""
        if invoice_number.startswith("FT"):
            return "Fatura"
        elif invoice_number.startswith("FR"):
            return "Fatura-Recibo"
        elif invoice_number.startswith("NC"):
            return "Nota de Crédito"
        elif invoice_number.startswith("ND"):
            return "Nota de Débito"
        elif invoice_number.startswith("FS"):
            return "Fatura Simplificada"
        else:
            return "Outro"
    
    def calculate_summary(self, calculations: List[Dict]) -> Dict:
        """
        Calculate summary totals from all calculations
        
        Args:
            calculations: List of calculation results
            
        Returns:
            Summary dictionary with totals and statistics
        """
        summary = {
            "total_sales": 0,
            "total_costs": 0,
            "total_gross_margin": 0,
            "total_vat": 0,
            "total_net_margin": 0,
            "average_margin_percentage": 0,
            "documents_processed": len(calculations),
            "documents_with_margin": 0,
            "documents_with_loss": 0,
            "by_type": {}
        }
        
        for calc in calculations:
            # Update totals
            summary["total_sales"] += calc["sale_amount"]
            summary["total_costs"] += calc["total_allocated_costs"]
            summary["total_gross_margin"] += calc["gross_margin"]
            summary["total_vat"] += calc["vat_amount"]
            summary["total_net_margin"] += calc["net_margin"]
            
            # Count profitable vs loss
            if calc["gross_margin"] > 0:
                summary["documents_with_margin"] += 1
            elif calc["gross_margin"] < 0:
                summary["documents_with_loss"] += 1
                
            # Group by document type
            doc_type = calc["invoice_type"]
            if doc_type not in summary["by_type"]:
                summary["by_type"][doc_type] = {
                    "count": 0,
                    "total_sales": 0,
                    "total_costs": 0,
                    "total_margin": 0,
                    "total_vat": 0
                }
                
            summary["by_type"][doc_type]["count"] += 1
            summary["by_type"][doc_type]["total_sales"] += calc["sale_amount"]
            summary["by_type"][doc_type]["total_costs"] += calc["total_allocated_costs"]
            summary["by_type"][doc_type]["total_margin"] += calc["gross_margin"]
            summary["by_type"][doc_type]["total_vat"] += calc["vat_amount"]
        
        # Calculate average margin percentage (weighted)
        if summary["total_sales"] > 0:
            summary["average_margin_percentage"] = round(
                (summary["total_gross_margin"] / summary["total_sales"]) * 100, 2
            )
            
        # Round all totals
        for key in ["total_sales", "total_costs", "total_gross_margin", "total_vat", "total_net_margin"]:
            summary[key] = round(summary[key], 2)
            
        return summary
    
    def validate_calculations(self, calculations: List[Dict]) -> List[Dict]:
        """
        Validate calculations and identify potential issues
        
        Args:
            calculations: List of calculation results
            
        Returns:
            List of validation warnings/errors
        """
        issues = []
        
        for calc in calculations:
            # Check for sales without costs
            if calc["cost_count"] == 0 and calc["sale_amount"] > 0:
                issues.append({
                    "type": "warning",
                    "invoice": calc["invoice_number"],
                    "message": "Venda sem custos associados - margem 100%"
                })
                
            # Check for negative margins
            if calc["gross_margin"] < 0:
                issues.append({
                    "type": "warning",
                    "invoice": calc["invoice_number"],
                    "message": f"Margem negativa: €{calc['gross_margin']}"
                })
                
            # Check for unusually high margins
            if calc["margin_percentage"] > 80:
                issues.append({
                    "type": "info",
                    "invoice": calc["invoice_number"],
                    "message": f"Margem elevada: {calc['margin_percentage']}%"
                })
                
        return issues
    
    def get_validation_errors(self) -> List[Dict]:
        """
        Get validation errors from last calculation
        
        Returns:
            List of validation errors and warnings
        """
        return getattr(self, 'validation_errors', [])

    def calculate_by_period(self, sales: List[Dict], costs: List[Dict],
                          period_start: str, period_end: str) -> Dict:
        """
        Calculate VAT on margin for a specific fiscal period

        Args:
            sales: List of sales documents
            costs: List of cost documents
            period_start: Start date (YYYY-MM-DD)
            period_end: End date (YYYY-MM-DD)

        Returns:
            Period calculation with cumulative margin compensation
        """
        from datetime import datetime

        start_date = datetime.strptime(period_start, "%Y-%m-%d")
        end_date = datetime.strptime(period_end, "%Y-%m-%d")

        # Filter documents by period
        period_sales = []
        period_costs = []

        for sale in sales:
            sale_date = datetime.strptime(sale["date"], "%Y-%m-%d")
            if start_date <= sale_date <= end_date:
                period_sales.append(sale)

        for cost in costs:
            cost_date = datetime.strptime(cost["date"], "%Y-%m-%d")
            if start_date <= cost_date <= end_date:
                period_costs.append(cost)

        # Calculate for period
        period_calculations = self.calculate_all(period_sales, period_costs)
        period_summary = self.calculate_summary(period_calculations)

        # Add period-specific data
        period_summary["period_start"] = period_start
        period_summary["period_end"] = period_end
        period_summary["calculation_mode"] = "period_based"
        period_summary["compliance"] = "CIVA Art. 308º - Regime Especial Agências Viagens"

        return {
            "summary": period_summary,
            "calculations": period_calculations,
            "validation_errors": self.validation_errors
        }
