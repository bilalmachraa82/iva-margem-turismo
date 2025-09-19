"""
Premium Analytics Module for IVA Margem Turismo
Executive-level insights and storytelling with deterministic narratives

Conformidade:
- CIVA Art. 308º (Regime especial agências viagens)
- IFRS 15 (Revenue recognition)
- IFRS 8 (Segment reporting)
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import statistics
import json

logger = logging.getLogger(__name__)


class PremiumAnalytics:
    """
    Executive-level analytics for C-Level reporting
    Zero inventions - all insights data-driven with deterministic narratives
    """

    def __init__(self, vat_rate: float = 23.0):
        self.vat_rate = vat_rate
        self.thresholds = {
            'high_margin': 25.0,      # >25% = high margin
            'low_margin': 5.0,        # <5% = low margin
            'outlier_percentile': 95,  # Top 5% outliers
            'stress_vat_increase': 6,  # Stress test: VAT +6pp
            'cost_variance': 15.0,     # >15% cost variance = alert
            'unlinked_threshold': 10.0 # >10% unlinked = critical
        }

    # -------------------------------------------------------------------------
    # Executive Summary (C-Level Dashboard)
    # -------------------------------------------------------------------------

    def generate_executive_summary(self, calculations: List[Dict],
                                 session_data: Dict) -> Dict[str, Any]:
        """
        Generate one-page executive summary for Board presentation

        Returns:
            Executive dashboard with KPI cards and narrative
        """
        # Core KPIs
        summary = self._calculate_core_kpis(calculations)

        # Performance drivers
        drivers = self._analyze_performance_drivers(calculations, summary)

        # Risk indicators (RAG)
        risks = self._assess_risk_indicators(calculations, summary)

        # Narrative generation
        narrative = self._generate_executive_narrative(summary, drivers, risks)

        # Recommendations
        recommendations = self._generate_recommendations(summary, drivers, risks)

        return {
            "executive_summary": {
                "kpi_cards": self._format_kpi_cards(summary),
                "performance_drivers": drivers,
                "risk_assessment": risks,
                "narrative": narrative,
                "recommendations": recommendations,
                "compliance_status": self._check_compliance(summary),
                "generated_at": datetime.now().isoformat(),
                "period_coverage": self._determine_period(calculations)
            }
        }

    def _calculate_core_kpis(self, calculations: List[Dict]) -> Dict[str, float]:
        """Calculate core executive KPIs"""
        if not calculations:
            return self._empty_kpis()

        total_sales = sum(calc["sale_amount"] for calc in calculations)
        total_costs = sum(calc["total_allocated_costs"] for calc in calculations)
        total_gross_margin = sum(calc["gross_margin"] for calc in calculations)
        total_vat = sum(calc["vat_amount"] for calc in calculations)
        total_net_margin = total_gross_margin - total_vat

        # Advanced KPIs
        documents_count = len(calculations)
        profitable_count = len([c for c in calculations if c["gross_margin"] > 0])
        profitability_rate = (profitable_count / documents_count * 100) if documents_count > 0 else 0

        # Revenue per transaction
        avg_revenue = total_sales / documents_count if documents_count > 0 else 0

        # Margin efficiency
        margin_percentage = (total_gross_margin / total_sales * 100) if total_sales > 0 else 0

        # Cash impact (net margin after VAT)
        cash_impact = total_net_margin

        return {
            "total_sales": total_sales,
            "total_costs": total_costs,
            "gross_margin": total_gross_margin,
            "net_margin": total_net_margin,
            "vat_amount": total_vat,
            "margin_percentage": margin_percentage,
            "documents_count": documents_count,
            "profitability_rate": profitability_rate,
            "avg_revenue": avg_revenue,
            "cash_impact": cash_impact
        }

    def _format_kpi_cards(self, summary: Dict[str, float]) -> List[Dict]:
        """Format KPIs as executive dashboard cards"""
        return [
            {
                "title": "Margem Líquida",
                "value": f"€{summary['net_margin']:,.2f}",
                "percentage": f"{summary['margin_percentage']:.1f}%",
                "trend": self._determine_trend(summary['margin_percentage']),
                "status": self._rag_status(summary['margin_percentage'], 15, 5)  # >15% green, <5% red
            },
            {
                "title": "Total Vendas",
                "value": f"€{summary['total_sales']:,.2f}",
                "subtitle": f"Média: €{summary['avg_revenue']:,.0f}/doc",
                "trend": "stable",
                "status": "ok"
            },
            {
                "title": "IVA sobre Margem",
                "value": f"€{summary['vat_amount']:,.2f}",
                "subtitle": f"Taxa: {self.vat_rate}%",
                "trend": "stable",
                "status": "ok"
            },
            {
                "title": "Taxa Rentabilidade",
                "value": f"{summary['profitability_rate']:.0f}%",
                "subtitle": f"{int(summary['documents_count'])} documentos",
                "trend": self._determine_trend(summary['profitability_rate']),
                "status": self._rag_status(summary['profitability_rate'], 80, 60)
            }
        ]

    # -------------------------------------------------------------------------
    # Performance Drivers Analysis
    # -------------------------------------------------------------------------

    def _analyze_performance_drivers(self, calculations: List[Dict],
                                   summary: Dict) -> Dict[str, Any]:
        """Analyze what's driving performance (volume, price, mix, efficiency)"""

        # Volume driver
        volume_analysis = {
            "documents": len(calculations),
            "avg_transaction": summary['avg_revenue'],
            "impact": "primary" if len(calculations) > 20 else "secondary"
        }

        # Price/Mix driver
        margins = [calc["margin_percentage"] for calc in calculations if calc["sale_amount"] > 0]
        margin_variance = statistics.stdev(margins) if len(margins) > 1 else 0

        price_mix_analysis = {
            "margin_variance": margin_variance,
            "high_margin_docs": len([m for m in margins if m > self.thresholds['high_margin']]),
            "impact": "primary" if margin_variance > 20 else "secondary"
        }

        # Efficiency driver (cost allocation)
        unlinked_sales = [calc for calc in calculations if calc["cost_count"] == 0]
        efficiency_rate = (1 - len(unlinked_sales) / len(calculations)) * 100 if calculations else 0

        efficiency_analysis = {
            "cost_allocation_rate": efficiency_rate,
            "unlinked_sales": len(unlinked_sales),
            "impact": "critical" if efficiency_rate < 90 else "good"
        }

        return {
            "volume": volume_analysis,
            "price_mix": price_mix_analysis,
            "efficiency": efficiency_analysis,
            "primary_driver": self._identify_primary_driver(volume_analysis, price_mix_analysis, efficiency_analysis)
        }

    def _identify_primary_driver(self, volume: Dict, price_mix: Dict, efficiency: Dict) -> str:
        """Determine the primary performance driver"""
        if efficiency["impact"] == "critical":
            return "efficiency"
        elif price_mix["impact"] == "primary":
            return "price_mix"
        elif volume["impact"] == "primary":
            return "volume"
        else:
            return "stable"

    # -------------------------------------------------------------------------
    # Risk Assessment (RAG Indicators)
    # -------------------------------------------------------------------------

    def _assess_risk_indicators(self, calculations: List[Dict],
                              summary: Dict) -> Dict[str, Any]:
        """RAG assessment with specific business rules"""

        risks = []

        # Critical: Carry-forward negative (high negative margins)
        negative_margins = [calc for calc in calculations if calc["gross_margin"] < -1000]
        if negative_margins:
            risks.append({
                "level": "critical",
                "category": "carry_forward",
                "message": f"{len(negative_margins)} documentos com margens muito negativas",
                "action": "Rever política de preços imediatamente",
                "impact": "high"
            })

        # High: Low margin rate
        if summary['margin_percentage'] < self.thresholds['low_margin']:
            risks.append({
                "level": "high",
                "category": "profitability",
                "message": f"Margem {summary['margin_percentage']:.1f}% abaixo do mínimo ({self.thresholds['low_margin']}%)",
                "action": "Analisar estrutura de custos",
                "impact": "medium"
            })

        # Medium: Unlinked costs
        unlinked_rate = self._calculate_unlinked_rate(calculations)
        if unlinked_rate > self.thresholds['unlinked_threshold']:
            risks.append({
                "level": "medium",
                "category": "data_quality",
                "message": f"{unlinked_rate:.1f}% custos sem associação",
                "action": "Melhorar processo de associação",
                "impact": "medium"
            })

        # Calculate overall RAG status
        overall_status = self._calculate_overall_rag(risks)

        return {
            "overall_status": overall_status,
            "risk_count": len(risks),
            "risks": risks,
            "compliance_score": self._calculate_compliance_score(calculations)
        }

    def _calculate_unlinked_rate(self, calculations: List[Dict]) -> float:
        """Calculate percentage of sales without cost allocation"""
        unlinked = len([calc for calc in calculations if calc["cost_count"] == 0])
        return (unlinked / len(calculations) * 100) if calculations else 0

    def _calculate_overall_rag(self, risks: List[Dict]) -> str:
        """Calculate overall RAG status from individual risks"""
        if any(risk["level"] == "critical" for risk in risks):
            return "red"
        elif any(risk["level"] == "high" for risk in risks):
            return "amber"
        elif any(risk["level"] == "medium" for risk in risks):
            return "amber"
        else:
            return "green"

    # -------------------------------------------------------------------------
    # Narrative Generation (Deterministic)
    # -------------------------------------------------------------------------

    def _generate_executive_narrative(self, summary: Dict, drivers: Dict,
                                    risks: Dict) -> Dict[str, str]:
        """Generate deterministic narrative based on data patterns"""

        # Performance summary
        performance_text = self._narrate_performance(summary)

        # Driver explanation
        driver_text = self._narrate_drivers(drivers)

        # Risk context
        risk_text = self._narrate_risks(risks)

        # Market context (if applicable)
        market_text = self._narrate_market_context(summary)

        return {
            "headline": self._generate_headline(summary, risks),
            "performance": performance_text,
            "drivers": driver_text,
            "risks": risk_text,
            "market_context": market_text,
            "conclusion": self._generate_conclusion(summary, drivers, risks)
        }

    def _narrate_performance(self, summary: Dict) -> str:
        """Generate performance narrative"""
        margin_pct = summary['margin_percentage']

        if margin_pct > self.thresholds['high_margin']:
            performance_level = "excelente"
        elif margin_pct > 15:
            performance_level = "sólida"
        elif margin_pct > self.thresholds['low_margin']:
            performance_level = "moderada"
        else:
            performance_level = "baixa"

        return (f"A margem líquida foi {summary['net_margin']:,.0f}€ "
                f"({margin_pct:.1f}%), revelando uma performance {performance_level}. "
                f"O impacto de caixa líquido após IVA é {summary['cash_impact']:,.0f}€.")

    def _narrate_drivers(self, drivers: Dict) -> str:
        """Generate drivers narrative"""
        primary = drivers['primary_driver']

        driver_messages = {
            "volume": f"O volume de {drivers['volume']['documents']} documentos foi o principal impulsionador.",
            "price_mix": f"A variação de margens ({drivers['price_mix']['margin_variance']:.1f}%) indica mix de produtos diversificado.",
            "efficiency": f"A eficiência operacional ({drivers['efficiency']['cost_allocation_rate']:.0f}% custos alocados) impacta a performance.",
            "stable": "Performance estável sem drivers dominantes identificados."
        }

        return driver_messages.get(primary, driver_messages["stable"])

    def _narrate_risks(self, risks: Dict) -> str:
        """Generate risk narrative"""
        status = risks['overall_status']
        count = risks['risk_count']

        if status == "red":
            return f"Identificados {count} riscos críticos que requerem ação imediata."
        elif status == "amber":
            return f"Monitorização necessária - {count} riscos identificados."
        else:
            return "Perfil de risco controlado dentro dos parâmetros normais."

    def _generate_headline(self, summary: Dict, risks: Dict) -> str:
        """Generate executive headline"""
        margin_pct = summary['margin_percentage']
        status = risks['overall_status']

        if status == "red":
            return f"Margem {margin_pct:.1f}% - Ação Corretiva Necessária"
        elif margin_pct > 20:
            return f"Performance Sólida - Margem {margin_pct:.1f}%"
        else:
            return f"Margem {margin_pct:.1f}% - Monitorização Ativa"

    # -------------------------------------------------------------------------
    # Recommendations Engine
    # -------------------------------------------------------------------------

    def _generate_recommendations(self, summary: Dict, drivers: Dict,
                                risks: Dict) -> List[Dict]:
        """Generate actionable recommendations based on data patterns"""
        recommendations = []

        # Immediate actions (next 2 weeks)
        immediate = self._immediate_actions(summary, risks)
        if immediate:
            recommendations.extend(immediate)

        # Strategic opportunities
        strategic = self._strategic_opportunities(summary, drivers)
        if strategic:
            recommendations.extend(strategic)

        # Process improvements
        process = self._process_improvements(drivers, risks)
        if process:
            recommendations.extend(process)

        return recommendations[:5]  # Top 5 recommendations

    def _immediate_actions(self, summary: Dict, risks: Dict) -> List[Dict]:
        """Generate immediate action items"""
        actions = []

        # Critical margin issues
        if summary['margin_percentage'] < self.thresholds['low_margin']:
            actions.append({
                "priority": "critical",
                "timeframe": "2 semanas",
                "category": "pricing",
                "action": "Rever política de preços - margem abaixo de limiar crítico",
                "owner": "Gestão Comercial",
                "kpi": "Margem > 10%"
            })

        # High-value opportunities
        if summary['cash_impact'] < 0:
            actions.append({
                "priority": "high",
                "timeframe": "1 semana",
                "category": "cash_flow",
                "action": "Revisar margens negativas - impacto de caixa adverso",
                "owner": "CFO",
                "kpi": "Cash impact > 0"
            })

        return actions

    def _strategic_opportunities(self, summary: Dict, drivers: Dict) -> List[Dict]:
        """Generate strategic improvement opportunities"""
        opportunities = []

        # High-margin focus
        if drivers['price_mix']['high_margin_docs'] > 0:
            opportunities.append({
                "priority": "medium",
                "timeframe": "1 mês",
                "category": "product_mix",
                "action": f"Expandir produtos alta margem ({drivers['price_mix']['high_margin_docs']} docs identificados)",
                "owner": "Produto",
                "kpi": "% vendas alta margem +20%"
            })

        return opportunities

    def _process_improvements(self, drivers: Dict, risks: Dict) -> List[Dict]:
        """Generate process improvement recommendations"""
        improvements = []

        # Cost allocation efficiency
        if drivers['efficiency']['cost_allocation_rate'] < 95:
            improvements.append({
                "priority": "medium",
                "timeframe": "2 semanas",
                "category": "operations",
                "action": "Melhorar processo de associação vendas-custos",
                "owner": "Operações",
                "kpi": "Taxa alocação > 95%"
            })

        return improvements

    # -------------------------------------------------------------------------
    # Advanced Analytics (Waterfall, Scenarios, Outliers)
    # -------------------------------------------------------------------------

    def generate_waterfall_analysis(self, calculations: List[Dict]) -> Dict[str, Any]:
        """Generate margin bridge/waterfall analysis"""

        # Segment calculations by type for waterfall
        segments = self._segment_by_document_type(calculations)

        waterfall_data = []
        cumulative = 0

        for doc_type, docs in segments.items():
            if not docs:
                continue

            segment_margin = sum(calc["gross_margin"] for calc in docs)
            cumulative += segment_margin

            waterfall_data.append({
                "category": doc_type,
                "value": segment_margin,
                "cumulative": cumulative,
                "count": len(docs),
                "avg_margin": segment_margin / len(docs) if docs else 0
            })

        return {
            "waterfall_data": waterfall_data,
            "total_margin": cumulative,
            "bridge_analysis": self._analyze_margin_bridges(segments)
        }

    def generate_scenario_analysis(self, calculations: List[Dict]) -> Dict[str, Any]:
        """Generate stress test scenarios"""

        base_summary = self._calculate_core_kpis(calculations)

        scenarios = {
            "base": {
                "name": "Cenário Base",
                "vat_rate": self.vat_rate,
                "net_margin": base_summary['net_margin'],
                "description": "Situação atual"
            }
        }

        # Stress test: VAT rate increase
        stress_vat_rate = self.vat_rate + self.thresholds['stress_vat_increase']
        stress_vat = base_summary['gross_margin'] * (stress_vat_rate / 100)
        stress_net = base_summary['gross_margin'] - stress_vat

        scenarios["stress"] = {
            "name": "Stress Test",
            "vat_rate": stress_vat_rate,
            "net_margin": stress_net,
            "impact": stress_net - base_summary['net_margin'],
            "description": f"IVA normal +{self.thresholds['stress_vat_increase']}pp"
        }

        # Optimistic: 15% cost reduction
        optimistic_costs = base_summary['total_costs'] * 0.85
        optimistic_margin = base_summary['total_sales'] - optimistic_costs
        optimistic_vat = optimistic_margin * (self.vat_rate / 100)
        optimistic_net = optimistic_margin - optimistic_vat

        scenarios["optimistic"] = {
            "name": "Cenário Otimista",
            "vat_rate": self.vat_rate,
            "net_margin": optimistic_net,
            "impact": optimistic_net - base_summary['net_margin'],
            "description": "Redução custos 15%"
        }

        return {
            "scenarios": scenarios,
            "sensitivity_analysis": self._calculate_sensitivities(base_summary)
        }

    def identify_outliers(self, calculations: List[Dict]) -> Dict[str, Any]:
        """Identify statistical outliers (percentile 95)"""

        if len(calculations) < 5:
            return {"outliers": [], "analysis": "Dados insuficientes para análise outliers"}

        # Margin outliers
        margins = [calc["margin_percentage"] for calc in calculations if calc["sale_amount"] > 0]
        margin_p95 = statistics.quantiles(margins, n=20)[18] if len(margins) >= 5 else 0  # 95th percentile

        high_margin_outliers = [
            calc for calc in calculations
            if calc["margin_percentage"] > margin_p95 and calc["sale_amount"] > 0
        ]

        # Revenue outliers
        revenues = [calc["sale_amount"] for calc in calculations]
        revenue_p95 = statistics.quantiles(revenues, n=20)[18] if len(revenues) >= 5 else 0

        high_revenue_outliers = [
            calc for calc in calculations
            if calc["sale_amount"] > revenue_p95
        ]

        return {
            "margin_outliers": {
                "threshold": margin_p95,
                "count": len(high_margin_outliers),
                "documents": [
                    {
                        "invoice": outlier["invoice_number"],
                        "margin_pct": outlier["margin_percentage"],
                        "amount": outlier["sale_amount"]
                    }
                    for outlier in high_margin_outliers[:5]  # Top 5
                ]
            },
            "revenue_outliers": {
                "threshold": revenue_p95,
                "count": len(high_revenue_outliers),
                "documents": [
                    {
                        "invoice": outlier["invoice_number"],
                        "amount": outlier["sale_amount"],
                        "margin": outlier["gross_margin"]
                    }
                    for outlier in high_revenue_outliers[:5]  # Top 5
                ]
            },
            "analysis": f"Identificados {len(high_margin_outliers)} outliers margem e {len(high_revenue_outliers)} outliers receita"
        }

    # -------------------------------------------------------------------------
    # Compliance & Governance
    # -------------------------------------------------------------------------

    def _check_compliance(self, summary: Dict) -> Dict[str, Any]:
        """Check compliance with fiscal regulations"""

        compliance_checks = []

        # CIVA Art. 308º compliance
        if summary['vat_amount'] >= 0:
            compliance_checks.append({
                "regulation": "CIVA Art. 308º",
                "status": "compliant",
                "description": "IVA sobre margem calculado corretamente"
            })
        else:
            compliance_checks.append({
                "regulation": "CIVA Art. 308º",
                "status": "review",
                "description": "IVA negativo requer revisão"
            })

        # Data quality check
        if summary['documents_count'] > 0:
            compliance_checks.append({
                "regulation": "Controlo Interno",
                "status": "compliant",
                "description": f"{summary['documents_count']} documentos processados"
            })

        overall_status = "compliant" if all(c["status"] == "compliant" for c in compliance_checks) else "review"

        return {
            "overall_status": overall_status,
            "checks": compliance_checks,
            "regulations": ["CIVA Art. 308º", "DL 221/85", "IFRS 15"],
            "last_updated": datetime.now().isoformat()
        }

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def _empty_kpis(self) -> Dict[str, float]:
        """Return empty KPI structure"""
        return {
            "total_sales": 0.0,
            "total_costs": 0.0,
            "gross_margin": 0.0,
            "net_margin": 0.0,
            "vat_amount": 0.0,
            "margin_percentage": 0.0,
            "documents_count": 0,
            "profitability_rate": 0.0,
            "avg_revenue": 0.0,
            "cash_impact": 0.0
        }

    def _determine_trend(self, value: float) -> str:
        """Determine trend direction (placeholder - needs historical data)"""
        # In real implementation, compare with previous period
        return "stable"

    def _rag_status(self, value: float, green_threshold: float, red_threshold: float) -> str:
        """Determine RAG status based on thresholds"""
        if value >= green_threshold:
            return "green"
        elif value >= red_threshold:
            return "amber"
        else:
            return "red"

    def _determine_period(self, calculations: List[Dict]) -> Dict[str, str]:
        """Determine period coverage from calculations"""
        if not calculations:
            return {"start": "", "end": "", "description": "Sem dados"}

        dates = [calc.get("date", "") for calc in calculations if calc.get("date")]
        if not dates:
            return {"start": "", "end": "", "description": "Datas não disponíveis"}

        dates.sort()
        return {
            "start": dates[0],
            "end": dates[-1],
            "description": f"Período: {dates[0]} a {dates[-1]}"
        }

    def _segment_by_document_type(self, calculations: List[Dict]) -> Dict[str, List[Dict]]:
        """Segment calculations by document type"""
        segments = {}
        for calc in calculations:
            doc_type = calc.get("invoice_type", "Outro")
            if doc_type not in segments:
                segments[doc_type] = []
            segments[doc_type].append(calc)
        return segments

    def _analyze_margin_bridges(self, segments: Dict[str, List[Dict]]) -> List[Dict]:
        """Analyze margin bridges between segments"""
        bridges = []
        for doc_type, docs in segments.items():
            if docs:
                total_margin = sum(calc["gross_margin"] for calc in docs)
                avg_margin = total_margin / len(docs)
                bridges.append({
                    "segment": doc_type,
                    "contribution": total_margin,
                    "avg_margin": avg_margin,
                    "document_count": len(docs)
                })
        return bridges

    def _calculate_sensitivities(self, base_summary: Dict) -> Dict[str, float]:
        """Calculate sensitivity to key variables"""
        return {
            "vat_rate_1pp": base_summary['gross_margin'] * 0.01,  # 1pp VAT impact
            "cost_1pct": base_summary['total_costs'] * 0.01,      # 1% cost impact
            "volume_1doc": base_summary['avg_revenue']            # 1 document impact
        }

    def _calculate_compliance_score(self, calculations: List[Dict]) -> float:
        """Calculate overall compliance score (0-100)"""
        if not calculations:
            return 0.0

        # Factors: data completeness, margin reasonableness, allocation quality
        complete_data = len([c for c in calculations if c.get("date") and c.get("client")])
        reasonable_margins = len([c for c in calculations if -50 <= c["margin_percentage"] <= 100])
        allocated_costs = len([c for c in calculations if c["cost_count"] > 0])

        total = len(calculations)
        completeness_score = (complete_data / total) * 40
        reasonableness_score = (reasonable_margins / total) * 30
        allocation_score = (allocated_costs / total) * 30

        return min(100.0, completeness_score + reasonableness_score + allocation_score)

    def _narrate_market_context(self, summary: Dict) -> str:
        """Generate market context narrative (placeholder)"""
        # In real implementation, integrate with market data
        margin_pct = summary['margin_percentage']

        if margin_pct > 15:
            return "Performance acima da média do setor turismo (10-15%)."
        elif margin_pct > 8:
            return "Performance alinhada com benchmarks do setor."
        else:
            return "Performance abaixo dos standards do setor - revisão necessária."

    def _generate_conclusion(self, summary: Dict, drivers: Dict, risks: Dict) -> str:
        """Generate executive conclusion"""
        status = risks['overall_status']
        margin_pct = summary['margin_percentage']

        if status == "green" and margin_pct > 15:
            return "Performance sólida com perfil de risco controlado. Manter estratégia atual."
        elif status == "amber":
            return "Performance adequada com pontos de atenção. Monitorização ativa recomendada."
        else:
            return "Ação corretiva necessária. Priorizar recomendações críticas."


# -------------------------------------------------------------------------
# Advanced KPI Calculations
# -------------------------------------------------------------------------

class AdvancedKPICalculator:
    """
    Calculate advanced financial KPIs for executive reporting
    """

    @staticmethod
    def calculate_roic_simplified(net_margin: float, invested_capital: float) -> float:
        """Simplified ROIC calculation for travel agencies"""
        if invested_capital <= 0:
            return 0.0
        return (net_margin / invested_capital) * 100

    @staticmethod
    def calculate_eva_simplified(net_margin: float, cost_of_capital: float,
                                invested_capital: float) -> float:
        """Simplified EVA calculation"""
        return net_margin - (cost_of_capital * invested_capital / 100)

    @staticmethod
    def calculate_margin_stability(calculations: List[Dict]) -> Dict[str, float]:
        """Calculate margin stability metrics"""
        if len(calculations) < 2:
            return {"volatility": 0.0, "consistency": 100.0}

        margins = [calc["margin_percentage"] for calc in calculations if calc["sale_amount"] > 0]

        if len(margins) < 2:
            return {"volatility": 0.0, "consistency": 100.0}

        avg_margin = statistics.mean(margins)
        volatility = statistics.stdev(margins)

        # Consistency: inverse of coefficient of variation
        consistency = max(0, 100 - (volatility / avg_margin * 100)) if avg_margin > 0 else 0

        return {
            "volatility": volatility,
            "consistency": consistency,
            "coefficient_variation": volatility / avg_margin if avg_margin > 0 else 0
        }