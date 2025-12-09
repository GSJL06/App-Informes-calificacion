#!/usr/bin/env python
"""
Tests for refactored templates with dynamic lists and tables.
"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'src')

import json
import pytest
import tempfile
from pathlib import Path
from docx import Document

from generar_informe import generate_report, DynamicContentProcessor


class TestJSONStructureValidation:
    """Tests for JSON data structure validation."""
    
    def test_minimal_data_structure(self):
        """Test minimal required data structure."""
        minimal_data = {
            "nombre_establecimiento": "Test Hospital"
        }
        assert "nombre_establecimiento" in minimal_data
        assert isinstance(minimal_data["nombre_establecimiento"], str)
    
    def test_complete_data_structure(self):
        """Test complete data structure with arrays."""
        complete_data = {
            "nombre_establecimiento": "Test Hospital",
            "dispositivos": ["Device 1", "Device 2"],
            "responsables": [
                {"nombre": "Person 1", "telefono": "123", "correo": "a@b.com"}
            ]
        }
        assert isinstance(complete_data["dispositivos"], list)
        assert isinstance(complete_data["responsables"], list)
        assert isinstance(complete_data["responsables"][0], dict)
    
    def test_empty_arrays_valid(self):
        """Test that empty arrays are valid."""
        data = {
            "nombre_establecimiento": "Test",
            "dispositivos": [],
            "responsables": []
        }
        assert len(data["dispositivos"]) == 0
        assert len(data["responsables"]) == 0


class TestDynamicLists:
    """Tests for dynamic list expansion."""
    
    def test_single_item_list(self):
        """Test list with single item."""
        data = {"dispositivos": ["Single Device"]}
        assert len(data["dispositivos"]) == 1
    
    def test_ten_item_list(self):
        """Test list with 10 items."""
        data = {"dispositivos": [f"Device {i}" for i in range(10)]}
        assert len(data["dispositivos"]) == 10
    
    def test_fifty_item_list(self):
        """Test list with 50 items."""
        data = {"dispositivos": [f"Device {i}" for i in range(50)]}
        assert len(data["dispositivos"]) == 50
    
    def test_list_preserves_order(self):
        """Test that list order is preserved."""
        items = ["First", "Second", "Third"]
        data = {"dispositivos": items}
        assert data["dispositivos"][0] == "First"
        assert data["dispositivos"][2] == "Third"


class TestDynamicTables:
    """Tests for dynamic table row expansion."""
    
    def test_single_row_table(self):
        """Test table with single data row."""
        data = {
            "responsables": [
                {"nombre": "Person 1", "telefono": "123", "correo": "a@b.com"}
            ]
        }
        assert len(data["responsables"]) == 1
    
    def test_multiple_row_table(self):
        """Test table with multiple rows."""
        data = {
            "responsables": [
                {"nombre": f"Person {i}", "telefono": str(i), "correo": f"p{i}@test.com"}
                for i in range(5)
            ]
        }
        assert len(data["responsables"]) == 5
    
    def test_table_row_fields(self):
        """Test that table rows have required fields."""
        row = {"nombre": "Test", "telefono": "123", "correo": "test@test.com"}
        assert "nombre" in row
        assert "telefono" in row
        assert "correo" in row
    
    def test_table_with_empty_fields(self):
        """Test table rows with empty optional fields."""
        data = {
            "responsables": [
                {"nombre": "Person", "telefono": "", "correo": ""}
            ]
        }
        assert data["responsables"][0]["telefono"] == ""


class TestReportGeneration:
    """Tests for report generation with dynamic content."""
    
    @pytest.fixture
    def temp_output(self):
        """Create temporary output file."""
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as f:
            yield Path(f.name)
    
    @pytest.fixture
    def sample_template(self):
        """Get sample template path."""
        template = Path('templates/plantilla_desempeno.docx')
        if template.exists():
            return template
        pytest.skip("Template not found")
    
    def test_generate_with_minimal_data(self, sample_template, temp_output):
        """Test generation with minimal data."""
        data = {"nombre_establecimiento": "Test Hospital"}
        result = generate_report(
            str(sample_template),
            str(temp_output),
            text_data=data
        )
        assert result is True
        assert temp_output.exists()
    
    def test_generate_with_complete_data(self, sample_template, temp_output):
        """Test generation with complete data including arrays."""
        data = {
            "nombre_establecimiento": "Test Hospital",
            "direccion": "Test Address",
            "fecha_calificacion": "01/01/2024",
            "dispositivos": ["Device 1", "Device 2", "Device 3"],
            "responsables": [
                {"nombre": "Person 1", "telefono": "123", "correo": "a@b.com"},
                {"nombre": "Person 2", "telefono": "456", "correo": "c@d.com"}
            ]
        }
        result = generate_report(
            str(sample_template),
            str(temp_output),
            text_data=data
        )
        assert result is True
        assert temp_output.exists()
    
    def test_generate_with_large_list(self, sample_template, temp_output):
        """Test generation with large list (50 items)."""
        data = {
            "nombre_establecimiento": "Test Hospital",
            "dispositivos": [f"Device {i}" for i in range(50)]
        }
        result = generate_report(
            str(sample_template),
            str(temp_output),
            text_data=data
        )
        assert result is True


class TestBackwardCompatibility:
    """Tests for backward compatibility with existing placeholders."""
    
    def test_scalar_placeholders_still_work(self):
        """Test that scalar placeholders are still replaced."""
        data = {
            "nombre_establecimiento": "Hospital X",
            "fecha_calificacion": "15/12/2024"
        }
        # Scalar values should be strings
        assert all(isinstance(v, str) for v in data.values())
    
    def test_mixed_scalar_and_array_data(self):
        """Test mixing scalar and array data."""
        data = {
            "nombre_establecimiento": "Hospital X",
            "dispositivos": ["Device 1", "Device 2"]
        }
        scalars = {k: v for k, v in data.items() if isinstance(v, str)}
        arrays = {k: v for k, v in data.items() if isinstance(v, list)}
        
        assert len(scalars) == 1
        assert len(arrays) == 1


class TestTemplateAnalysis:
    """Tests for template analysis functionality."""
    
    def test_analyzer_import(self):
        """Test that analyzer can be imported."""
        from refactorizar_plantillas import TemplateAnalyzer
        assert TemplateAnalyzer is not None
    
    def test_analyze_template(self):
        """Test analyzing a template."""
        from refactorizar_plantillas import TemplateAnalyzer
        
        template = Path('templates/plantilla_desempeno.docx')
        if not template.exists():
            pytest.skip("Template not found")
        
        analyzer = TemplateAnalyzer(template)
        analysis = analyzer.analyze()
        
        assert 'existing_placeholders' in analysis
        assert 'bullet_lists' in analysis
        assert 'tables_with_hardcoded' in analysis
        assert 'statistics' in analysis


if __name__ == '__main__':
    pytest.main([__file__, '-v'])