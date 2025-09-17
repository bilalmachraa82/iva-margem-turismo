"""HTML to PDF rendering helpers with graceful fallback handling."""
from __future__ import annotations

import io
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_PREMIUM_ENV_FLAG = os.getenv("ENABLE_PREMIUM_PDF", "").lower() in {"1", "true", "yes"}


class PremiumPDFUnavailable(RuntimeError):
    """Exception raised when the premium HTML renderer cannot be used."""


@dataclass
class ReportMeta:
    """Metadata attached to premium PDF outputs."""

    title: str
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)

    def as_dict(self) -> Dict[str, str]:
        payload = {"title": self.title}
        if self.author:
            payload["author"] = self.author
        if self.subject:
            payload["subject"] = self.subject
        if self.keywords:
            payload["keywords"] = ", ".join(self.keywords)
        return payload


class PDFRenderer:
    """Best-effort HTML → PDF renderer using WeasyPrint when available."""

    def __init__(self) -> None:
        self._engine = self._load_engine()

    def _load_engine(self) -> Optional[Dict[str, Any]]:
        if not _PREMIUM_ENV_FLAG:
            logger.info("Premium PDF engine disabled. Set ENABLE_PREMIUM_PDF=1 to enable HTML rendering.")
            return None
        try:
            from weasyprint import HTML, CSS  # type: ignore
            try:
                from weasyprint.text.fonts import FontConfiguration  # type: ignore
            except Exception:  # pragma: no cover - compatibility with older releases
                FontConfiguration = None  # type: ignore
            logger.debug("WeasyPrint engine loaded successfully")
            return {
                "HTML": HTML,
                "CSS": CSS,
                "FontConfiguration": FontConfiguration,
            }
        except Exception as exc:  # pragma: no cover - executed when dependency is missing
            logger.info("Premium PDF engine unavailable: %s", exc)
            return None

    @property
    def available(self) -> bool:
        """Return True when the premium engine is ready to be used."""
        return self._engine is not None

    def render_html_to_pdf(self, html: str, metadata: Optional[ReportMeta] = None) -> bytes:
        """Render HTML content to a binary PDF or raise when unavailable."""
        if not self._engine:
            raise PremiumPDFUnavailable("Premium renderer is not available in this environment")

        HTML = self._engine["HTML"]
        CSS = self._engine["CSS"]
        font_config_cls = self._engine["FontConfiguration"]
        font_config = font_config_cls() if font_config_cls else None

        try:
            document = HTML(string=html, base_url=os.getcwd())
            stylesheets = [CSS(string="@page { size: A4; margin: 18mm 16mm 24mm 16mm; }")]
            pdf_bytes = document.write_pdf(
                stylesheets=stylesheets,
                presentational_hints=True,
                font_config=font_config,
            )
        except Exception as exc:  # pragma: no cover - depends on external binary
            logger.exception("Premium renderer failed: %s", exc)
            raise PremiumPDFUnavailable(str(exc)) from exc

        # Apply metadata when supported by the backend implementation.
        if metadata:
            try:
                pdf_bytes = self._inject_metadata(pdf_bytes, metadata)
            except Exception as exc:  # pragma: no cover - metadata injection best-effort
                logger.warning("Unable to inject PDF metadata: %s", exc)
        return pdf_bytes

    def _inject_metadata(self, pdf_bytes: bytes, metadata: ReportMeta) -> bytes:
        """Inject metadata using pypdf if available; leave untouched otherwise."""
        try:
            from pypdf import PdfReader, PdfWriter  # type: ignore
        except Exception as exc:  # pragma: no cover - optional dependency
            logger.info("pypdf not installed, skipping metadata injection: %s", exc)
            return pdf_bytes

        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        meta_payload = metadata.as_dict()
        writer.add_metadata({
            "/Title": meta_payload.get("title", "Relatório IVA sobre Margem"),
            "/Author": meta_payload.get("author", "IVA Margem Premium"),
            "/Subject": meta_payload.get("subject", "Regime especial de IVA sobre a margem"),
            "/Keywords": meta_payload.get("keywords", "IVA, Margem, Turismo"),
        })

        buffer = io.BytesIO()
        writer.write(buffer)
        return buffer.getvalue()


__all__ = ["PDFRenderer", "ReportMeta", "PremiumPDFUnavailable"]
