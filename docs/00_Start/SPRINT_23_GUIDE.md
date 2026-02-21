# Sprint 23: Certificação de Experiência Premium & BDD Interativo 💎

Este documento orienta o desenvolvimento da **Sprint 23**, focada em elevar o nível de maturidade do fotonPDF através da validação rigorosa dos seus diferenciais competitivos e da experiência lúdica (Premium UX).

## 🎯 Objetivo da Sprint

Implementar uma suíte de testes de **Usabilidade e Interatividade** que valide os diferenciais "IDE-like" e "AEC-focused" definidos no Roadmap, garantindo que a fluidez prometida no mockup seja uma realidade técnica estável.

---

## 🏗️ 1. Pilares de Validação (Cenários BDD)

Os novos testes devem ser implementados em `tests/bdd/test_premium_ux.py` e focar nos seguintes fluxos:

### 1.1 Manipulação Espacial na Mesa de Luz

* **Cenário:** Reordenação Tangível.
  * **Given:** Um documento de 3 páginas aberto na Mesa de Luz.
  * **When:** O usuário arrasta a Página 3 para a posição entre a 1 e a 2.
  * **Then:** O `PDFDocument` virtual deve atualizar sua lista de índices para `[0, 2, 1]` e a renderização deve refletir a nova ordem visual.
* **Cenário:** Seleção em Lote (RubberBand).
  * **Given:** 10 páginas em grid.
  * **When:** O usuário desenha um retângulo capturando 5 páginas.
  * **Then:** O sinal `selectionChanged` deve reportar exatamente 5 IDs de página e as bordas devem ficar em Ciano Neon (#00E5FF).

### 1.2 Precisão de Engenharia no Infinite Canvas

* **Cenário:** Zoom Cirúrgico (Anchor-under-Mouse).
  * **Given:** Uma planta A0 carregada.
  * **When:** O mouse está posicionado na coordenada (500, 500) e o scroll de zoom é disparado.
  * **Then:** O ponto central do viewport deve ser movido proporcionalmente para manter a coordenada (500, 500) sob o cursor.
* **Cenário:** Recuperação de Qualidade Pós-Zoom.
  * **When:** O nível de zoom é alterado para 4.0x.
  * **Then:** Um `QTimer` de 300ms deve ser disparado, seguido por uma nova chamada à `RenderEngine` solicitando pixmaps de alta resolução para as páginas visíveis.

### 1.3 Produtividade via Command Palette

* **Cenário:** Execução Operacional sem Mouse.
  * **Given:** Documento aberto e Paleta de Comandos ativa.
  * **When:** Usuário digita "Girar 90" e pressiona `Enter`.
  * **Then:** O comando deve ser roteado para o `RotatePDFUseCase` e a UI deve notificar o sucesso no `BottomPanel`.

---

## 🛠️ 2. Guia de Implementação Técnica

### A. Simulando Eventos Físicos com `qtbot`

Para testar a "sensação" de drag-and-drop ou zoom, utilize as ferramentas de mouse do `pytest-qt`:

```python
def test_snap_to_grid_drag(qtbot, light_table):
    # Pega o primeiro item
    item = light_table.scene.items()[0]
    start_pos = light_table.mapFromScene(item.pos())
    end_pos = start_pos + QPoint(200, 0)
    
    # Simula o arrasto
    qtbot.mousePress(light_table.viewport(), Qt.MouseButton.LeftButton, pos=start_pos)
    qtbot.mouseMove(light_table.viewport(), pos=end_pos)
    qtbot.mouseRelease(light_table.viewport(), Qt.MouseButton.LeftButton, pos=end_pos)
    
    # Verifica se o sinal de reordenação foi disparado
```

### B. Mocks de Engine p/ Performance

Continue usando mocks para a `RenderEngine` em testes de UI pura, mas use o `stress_pdfs` (arquivos reais) em testes de integração de sistema para validar a latência percebida.

---

## 📝 3. Checklist de Definição de Pronto (DoP)

- [ ] Implementar `tests/gui/test_interactive_physics.py`.
* [ ] Implementar `tests/bdd/test_command_workflow.py`.
* [ ] Garantir 100% de cobertura nos métodos de `InfiniteCanvasView` e `LightTableView`.
* [ ] Validar que nenhum novo `RuntimeError` de C++ foi introduzido pelas simulações de mouse.

---

## 🚀 Próximos Passos

1. **Merge** da branch atual `feature/massive-mockup-ui` -> `develop`.
2. **Checkout** de uma nova branch `sprint-23-ux-certification`.
3. **Draft PR** no início da implementação para acompanhamento.

[[MAP|← Voltar ao Mapa]] | [[DASHBOARD|🎛️ Dashboard]]
