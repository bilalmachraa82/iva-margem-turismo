"""
Company Configuration System
Professional-grade company data management for PDF reports
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class CompanyInfo:
    """Complete company information for report personalization"""

    # Basic company details
    name: str = "Agência de Viagens Excel Modelo Lda"
    nif: str = "123456789"

    # Address details
    address_line1: str = "Rua das Agências de Viagens, 123"
    address_line2: str = "2º Andar, Sala 201"
    postal_code: str = "1000-001"
    city: str = "Lisboa"
    country: str = "Portugal"

    # Contact information
    phone: str = "+351 21 123 4567"
    email: str = "geral@agenciaturismo.pt"
    website: str = "www.agenciaturismo.pt"

    # Additional details
    cae_code: str = "79110"  # CAE para agências de viagens
    registration_number: str = "12345"
    conservatory: str = "Conservatória do Registo Comercial de Lisboa"

    # Branding
    logo_path: Optional[str] = None
    primary_color: str = "#2563eb"  # Blue
    secondary_color: str = "#1e40af"  # Dark blue
    accent_color: str = "#10b981"  # Green for positive values

    # Legal & compliance
    certified_accountant: str = "Dr. João Silva (CC 12345)"
    legal_representative: str = "Maria Santos"

    def get_full_address(self) -> str:
        """Return formatted full address"""
        parts = [self.address_line1]
        if self.address_line2:
            parts.append(self.address_line2)
        parts.append(f"{self.postal_code} {self.city}")
        if self.country and self.country != "Portugal":
            parts.append(self.country)
        return ", ".join(parts)

    def get_contact_info(self) -> str:
        """Return formatted contact information"""
        contacts = []
        if self.phone:
            contacts.append(f"Tel: {self.phone}")
        if self.email:
            contacts.append(f"Email: {self.email}")
        if self.website:
            contacts.append(f"Web: {self.website}")
        return " | ".join(contacts)

class CompanyConfigManager:
    """Professional company configuration management"""

    def __init__(self, config_file: str = "company_config.json"):
        self.config_file = Path(config_file)
        self._company_info: Optional[CompanyInfo] = None
        self.load_config()

    def load_config(self) -> CompanyInfo:
        """Load company configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._company_info = CompanyInfo(**data)
                    logger.info(f"Loaded company config from {self.config_file}")
            else:
                self._company_info = CompanyInfo()
                self.save_config()
                logger.info("Created default company configuration")
        except Exception as e:
            logger.error(f"Error loading company config: {e}")
            self._company_info = CompanyInfo()

        return self._company_info

    def save_config(self) -> bool:
        """Save current company configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self._company_info), f, indent=2, ensure_ascii=False)
            logger.info(f"Saved company config to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving company config: {e}")
            return False

    def update_company_info(self, **kwargs) -> CompanyInfo:
        """Update company information with provided fields"""
        for key, value in kwargs.items():
            if hasattr(self._company_info, key):
                setattr(self._company_info, key, value)
            else:
                logger.warning(f"Unknown company field: {key}")

        self.save_config()
        return self._company_info

    def get_company_info(self) -> CompanyInfo:
        """Get current company information"""
        if self._company_info is None:
            self.load_config()
        return self._company_info

    def get_pdf_header_data(self) -> Dict[str, Any]:
        """Get data formatted for PDF header"""
        company = self.get_company_info()
        return {
            "company_name": company.name,
            "nif": company.nif,
            "address": company.get_full_address(),
            "contact": company.get_contact_info(),
            "logo_path": company.logo_path,
            "primary_color": company.primary_color,
            "secondary_color": company.secondary_color
        }

    def get_pdf_footer_data(self) -> Dict[str, Any]:
        """Get data formatted for PDF footer"""
        company = self.get_company_info()
        return {
            "certified_accountant": company.certified_accountant,
            "legal_representative": company.legal_representative,
            "registration_info": f"Reg. Comercial: {company.registration_number} | CAE: {company.cae_code}",
            "conservatory": company.conservatory
        }

# Global instance for easy access
company_config = CompanyConfigManager()

# Pre-configured company profiles for common use cases
COMPANY_PROFILES = {
    "agencia_lisboa": CompanyInfo(
        name="Viagens & Descobertas Lda",
        nif="123456789",
        address_line1="Avenida da Liberdade, 225",
        address_line2="3º Piso",
        postal_code="1250-142",
        city="Lisboa",
        phone="+351 21 123 4567",
        email="info@viagensdescoberta.pt",
        website="www.viagensdescoberta.pt",
        certified_accountant="Dr. Ana Costa (CC 54321)",
        legal_representative="João Pereira"
    ),

    "agencia_porto": CompanyInfo(
        name="Norte Turismo - Agência de Viagens Lda",
        nif="987654321",
        address_line1="Rua de Santa Catarina, 150",
        postal_code="4000-447",
        city="Porto",
        phone="+351 22 987 6543",
        email="geral@norteturismo.pt",
        website="www.norteturismo.pt",
        primary_color="#c2410c",  # Orange theme
        secondary_color="#9a3412",
        certified_accountant="Dr. Miguel Santos (CC 98765)",
        legal_representative="Clara Fernandes"
    ),

    "agencia_premium": CompanyInfo(
        name="Luxury Travel Portugal Lda",
        nif="555666777",
        address_line1="Quinta da Fonte, Lote 5",
        address_line2="Complexo Empresarial",
        postal_code="2750-642",
        city="Cascais",
        phone="+351 21 555 6677",
        email="concierge@luxurytravel.pt",
        website="www.luxurytravel.pt",
        primary_color="#7c3aed",  # Purple theme
        secondary_color="#5b21b6",
        accent_color="#f59e0b",
        certified_accountant="Dr. Patricia Oliveira (CC 11111)",
        legal_representative="Ricardo Silva"
    )
}

def apply_company_profile(profile_name: str) -> bool:
    """Apply a pre-configured company profile"""
    if profile_name in COMPANY_PROFILES:
        profile = COMPANY_PROFILES[profile_name]
        company_config._company_info = profile
        company_config.save_config()
        logger.info(f"Applied company profile: {profile_name}")
        return True
    else:
        logger.error(f"Unknown company profile: {profile_name}")
        return False