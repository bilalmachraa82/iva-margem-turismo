#!/usr/bin/env python3
"""Unit tests for the Premium Analytics engine"""

import unittest
import sys
from pathlib import Path

# Garantir que o pacote backend é importável
ROOT = Path(__file__).resolve().parent
BACKEND_PATH = ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.append(str(BACKEND_PATH))

from app.analytics import PremiumAnalytics, AdvancedKPICalculator
from app.calculator import VATCalculator


def build_fixture(num_entries: int = 5):
    """Create synthetic sales/costs dataset with consistent links."""
    sales = []
    costs = []

    for idx in range(1, num_entries + 1):
        sale_id = f"s{idx}"
        cost_id = f"c{idx}"
        sale_amount = 800 + idx * 150
        cost_amount = 300 + idx * 40

        sale = {
            "id": sale_id,
            "number": f"FT 2025/{idx:03d}",
            "date": f"2025-02-{10 + idx:02d}",
            "client": f"Cliente {idx:03d}",
            "amount": float(sale_amount),
            "vat_amount": 0.0,
            "gross_total": float(sale_amount),
            "linked_costs": [cost_id]
        }

        cost = {
            "id": cost_id,
            "supplier": f"Fornecedor {idx:03d}",
            "description": "Serviço turístico",
            "date": f"2025-02-{9 + idx:02d}",
            "amount": float(cost_amount),
            "vat_amount": 0.0,
            "gross_total": float(cost_amount),
            "document_number": f"FTC-{idx:03d}",
            "linked_sales": [sale_id]
        }

        sales.append(sale)
        costs.append(cost)

    return sales, costs


class PremiumAnalyticsTests(unittest.TestCase):
    """Validate deterministic analytics helpers"""

    def setUp(self):
        self.sales, self.costs = build_fixture()
        self.calculator = VATCalculator(vat_rate=23)
        self.calculations = self.calculator.calculate_all(self.sales, self.costs)
        self.analytics = PremiumAnalytics(vat_rate=23)

    def test_calculations_produce_results(self):
        self.assertTrue(self.calculations, "VAT calculator should produce results")
        summary = self.calculator.calculate_summary(self.calculations)
        self.assertGreater(summary["total_sales"], 0)
        self.assertIn("average_margin_percentage", summary)

    def test_executive_summary_structure(self):
        payload = {"sales": self.sales, "costs": self.costs}
        result = self.analytics.generate_executive_summary(self.calculations, payload)
        self.assertIn("executive_summary", result)
        exec_summary = result["executive_summary"]
        self.assertIn("kpi_cards", exec_summary)
        self.assertGreater(len(exec_summary["kpi_cards"]), 0)
        self.assertIn("narrative", exec_summary)

    def test_waterfall_analysis_not_empty(self):
        waterfall = self.analytics.generate_waterfall_analysis(self.calculations)
        self.assertIn("waterfall_data", waterfall)
        self.assertIsInstance(waterfall["waterfall_data"], list)
        self.assertGreaterEqual(len(waterfall["waterfall_data"]), 1)

    def test_scenario_analysis_contains_base(self):
        scenarios = self.analytics.generate_scenario_analysis(self.calculations)
        self.assertIn("scenarios", scenarios)
        self.assertIn("base", scenarios["scenarios"])
        self.assertIn("stress", scenarios["scenarios"])

    def test_outlier_analysis_schema(self):
        outliers = self.analytics.identify_outliers(self.calculations)
        self.assertIn("margin_outliers", outliers)
        self.assertIn("revenue_outliers", outliers)
        self.assertIn("analysis", outliers)

    def test_advanced_kpi_helpers(self):
        summary = self.calculator.calculate_summary(self.calculations)
        roic = AdvancedKPICalculator.calculate_roic_simplified(summary["total_net_margin"], summary["total_costs"])
        eva = AdvancedKPICalculator.calculate_eva_simplified(summary["total_net_margin"], 8.0, summary["total_costs"])
        stability = AdvancedKPICalculator.calculate_margin_stability(self.calculations)

        self.assertGreaterEqual(roic, 0)
        self.assertIsInstance(eva, float)
        self.assertIn("volatility", stability)
        self.assertIn("consistency", stability)


if __name__ == "__main__":
    unittest.main()
