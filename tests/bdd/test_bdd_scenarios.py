
import pytest
from PyQt6.QtCore import Qt

class TestBDDFeatures:
    """
    Validation Suite for Core Features (BDD Style).
    Tests critical user flows with stress-test files.
    """

    def test_scenario_open_large_a0_drawing(self, qtbot, main_window, stress_pdfs):
        """
        Scenario: User opens a high-resolution A0 drawing.
        Given the application is ready
        When I open 'test_A0.pdf'
        Then the viewer should display a canvas of approx 841x1189 mm
        And the UI should remain responsive
        """
        # When
        pdf_path = stress_pdfs["large_a0"]
        main_window.open_file(pdf_path)
        
        # Then (Wait for async load)
        def check_loaded():
            if main_window.viewer is None:
                raise AssertionError("Viewer not ready yet")
            assert main_window.viewer.current_doc is not None
            assert main_window.viewer.current_doc.page_count >= 1
        qtbot.waitUntil(check_loaded, timeout=10000)
        
        # Check Inspector dimensions
        inspector = main_window.side_bar_right.get_panel("inspector")
        assert inspector is not None
        
        def check_dimensions():
            text = inspector.lbl_dims.text()
            assert "841" in text or "842" in text
            assert "1189" in text
        qtbot.waitUntil(check_dimensions, timeout=5000)

    def test_scenario_navigate_multi_page(self, qtbot, main_window, stress_pdfs):
        """
        Scenario: User navigates a multi-page document.
        Given 'test_multi_page_text.pdf' is open
        When I go to page 50
        Then the viewer should display page 50
        """
        # Given
        pdf_path = stress_pdfs["multi_page_text"]
        main_window.open_file(pdf_path)
        
        def check_ready():
            if main_window.viewer is None: raise AssertionError("Viewer None")
            assert main_window.viewer.current_doc is not None
        qtbot.waitUntil(check_ready, timeout=5000)
        
        # When (Simulate Navigation)
        main_window.viewer.scroll_to_page(49) # 0-indexed
        
        # Then
        assert main_window.viewer.get_current_page_index() == 49
        
    def test_scenario_open_complex_vectors(self, qtbot, main_window, stress_pdfs):
        """
        Scenario: User opens a document with thousands of vector elements.
        Given the application is ready
        When I open 'test_complex_vectors.pdf'
        Then the application should not crash
        And the page should render eventually
        """
        # When
        pdf_path = stress_pdfs["complex_vectors"]
        main_window.open_file(pdf_path)
        
        # Then
        def check_loaded():
            if main_window.viewer is None: raise AssertionError("Viewer None")
            assert main_window.viewer.current_doc is not None
        qtbot.waitUntil(check_loaded, timeout=10000) # Give more time for complex allocs
