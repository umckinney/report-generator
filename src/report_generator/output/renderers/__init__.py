"""
Audience-specific renderers for multi-view report generation.

This module provides rendering strategies for different audiences:
- ExecutiveRenderer: High-level, decision-focused
- TechnicalRenderer: Detailed status, technical blockers
- PartnerRenderer: External-safe, sanitized information
"""

from report_generator.output.renderers.base import AudienceRenderer
from report_generator.output.renderers.executive import ExecutiveRenderer
from report_generator.output.renderers.partner import PartnerRenderer
from report_generator.output.renderers.technical import TechnicalRenderer

__all__ = [
    "AudienceRenderer",
    "ExecutiveRenderer",
    "TechnicalRenderer",
    "PartnerRenderer",
]
