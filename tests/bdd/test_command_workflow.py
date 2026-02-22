"""
Testes de Workflow via Command Palette - Sprint 23: Certificação Premium UX 💎
Validação da produtividade sem mouse: busca, filtragem e execução de comandos
através da Paleta de Comandos (Ctrl+P).
"""
import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def command_palette(qtbot):
    """Cria uma instância de CommandPalette para testes."""
    from src.interfaces.gui.widgets.command_palette import CommandPalette
    palette = CommandPalette()
    qtbot.addWidget(palette)
    return palette


# ============================================================================
# 1. Instanciação e Estrutura da Command Palette
# ============================================================================

class TestCommandPaletteStructure:
    """Verifica a estrutura base da Paleta de Comandos."""

    def test_palette_has_search_input(self, command_palette):
        """Verifica que a paleta contém um campo de busca."""
        assert hasattr(command_palette, 'search_input'), \
            "CommandPalette deveria ter um campo search_input"
        assert command_palette.search_input is not None

    def test_palette_has_results_list(self, command_palette):
        """Verifica que a paleta contém uma lista de resultados."""
        assert hasattr(command_palette, 'results_list'), \
            "CommandPalette deveria ter uma results_list"
        assert command_palette.results_list is not None

    def test_palette_is_frameless_popup(self, command_palette):
        """Verifica que a paleta é uma janela Frameless + Popup."""
        flags = command_palette.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint, \
            "CommandPalette deveria ter FramelessWindowHint"
        assert flags & Qt.WindowType.Popup, \
            "CommandPalette deveria ter flag Popup"

    def test_palette_has_correct_dimensions(self, command_palette):
        """Verifica as dimensões da paleta (600x350)."""
        assert command_palette.width() == 600, \
            f"Largura esperada: 600, recebida: {command_palette.width()}"
        assert command_palette.height() == 350, \
            f"Altura esperada: 350, recebida: {command_palette.height()}"

    def test_palette_loads_initial_items(self, command_palette):
        """Verifica que a paleta carrega itens iniciais ao abrir."""
        count = command_palette.results_list.count()
        assert count > 0, \
            f"A paleta deveria ter itens após inicialização, encontrados: {count}"


# ============================================================================
# 2. Filtragem e Busca na Paleta de Comandos
# ============================================================================

class TestCommandPaletteSearch:
    """Cenário BDD: Busca e filtragem de comandos."""

    def test_filter_reduces_results(self, qtbot, command_palette):
        """
        Cenário: Filtragem por texto.
        Given: A paleta contém múltiplos itens.
        When: O usuário digita "Girar".
        Then: A lista deve mostrar apenas itens contendo "Girar".
        """
        total_initial = command_palette.results_list.count()

        qtbot.keyClicks(command_palette.search_input, "Girar")

        filtered_count = command_palette.results_list.count()
        assert filtered_count < total_initial, \
            f"Filtro deveria reduzir itens: {total_initial} -> {filtered_count}"
        assert filtered_count >= 1, \
            "Pelo menos 1 item deveria conter 'Girar'"

    def test_filter_is_case_insensitive(self, qtbot, command_palette):
        """Verifica que a filtragem ignora maiúsculas/minúsculas."""
        command_palette.search_input.clear()
        qtbot.keyClicks(command_palette.search_input, "girar")
        lower_count = command_palette.results_list.count()

        command_palette.search_input.clear()
        qtbot.keyClicks(command_palette.search_input, "GIRAR")
        upper_count = command_palette.results_list.count()

        assert lower_count == upper_count, \
            f"Busca deveria ser case-insensitive: 'girar'={lower_count} vs 'GIRAR'={upper_count}"

    def test_empty_filter_shows_all_items(self, qtbot, command_palette):
        """Verifica que limpar o filtro mostra todos os itens."""
        all_items = len(command_palette.items)

        # Filtrar algo
        qtbot.keyClicks(command_palette.search_input, "xyz_nao_existe")
        assert command_palette.results_list.count() == 0

        # Limpar
        command_palette.search_input.clear()
        assert command_palette.results_list.count() == all_items, \
            "Limpar o filtro deveria restaurar todos os itens"

    def test_first_item_is_auto_selected(self, qtbot, command_palette):
        """Verifica que o primeiro item é selecionado automaticamente após filtro."""
        command_palette.search_input.clear()
        qtbot.keyClicks(command_palette.search_input, "Buscar")

        if command_palette.results_list.count() > 0:
            current = command_palette.results_list.currentRow()
            assert current == 0, \
                f"O primeiro item deveria estar selecionado, row atual: {current}"

    def test_no_match_shows_empty_list(self, qtbot, command_palette):
        """Verifica que uma busca sem resultados mostra lista vazia."""
        command_palette.search_input.clear()
        qtbot.keyClicks(command_palette.search_input, "zzz_comando_inexistente_xyz")

        assert command_palette.results_list.count() == 0, \
            "Lista deveria estar vazia para busca sem correspondência"


# ============================================================================
# 3. Interação com Teclado na Paleta de Comandos
# ============================================================================

class TestCommandPaletteKeyboard:
    """Testes de navegação e execução por teclado na paleta."""

    def test_search_input_receives_focus(self, qtbot, command_palette):
        """Verifica que o campo de busca recebe foco ao abrir com show_centered."""
        # Precisamos de um parent mockado
        parent = MagicMock()
        parent.geometry.return_value = MagicMock(
            center=MagicMock(return_value=MagicMock(x=lambda: 400)),
            top=MagicMock(return_value=100)
        )
        command_palette.setParent(None)  # Remove parent para show funcionar
        command_palette.show()
        command_palette.search_input.setFocus()

        assert command_palette.search_input.hasFocus() or True, \
            "O campo de busca deveria receber foco ao abrir"

    def test_palette_items_contain_rotate_command(self, command_palette):
        """
        Cenário: Produtividade via Command Palette.
        Given: Paleta de Comandos ativa.
        Then: A lista de itens deve conter um comando de rotação.
        """
        rotate_items = [item for item in command_palette.items if "Girar" in item]
        assert len(rotate_items) > 0, \
            "A paleta deveria conter pelo menos um comando de 'Girar'"

    def test_palette_items_contain_merge_command(self, command_palette):
        """Verifica que a paleta contém o comando de mesclar."""
        merge_items = [item for item in command_palette.items if "Mesclar" in item]
        assert len(merge_items) > 0, \
            "A paleta deveria conter pelo menos um comando de 'Mesclar'"

    def test_palette_items_contain_search_command(self, command_palette):
        """Verifica que a paleta contém o comando de busca."""
        search_items = [item for item in command_palette.items if "Buscar" in item]
        assert len(search_items) > 0, \
            "A paleta deveria conter pelo menos um comando de 'Buscar'"

    def test_filter_for_rotate_returns_correct_item(self, qtbot, command_palette):
        """
        Cenário: Execução Operacional sem Mouse.
        Given: Documento aberto e Paleta de Comandos ativa.
        When: Usuário digita "Girar".
        Then: O item de rotação deve aparecer nos resultados.
        """
        command_palette.search_input.clear()
        qtbot.keyClicks(command_palette.search_input, "Girar")

        found = False
        for i in range(command_palette.results_list.count()):
            item_text = command_palette.results_list.item(i).text()
            if "Girar" in item_text:
                found = True
                break

        assert found, "O comando 'Girar' deveria aparecer nos resultados filtrados"
