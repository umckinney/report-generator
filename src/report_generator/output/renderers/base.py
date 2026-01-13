"""
Base renderer interface for audience-specific report generation.

This module defines the abstract interface that all audience renderers
must implement.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader


class AudienceRenderer(ABC):
    """
    Abstract base class for audience-specific renderers.

    Each renderer is responsible for:
    1. Filtering/transforming context for its audience
    2. Selecting the appropriate template
    3. Rendering the final HTML output

    Example:
        >>> renderer = ExecutiveRenderer(template_dir)
        >>> context = {"deliverables": [...], "synthesis": {...}}
        >>> html = renderer.render(context, logo_base64="...")
    """

    def __init__(self, template_dir: Path):
        """
        Initialize renderer with template directory.

        Args:
            template_dir: Directory containing Jinja2 templates
        """
        self.template_dir = template_dir
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    @abstractmethod
    def get_template_name(self) -> str:
        """
        Return the template filename for this renderer.

        Returns:
            Template filename (e.g., "template_executive.html")
        """
        pass

    @abstractmethod
    def get_audience_name(self) -> str:
        """
        Return the human-readable audience name.

        Returns:
            Audience name (e.g., "Executive", "Technical", "Partner")
        """
        pass

    @abstractmethod
    def transform_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform context for this audience.

        This method filters, summarizes, or enhances the context
        to be appropriate for the target audience.

        Args:
            context: Original report context

        Returns:
            Transformed context suitable for this audience
        """
        pass

    def render(self, context: Dict[str, Any], logo_base64: str = "") -> str:
        """
        Render report for this audience.

        This is the main entry point for rendering. It:
        1. Transforms the context for this audience
        2. Loads the appropriate template
        3. Renders the final HTML

        Args:
            context: Original report context
            logo_base64: Base64-encoded logo image (optional)

        Returns:
            Rendered HTML string

        Example:
            >>> renderer = ExecutiveRenderer(template_dir)
            >>> html = renderer.render(context, logo_base64="...")
        """
        # Transform context for this audience
        transformed_context = self.transform_context(context)

        # Add logo
        transformed_context["logo_base64"] = logo_base64

        # Add audience metadata
        transformed_context["audience"] = self.get_audience_name()

        # Load and render template
        template = self.jinja_env.get_template(self.get_template_name())
        html = template.render(transformed_context)

        return html
