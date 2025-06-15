"""
Validadores de segurança e qualidade dos dados
"""
from typing import List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataValidator:
    """Validador para dados de IVA margem"""
    
    @staticmethod
    def validate_file_upload(file_size: int, filename: str) -> List[str]:
        """Valida upload de ficheiro"""
        errors = []
        
        # Tamanho máximo: 50MB
        if file_size > 50 * 1024 * 1024:
            errors.append("Ficheiro muito grande (máximo 50MB)")
        
        # Extensão
        if not filename.lower().endswith(('.xml', '.xlsm', '.xlsx')):
            errors.append("Formato inválido. Use XML (SAF-T) ou Excel")
        
        # Nome suspeito
        suspicious_chars = ['<', '>', '|', '&', ';', '$', '`']
        if any(char in filename for char in suspicious_chars):
            errors.append("Nome de ficheiro contém caracteres inválidos")
            
        return errors
    
    @staticmethod
    def validate_margin_regime_data(sales: List[Dict], costs: List[Dict]) -> Dict[str, Any]:
        """Valida dados para regime de margem"""
        warnings = []
        errors = []
        stats = {"sales_count": len(sales), "costs_count": len(costs)}
        
        # Validar vendas
        for sale in sales:
            # Vendas não devem ter IVA separado no regime de margem
            if sale.get('vat_amount', 0) != 0:
                errors.append(f"Venda {sale.get('number', 'N/A')}: IVA separado não permitido no regime de margem")
            
            # Verificar valores suspeitos
            amount = sale.get('amount', 0)
            if amount > 50000:
                warnings.append(f"Venda {sale.get('number', 'N/A')}: Valor muito alto (€{amount:,.2f})")
            elif amount == 0:
                warnings.append(f"Venda {sale.get('number', 'N/A')}: Valor zero")
        
        # Validar custos
        for cost in costs:
            amount = cost.get('amount', 0)
            if amount > 50000:
                warnings.append(f"Custo {cost.get('supplier', 'N/A')}: Valor muito alto (€{amount:,.2f})")
        
        # Calcular margens estimadas
        total_sales = sum(s.get('amount', 0) for s in sales if s.get('amount', 0) > 0)
        total_costs = sum(c.get('amount', 0) for c in costs)
        
        if total_sales > 0:
            margin_pct = ((total_sales - total_costs) / total_sales) * 100
            stats['margin_percentage'] = margin_pct
            
            if margin_pct > 40:
                warnings.append(f"Margem muito alta ({margin_pct:.1f}%) - Típico turismo: 5-25%")
            elif margin_pct < 0:
                warnings.append(f"Margem negativa ({margin_pct:.1f}%) - Verificar associações")
        
        return {
            "errors": errors,
            "warnings": warnings, 
            "stats": stats,
            "is_valid": len(errors) == 0
        }
    
    @staticmethod
    def validate_session_data(session_data: Dict) -> bool:
        """Valida integridade dos dados da sessão"""
        required_fields = ['sales', 'costs', 'metadata']
        
        for field in required_fields:
            if field not in session_data:
                logger.error(f"Campo obrigatório ausente: {field}")
                return False
        
        # Verificar estrutura básica
        if not isinstance(session_data['sales'], list):
            logger.error("Campo 'sales' deve ser uma lista")
            return False
            
        if not isinstance(session_data['costs'], list):
            logger.error("Campo 'costs' deve ser uma lista")
            return False
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de ficheiro"""
        import re
        # Remove caracteres perigosos
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limita tamanho
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:250] + ('.' + ext if ext else '')
        return filename
    
    @staticmethod
    def validate_calculation_request(request_data: Dict) -> List[str]:
        """Valida pedido de cálculo"""
        errors = []
        
        # Verificar session_id
        if not request_data.get('session_id'):
            errors.append("Session ID obrigatório")
        
        # Verificar VAT rate
        vat_rate = request_data.get('vat_rate')
        if vat_rate is None:
            errors.append("Taxa IVA obrigatória")
        elif not isinstance(vat_rate, (int, float)):
            errors.append("Taxa IVA deve ser numérica")
        elif vat_rate < 0 or vat_rate > 100:
            errors.append("Taxa IVA deve estar entre 0% e 100%")
        
        return errors
    
    @staticmethod
    def validate_associations_integrity(sales: List[Dict], costs: List[Dict]) -> List[Dict]:
        """
        Valida integridade bidirecional das associações
        
        Args:
            sales: Lista de vendas
            costs: Lista de custos
            
        Returns:
            Lista de erros de integridade encontrados
        """
        errors = []
        
        # Criar mapas para lookup rápido
        sales_map = {sale["id"]: sale for sale in sales}
        costs_map = {cost["id"]: cost for cost in costs}
        
        # Verificar integridade das vendas -> custos
        for sale in sales:
            for cost_id in sale.get("linked_costs", []):
                if cost_id not in costs_map:
                    errors.append({
                        "type": "error",
                        "entity": "sale",
                        "id": sale["id"],
                        "number": sale.get("number", "N/A"),
                        "message": f"Venda referencia custo inexistente: {cost_id}"
                    })
                else:
                    cost = costs_map[cost_id]
                    if sale["id"] not in cost.get("linked_sales", []):
                        errors.append({
                            "type": "warning",
                            "entity": "sale",
                            "id": sale["id"],
                            "number": sale.get("number", "N/A"),
                            "message": f"Associação unidirecional: venda → custo {cost.get('supplier', cost_id)}"
                        })
        
        # Verificar integridade dos custos -> vendas
        for cost in costs:
            for sale_id in cost.get("linked_sales", []):
                if sale_id not in sales_map:
                    errors.append({
                        "type": "error",
                        "entity": "cost",
                        "id": cost["id"],
                        "supplier": cost.get("supplier", "N/A"),
                        "message": f"Custo referencia venda inexistente: {sale_id}"
                    })
                else:
                    sale = sales_map[sale_id]
                    if cost["id"] not in sale.get("linked_costs", []):
                        errors.append({
                            "type": "warning",
                            "entity": "cost",
                            "id": cost["id"],
                            "supplier": cost.get("supplier", "N/A"),
                            "message": f"Associação unidirecional: custo → venda {sale.get('number', sale_id)}"
                        })
        
        # Verificar custos órfãos (sem associações)
        orphan_costs = [cost for cost in costs if not cost.get("linked_sales", [])]
        if orphan_costs:
            errors.append({
                "type": "info",
                "entity": "costs",
                "count": len(orphan_costs),
                "message": f"{len(orphan_costs)} custos sem vendas associadas"
            })
        
        # Verificar vendas sem custos (pode ser legítimo mas vale a pena avisar)
        sales_without_costs = [sale for sale in sales if not sale.get("linked_costs", [])]
        if sales_without_costs:
            errors.append({
                "type": "info",
                "entity": "sales",
                "count": len(sales_without_costs),
                "message": f"{len(sales_without_costs)} vendas sem custos associados (margem 100%)"
            })
        
        return errors