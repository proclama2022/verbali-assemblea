from abc import ABC, abstractmethod
from typing import Dict, Any, List
from docx import Document
from datetime import datetime, date
import re
import streamlit as st

class DocumentTemplate(ABC):
    """Base class for document templates"""
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Get the template name"""
        pass
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Get list of required fields for this template"""
        pass
    
    @abstractmethod
    def generate_document(self, data: Dict[str, Any]) -> Document:
        """Generate document from data"""
        pass
    
    @abstractmethod
    def get_form_fields(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get form fields configuration for Streamlit UI"""
        pass


class DocumentTemplateFactory:
    """Factory to create document templates"""
    
    _templates = {}
    
    @classmethod
    def register_template(cls, template_type: str, template_class):
        """Register a new template type"""
        cls._templates[template_type.lower()] = template_class
    
    @classmethod
    def create_template(cls, template_type: str) -> DocumentTemplate:
        """Create a template instance"""
        if template_type.lower() not in cls._templates:
            raise ValueError(f"Tipo template non supportato: {template_type}")
        
        return cls._templates[template_type.lower()]()
    
    @classmethod
    def get_available_templates(cls) -> List[str]:
        """Get list of available template types"""
        return list(cls._templates.keys()) 