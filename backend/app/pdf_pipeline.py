"""Shared helpers for premium PDF pipeline."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from .pdf_renderer import PDFRenderer, PremiumPDFUnavailable, ReportMeta


def resolve_company_payload(company_info: Any, session_data: Dict[str, Any]) -> Dict[str, Any]:
    """Merge company details from request payload and session metadata."""
    payload: Dict[str, Any] = {}

    if company_info:
        if hasattr(company_info, "model_dump"):
            payload = company_info.model_dump()
        elif hasattr(company_info, "dict"):
            payload = company_info.dict()
        elif isinstance(company_info, dict):
            payload = company_info

    if not payload:
        metadata_company = session_data.get("metadata", {}).get("company_info", {})
        if isinstance(metadata_company, dict):
            payload = metadata_company

    if not payload:
        try:
            from .company_config import company_config  # Local import to avoid circular dependency

            info = company_config.get_company_info()
            payload = {
                "name": getattr(info, "name", None),
                "nif": getattr(info, "nif", None),
                "cae": getattr(info, "cae_code", None),
            }
        except Exception:  # pragma: no cover - defensive fallback
            payload = {}

    return {k: v for k, v in (payload or {}).items() if v}


def sanitize_company_name(name: str) -> str:
    return str(name or "Empresa").replace("/", " ").replace("\\", " ").strip()


def render_pdf_from_html(
    html_content: str,
    session_data: Dict[str, Any],
    calculations: List[Dict[str, Any]],
    vat_rate: float,
    final_results: Dict[str, Any],
    company_payload: Dict[str, Any],
    safe_company: str,
) -> Tuple[bytes, str]:
    """Render premium PDF or fall back to ReportLab implementation."""
    renderer = PDFRenderer()
    renderer_name = "premium-html"

    metadata = ReportMeta(
        title=f"Relatório IVA sobre Margem - {safe_company}",
        author=company_payload.get("name") or safe_company,
        subject=f"IVA sobre Margem ({vat_rate:.2f}%)",
        keywords=[
            safe_company,
            "IVA",
            "Margem",
            "Regime Especial",
            "Consultoria Financeira",
        ],
    )

    try:
        pdf_bin = renderer.render_html_to_pdf(html_content, metadata)
    except PremiumPDFUnavailable:
        renderer_name = "reportlab-fallback"
        from .pdf_export import generate_pdf_report as generate_basic_pdf
        pdf_bin = generate_basic_pdf(
            session_data=session_data,
            calculation_results=calculations,
            vat_rate=vat_rate,
            final_results=final_results,
        )

    return pdf_bin, renderer_name
