import os
import sys
import unittest
from unittest.mock import patch

sys.path.append('backend')

from app.pdf_export_professional import ProfessionalReportGenerator
from app.pdf_renderer import PDFRenderer, PremiumPDFUnavailable, ReportMeta
from app.pdf_pipeline import render_pdf_from_html


RUN_PREMIUM_TESTS = os.getenv("RUN_PREMIUM_PDF_TESTS", "").lower() in {"1", "true", "yes"}


@unittest.skipUnless(RUN_PREMIUM_TESTS, "Set RUN_PREMIUM_PDF_TESTS=1 to enable premium pipeline tests.")
class ProfessionalReportGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.generator = ProfessionalReportGenerator()
        self.session_data = {
            "sales": [
                {"id": "s1", "number": "FT 1", "amount": 1000.0, "linked_costs": ["c1"]},
            ],
            "costs": [
                {"id": "c1", "amount": 400.0, "linked_sales": ["s1"]},
            ],
            "metadata": {
                "company_name": "Consultoria Premium Lda.",
                "company_info": {
                    "name": "Consultoria Premium Lda.",
                    "nif": "123456789",
                    "address": "Av. da Liberdade, 1",
                    "city": "Lisboa",
                    "postal_code": "1000-001",
                    "phone": "+351 21 000 0000",
                    "email": "fiscal@consultoria.pt",
                },
            },
        }
        self.calculations = [
            {
                "invoice_number": "FT 1",
                "date": "2025-01-01",
                "client": "Cliente XPTO",
                "sale_amount": 1000.0,
                "total_allocated_costs": 400.0,
                "gross_margin": 600.0,
                "vat_amount": 138.0,
            }
        ]
        self.final_results = {
            "totalSales": 1000.0,
            "totalCosts": 400.0,
            "grossMargin": 600.0,
            "netMargin": 462.0,
            "totalVAT": 138.0,
            "calculationType": "standard",
        }

    def test_html_report_contains_metadata_and_sections(self):
        html = self.generator.generate_html_report(
            self.session_data,
            self.calculations,
            vat_rate=23.0,
            final_results=self.final_results,
            company_info=self.session_data["metadata"]["company_info"],
        )
        self.assertIn("Relatório premium", html)
        self.assertIn("meta name=\"author\"", html)
        self.assertIn("Resumo Executivo", html)
        self.assertIn("Trace ID", html)
        self.assertIn("Consultoria Premium Lda.", html)


@unittest.skipUnless(RUN_PREMIUM_TESTS, "Set RUN_PREMIUM_PDF_TESTS=1 to enable premium pipeline tests.")
class PDFRendererTests(unittest.TestCase):
    def test_renderer_unavailable_raises(self):
        renderer = PDFRenderer()
        renderer._engine = None  # Force unavailable state
        with self.assertRaises(PremiumPDFUnavailable):
            renderer.render_html_to_pdf("<html></html>")

    def test_renderer_with_fake_engine(self):
        class FakeHTML:
            def __init__(self, string, base_url):
                self.string = string
                self.base_url = base_url

            def write_pdf(self, stylesheets=None, presentational_hints=None, font_config=None):
                return b"%PDF-FAKE%"

        class FakeCSS:
            def __init__(self, string):  # noqa: D401 - signature matches CSS
                self.string = string

        renderer = PDFRenderer()
        renderer._engine = {"HTML": FakeHTML, "CSS": FakeCSS, "FontConfiguration": None}
        renderer._inject_metadata = lambda pdf_bytes, meta: pdf_bytes + b"-META"  # type: ignore

        output = renderer.render_html_to_pdf("<html></html>", ReportMeta(title="Demo"))
        self.assertEqual(output, b"%PDF-FAKE%-META")


@unittest.skipUnless(RUN_PREMIUM_TESTS, "Set RUN_PREMIUM_PDF_TESTS=1 to enable premium pipeline tests.")
class RenderPipelineSelectionTests(unittest.TestCase):
    def setUp(self):
        self.session_data = {"sales": [], "costs": [], "metadata": {}}
        self.calculations = []
        self.final_results = {}
        self.company_payload = {"name": "Empresa Demo"}
        self.safe_company = "Empresa Demo"
        self.html = "<html></html>"

    def test_premium_renderer_used_when_available(self):
        with patch("app.pdf_pipeline.PDFRenderer.render_html_to_pdf", return_value=b"%PDF-PREMIUM%") as premium_mock, \
             patch("app.pdf_pipeline.generate_basic_pdf") as fallback_mock:
            pdf_bin, renderer_name = render_pdf_from_html(
                self.html,
                self.session_data,
                self.calculations,
                23.0,
                self.final_results,
                self.company_payload,
                self.safe_company,
            )

        self.assertEqual(pdf_bin, b"%PDF-PREMIUM%")
        self.assertEqual(renderer_name, "premium-html")
        premium_mock.assert_called_once()
        fallback_mock.assert_not_called()

    def test_fallback_renderer_when_premium_unavailable(self):
        with patch("app.pdf_pipeline.PDFRenderer.render_html_to_pdf", side_effect=PremiumPDFUnavailable("no engine")), \
             patch("app.pdf_pipeline.generate_basic_pdf", return_value=b"%PDF-BASIC%") as fallback_mock:
            pdf_bin, renderer_name = render_pdf_from_html(
                self.html,
                self.session_data,
                self.calculations,
                23.0,
                self.final_results,
                self.company_payload,
                self.safe_company,
            )

        self.assertEqual(pdf_bin, b"%PDF-BASIC%")
        self.assertEqual(renderer_name, "reportlab-fallback")
        fallback_mock.assert_called_once()


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
