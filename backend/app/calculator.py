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
    
    def __init__(self, vat_rate: float = 23.0):
        """
        Initialize calculator with VAT rate
        
        Args:
            vat_rate: VAT percentage rate (default 23% for Portugal)
        """
        self.vat_rate = vat_rate
        
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
        
        # Create cost map for quick lookup
        costs_map = {cost["id"]: cost for cost in costs}
        
        for sale in sales:
            try:
                result = self._calculate_sale_margin(sale, costs_map)
                results.append(result)
            except Exception as e:
                logger.error(f"Error calculating margin for sale {sale.get('number', 'unknown')}: {str(e)}")
                continue
                
        return results
    
    def _calculate_sale_margin(self, sale: Dict, costs_map: Dict[str, Dict]) -> Dict:
        """Calculate margin and VAT for a single sale"""
        
        # Initialize calculation
        sale_amount = sale.get("amount", 0)
        linked_cost_details = []
        total_allocated_costs = 0
        
        # Process linked costs
        for cost_id in sale.get("linked_costs", []):
            if cost_id not in costs_map:
                logger.warning(f"Cost {cost_id} not found for sale {sale.get('number')}")
                continue
                
            cost = costs_map[cost_id]
            
            # Calculate cost allocation
            # If cost is linked to multiple sales, distribute proportionally
            num_linked_sales = len(cost.get("linked_sales", []))
            if num_linked_sales == 0:
                num_linked_sales = 1  # Avoid division by zero
                
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
        
        # Calculate margin
        gross_margin = sale_amount - total_allocated_costs
        
        # Calculate VAT on margin
        # Formula para IVA sobre margem (Portugal - CIVA Art. 308º):
        # IVA = Margem × Taxa_IVA / 100
        # A margem é tributável pelo IVA normal, não incluído
        if gross_margin > 0:
            vat_on_margin = gross_margin * self.vat_rate / 100
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