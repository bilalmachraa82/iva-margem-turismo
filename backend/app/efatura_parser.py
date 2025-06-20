"""
E-Fatura CSV Parser for IVA Margem Turismo
Handles both sales (vendas) and purchases (compras) CSV files from Portal das Finanças
"""
import csv
import io
import re
from datetime import datetime
from typing import Dict, List, Any, Tuple
import uuid
import logging

logger = logging.getLogger(__name__)

# --- Início da Lógica de Enriquecimento de Dados ---

# Regras de categorização baseadas em palavras-chave
# A ordem é importante: regras mais específicas devem vir primeiro.
COST_CATEGORIZATION_RULES = [
    # Transporte Aéreo
    ({"ryanair", "tap", "easyjet", "lufthansa", "air france", "klm", "voo", "flight", "aeroporto", "airport"}, "Transporte Aéreo", "✈️"),
    # Alojamento
    ({"hotel", "hostel", "booking.com", "airbnb", "alojamento", "resort", "pousada"}, "Alojamento", "🏨"),
    # Transporte Terrestre
    ({"comboio", "train", "cp", "fertagus", "flixbus", "rede expressos", "autocarro", "bus", "uber", "bolt", "táxi"}, "Transporte Terrestre", "🚆"),
    # Aluguer de Viatura
    ({"rent-a-car", "aluguer de carro", "hertz", "avis", "europcar", "sixt", "goldcar"}, "Aluguer de Viatura", "🚗"),
    # Restauração
    ({"restaurante", "comida", "refeição", "jantar", "almoço", "food", "meal", "restaurant"}, "Restauração", "🍽️"),
    # Atividades e Tours
    ({"tour", "excursão", "museu", "bilhetes", "tickets", "guia", "passeio"}, "Atividades e Tours", "🎟️"),
    # Seguros
    ({"seguro", "insurance", "fidelidade", "allianz", "europ assistance"}, "Seguros", "🛡️"),
    # Combustível
    ({"galp", "repsol", "bp", "cepsa", "combustível", "gasolina", "gasóleo"}, "Combustível", "⛽"),
    # Portagens
    ({"portagem", "scut", "via verde"}, "Portagens", "🛣️"),
    # Taxas e Serviços
    ({"comissão", "taxa", "serviço"}, "Taxas e Serviços", "💼"),
]

DEFAULT_CATEGORY = ("Outros Custos", "🧾")

def _enrich_cost_data(cost_item: Dict[str, Any]) -> Dict[str, Any]:
    """Enriquece um item de custo com uma categoria e um ícone."""
    search_text = (cost_item.get("supplier", "") + " " + cost_item.get("description", "")).lower()

    cost_item["category"] = DEFAULT_CATEGORY[0]
    cost_item["icon"] = DEFAULT_CATEGORY[1]

    for keywords, category, icon in COST_CATEGORIZATION_RULES:
        if any(re.search(r'\b' + re.escape(keyword) + r'\b', search_text) for keyword in keywords):
            cost_item["category"] = category
            cost_item["icon"] = icon
            break

    return cost_item

# --- Fim da Lógica de Enriquecimento de Dados ---

class EFaturaParser:
    """Parser for e-Fatura CSV files (vendas and compras)"""

    @staticmethod
    def parse(vendas_content: bytes, compras_content: bytes) -> Dict[str, Any]:
        """Parse both e-Fatura CSV files, assuming correct files are uploaded."""
        sales, sales_errors = EFaturaParser._parse_csv(vendas_content, EFaturaParser._parse_venda_row)
        costs, costs_errors = EFaturaParser._parse_csv(compras_content, EFaturaParser._parse_compra_row)

        company_name = "A Minha Empresa"

        return {
            "sales": sales,
            "costs": costs,
            "metadata": {
                "source": "e-Fatura CSV",
                "company_name": company_name,
                "errors": sales_errors + costs_errors
            }
        }

    @staticmethod
    def _parse_csv(content: bytes, row_parser) -> Tuple[List[Dict], List[str]]:
        """Generic CSV parser"""
        items, errors = [], []
        encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        text_content = None
        for encoding in encodings:
            try:
                text_content = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if text_content is None:
            errors.append("Failed to decode CSV with any tried encodings.")
            return [], errors

        try:
            lines = text_content.strip().splitlines()
            if not lines:
                return [], []
            
            header = lines[0]
            # Fix common encoding issues in header before parsing
            corrected_header = header.replace('N�', 'Nº')\
                                     .replace('Emiss�o', 'Emissão')\
                                     .replace('Tribut�vel', 'Tributável')\
                                     .replace('Situa��o', 'Situação')\
                                     .replace('Comunica��o  Emitente', 'Comunicação Emitente')\
                                     .replace('Comunica��o  Adquirente', 'Comunicação Adquirente')\
                                     .replace('cr�dito', 'crédito')
            lines[0] = corrected_header
            
            reader = csv.DictReader(lines, delimiter=';')
            for i, row in enumerate(reader, 2):
                try:
                    item, parse_errors = row_parser(row, i)
                    if item: items.append(item)
                    if parse_errors: errors.extend(parse_errors)
                except Exception as e:
                    errors.append(f"Error parsing row {i}: {e}")
        except Exception as e:
            errors.append(f"Error reading CSV: {e}")
            
        return items, errors

    @staticmethod
    def _parse_venda_row(row: Dict[str, str], row_num: int) -> Tuple[Dict, List[str]]:
        """Parses a single sale row from the 'e-fatura venda.csv' file."""
        errors = []
        client_nif = row.get('NIF Adquirente', '')
        doc_type = row.get('Tipo do Documento', '')
        multiplier = -1 if 'crédito' in doc_type.lower() else 1

        sale = {
            "id": f"s_{uuid.uuid4().hex[:8]}",
            "number": row.get('Nº Documento / ATCUD', f'DOC_{row_num}'),
            "date": EFaturaParser._parse_date(row.get('Data Emissão', '')),
            "client": f"Cliente NIF {client_nif}" if client_nif else "Cliente Indiferenciado",
            "client_nif": client_nif,
            "amount": EFaturaParser._parse_amount(row.get('Base Tributável', '0')) * multiplier,
            "vat_amount": EFaturaParser._parse_amount(row.get('IVA', '0')) * multiplier,
            "gross_total": EFaturaParser._parse_amount(row.get('Total', '0')) * multiplier,
            "issuer": "", # Issuer (own company) is not in this file
            "doc_type": doc_type,
            "linked_costs": []
        }
        return sale, errors

    @staticmethod
    def _parse_compra_row(row: Dict[str, str], row_num: int) -> Tuple[Dict, List[str]]:
        """Parses a single cost row from the 'e-fatura compras.csv' file."""
        errors = []
        supplier_raw = row.get('Emitente', '')
        supplier_nif, supplier_name = EFaturaParser._parse_entity(supplier_raw)
        doc_type = row.get('Tipo', '')
        multiplier = -1 if 'crédito' in doc_type.lower() else 1

        cost = {
            "id": f"c_{uuid.uuid4().hex[:8]}",
            "supplier": supplier_name,
            "supplier_nif": supplier_nif,
            "description": f"Compra - {doc_type}",
            "date": EFaturaParser._parse_date(row.get('Data Emissão', '')),
            "amount": EFaturaParser._parse_amount(row.get('Base Tributável', '0')) * multiplier,
            "vat_amount": EFaturaParser._parse_amount(row.get('IVA', '0')) * multiplier,
            "gross_total": EFaturaParser._parse_amount(row.get('Total', '0')) * multiplier,
            "document_number": row.get('Nº Fatura / ATCUD', f'DOC_{row_num}'),
            "linked_sales": []
        }

        cost = _enrich_cost_data(cost)
        return cost, errors

    @staticmethod
    def _parse_entity(raw_string: str) -> Tuple[str, str]:
        """Parses an entity string in 'NIF - Name' format."""
        if ' - ' in raw_string:
            parts = raw_string.split(' - ', 1)
            if parts[0].strip().isdigit():
                return parts[0].strip(), parts[1].strip()
        return "", raw_string.strip() if raw_string else "Desconhecido"

    @staticmethod
    def _parse_amount(value: str) -> float:
        """
        Parse amount string to float.
        Handles formats like '1.234,56 €' or '1234,56' and common encoding errors.
        """
        if not value:
            return 0.0
        
        # Remove currency symbols (€ or its replacement character � from encoding errors) and whitespace.
        cleaned = value.replace('€', '').replace('�', '').replace(' ', '').strip()
        
        # Normalize number format for Portuguese locale:
        # - Remove thousand separators ('.')
        # - Replace decimal separator (',') with '.'
        if '.' in cleaned and ',' in cleaned:
            # Format '1.234,56' -> '1234.56'
            cleaned = cleaned.replace('.', '').replace(',', '.')
        else:
            # Format '1234,56' -> '1234.56'
            cleaned = cleaned.replace(',', '.')
            
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            logger.warning(f"Could not parse amount. Original value: '{value}', Cleaned value: '{cleaned}'")
            return 0.0

    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Parse date string to ISO format."""
        if not date_str: return ''
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d']
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).strftime('%Y-%m-%d')
            except ValueError:
                continue
        return ''