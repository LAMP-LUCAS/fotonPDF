# ✨ Funcionalidades do fotonPDF

Este documento detalha as capacidades técnicas do **fotonPDF**, explicando sua implementação, modos de uso e as melhores práticas recomendadas.

---

## 🛠️ 1. Manipulação Core (Motor PDF)

As funcionalidades core são implementadas sobre o adaptador `PyMuPDF` (fitz), garantindo alta performance e baixo consumo de memória.

### 1.1 Girar Páginas (Rotate)

- **O que faz:** Rotaciona páginas específicas ou todo o documento em incrementos de 90°.
- **Implementação:** `src/application/use_cases/rotate_pdf.py`. Utiliza o método `set_rotation` do PyMuPDF.
- **Como utilizar:**
  - **CLI:** `foton rotate --file "doc.pdf" --pages 1,3 --degrees 90`
  - **GUI:** Selecione as miniaturas na barra lateral e use os botões de giro na toolbar.
  - **Context Menu:** Clique com o botão direito no arquivo e escolha `fotonPDF ▸ Girar 90°`.
- **Boas Práticas:** Use o visualizador para confirmar a orientação antes de salvar o arquivo final.

### 1.2 Unir PDFs (Merge 2.0)

- **O que faz:** Combina múltiplos arquivos PDF em um único documento, preservando a ordem desejada.
- **Implementação:** `src/interfaces/gui/state/pdf_state.py` (`append_document`). Implementa um **Documento Virtual** que permite anexação instantânea sem recarregar arquivos.
- **Como utilizar:**
  - **CLI:** `foton merge --files "a.pdf" "b.pdf"`
  - **GUI:** Botão "Unir PDF" ou arraste arquivos diretamente para a **Sidebar de Miniaturas**.
- **Boas Práticas:** Reordene as páginas visualmente na sidebar após unir os arquivos para garantir o fluxo correto do documento.

### 1.3 Separar Páginas (Split)

- **O que faz:** Divide um documento em múltiplos arquivos baseados em intervalos de páginas.
- **Como utilizar:**
  - **CLI:** `foton split --file "doc.pdf" --ranges "1-5,6-10"`
- **Boas Práticas:** Ideal para separar capítulos ou anexos de um documento principal.

---

## 🖥️ 2. Visualizador Fóton (GUI Premium)

Interface gráfica desenvolvida em **PyQt6**, focada em velocidade e fluidez.

### 2.1 Visualização Ultra-Rápida (RenderEngine)

- **Implementação:** `src/interfaces/gui/state/render_engine.py`. Utiliza `QThreadPool` e uma fila de renderização inteligente para evitar crashes e travamentos da UI.
- **Diferencial:** Renderiza apenas as páginas visíveis sob demanda (Lazy Loading), mantendo a memória sob controle.

### 2.2 Navegação e Zoom Inteligente

- **Funções:** Zoom +, Zoom -, 100%, Ajustar Largura e Ajustar Altura.
- **Smarts:** Os botões de **Ajuste** detectam automaticamente a página atual visível e adaptam o zoom às proporções específicas dessa página (ideal para PDFs com tamanhos de página mistos).

### 2.3 Extração Visual

- **O que faz:** Permite selecionar um subconjunto de páginas na barra lateral e salvá-las instantaneamente como um novo arquivo PDF.
- **Como utilizar:** Selecione as páginas na sidebar (Ctrl+Clique) e clique no botão **Extrair** na Toolbar.

---

## 🚀 3. Suíte de Conversão

Ferramentas avançadas para exportar o conteúdo do PDF para outros formatos.

### 3.1 Exportar como Imagem

- **Formatos:** PNG (Alta Resolução), JPG (Compacto), WebP (Otimizado).
- **Implementação:** Gera pixmaps de alta fidelidade (300 DPI) para garantir clareza textual nas imagens.
- **Uso:** Toolbar ▸ Botão "Exportar Imagem".

### 3.2 Exportar SVG (Vetores)

- **O que faz:** Converte a página visível em um gráfico vetorial (SVG), permitindo edição em softwares como Illustrator ou Figma.

### 3.3 Exportar Markdown

- **O que faz:** Extrai o texto do PDF convertendo-o em Markdown estruturado, ideal para anotações em ferramentas como Obsidian ou Notion.

---

## 🖥️ 4. Integração com Sistema Operacional

Conecta o fotonPDF diretamente ao workflow do usuário.

### 4.1 Menu de Contexto (Windows Explorer)

- **O que faz:** Adiciona o menu `fotonPDF ▸` ao clicar com o botão direito em arquivos PDF.
- **Segurança:** Gera arquivos com **Timestamps** automáticos para evitar que o arquivo original seja sobrescrito acidentalmente.

---

## 🔗 Relacionamentos e Navegação

- [[ARCHITECTURE|🏗️ Arquitetura]]: Entenda como os adaptadores e portas sustentam estas features.
- [[DASHBOARD|🎛️ Dashboard]]: Acompanhe o status de implementação de cada funcionalidade.
- [[guides/NEW_OPERATION|➕ Guia de Operações]]: Aprenda a adicionar novas funcionalidades a este ecossistema.

---
[[MAP|← Voltar ao Mapa]]
