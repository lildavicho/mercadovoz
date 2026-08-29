"""MercadoVoz Sprint 0 text parser."""

from .parser import parse_text
from .corrections import apply_correction

__all__ = ["parse_text", "apply_correction"]
__version__ = "0.1.0"

