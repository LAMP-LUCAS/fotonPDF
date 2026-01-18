# ✨ Funcionalidades do fotonPDF

Este documento detalha as capacidades técnicas do **fotonPDF**, explicando sua implementação profunda, modos de uso avançados e as melhores práticas recomendadas para produtividade máxima.

---

## 🛠️ 1. Manipulação Core (Motor PDF)

As funcionalidades core são implementadas sobre o adaptador `PyMuPDF` (fitz), garantindo alta fidelidade e performance.

### 1.1 Girar Páginas (Rotate)

- **O que faz:** Rotaciona páginas específicas ou todo o documento em incrementos de 90°.
- **Interno:** Implementado via `src/application/use_cases/rotate_pdf.py`. No modo visual, a rotação é aplicada no `PDFStateManager` como um `rotation_offset`, permitindo que o usuário visualize a mudança instantaneamente sem modificar o arquivo original até o momento do "Salvar".
- **Como utilizar:**
  - **GUI:** Selecione as miniaturas na barra lateral (use `Ctrl` para múltiplas) e clique em **Girar -90°** ou **Girar +90°**.
  - **CLI:** `foton rotate --file "doc.pdf" --pages 1,3 --degrees 90`
- **Integridade**: O sistema sincroniza o índice visual com o estado interno, garantindo que a página rotacionada seja exatamente a que você selecionou, mesmo após reordenações.

### 1.2 Unir PDFs (Merge 2.0 - Documento Virtual)

- **O que faz:** Combina múltiplos arquivos PDF em um único fluxo de trabalho contínuo.
- **Diferencial Técnico:** Introduz o conceito de **Documento Virtual**. Em vez de unir arquivos fisicamente no disco e recarregar, o fotonPDF gerencia uma lista dinâmica de referências para páginas de diferentes arquivos fonte. Isso torna a "unificação" instantânea.
- **Interface Inteligente:**
  - Arraste arquivos para a **Sidebar** para anexá-los ao documento atual.
  - Arraste para o **Centro** para abrir como um novo projeto.
- **Boas Práticas:** Utilize a reordenação por Drag & Drop na sidebar para organizar o documento final antes de salvar.

---

## 🖥️ 2. Visualizador Fóton (GUI Premium)

Interface gráfica em **PyQt6**, projetada para ser o centro de controle do seu fluxo de trabalho documental.

### 2.1 Motor de Renderização Concorrente (`RenderEngine`)

- **Implementação**: Localizada em `src/interfaces/gui/state/render_engine.py`. Utiliza `QThreadPool` com limite de concorrência (2 threads) para evitar que o Windows esgote recursos ao abrir PDFs massivos.
- **Estabilidade**: Cada página é renderizada em uma tarefa isolada. Se uma página estiver corrompida, o visualizador continua operando normalmente para as demais.

### 2.2 Navegação Adaptativa

- **Ajuste de Tela**: Os botões de **Largura** e **Altura** são "conscientes do contexto". Eles identificam qual página está mais visível no topo do viewport e ajustam o zoom baseado nas dimensões reais *daquela página específica*.
- **Suporte Mixed-Size**: Perfeito para documentos que misturam páginas A4 vertical com plantas de engenharia no formato paisagem (A3/A2).

### 2.3 Extração Visual Premium

- **O que faz:** Cria um novo arquivo PDF contendo apenas as páginas que você selecionou visualmente.
- **Processo**:
    1. Selecione as páginas desejadas na sidebar (ordenadas como desejar).
    2. Clique em **Extrair** na Toolbar.
    3. O sistema compila um novo PDF binário unindo as fontes originais e preservando a nova ordem e rotações aplicadas.
- **Uso Comum**: Separar páginas de um contrato ou criar um resumo de um relatório extenso.

---

## 🚀 3. Suíte de Conversão Profissional

Converta o conteúdo estático do PDF em ativos úteis para outros softwares.

### 3.1 Exportação para Imagem (High-DPI)

- **Formatos**: **PNG** (Lossless), **JPG** (Web), **WebP** (Moderno).
- **Qualidade Técnica**: Gera buffers de imagem a **300 DPI** (dots per inch). Diferente de capturas de tela, a exportação utiliza o motor vetorial do PDF para rasterizar o texto com nitidez cirúrgica.
- **Fluxo**: Utiliza o componente `QImage` para garantir compressão otimizada e compatibilidade total com visualizadores de imagem padrão.

### 3.2 Exportação SVG (Vetor Nativo)

- **O que faz**: Converte a geometria da página em XML vetorial.
- **Vantagem**: O arquivo gerado pode ser aberto em ferramentas como **Figma**, **Illustrator** ou browsers, mantendo a capacidade de redimensionamento infinito sem perda de definição.

### 3.3 Exportação Markdown (Text Logic)

- **O que faz**: Extrai a estrutura semântica do documento para um arquivo `.md`.
- **Implementação**: Tenta identificar cabeçalhos, tabelas e parágrafos. Cada página do PDF é separada por um divisor `---` e um título `# Página X`.
- **Ideal para**: Usuários de **Obsidian**, **Logseq** ou **Notion** que precisam processar textos de PDFs de forma rápida e estruturada.

---

## 🖥️ 4. Integração com Sistema Operacional

Conforto e rapidez diretamente da área de trabalho.

### 4.1 Menu de Contexto (Windows)

- **Acesso**: Botão direito no Explorer ▸ `fotonPDF ▸`.
- **Timestamps**: Todas as ações rápidas (Girar, Unir) geram novos arquivos com a marca de tempo no nome (ex: `documento_ROTATE_20260118.pdf`). Isso garante que você nunca perca o arquivo original por um erro de operação.

---

## 🔗 Relacionamentos e Navegação

- [[ARCHITECTURE|🏗️ Arquitetura]]: Saiba mais sobre o motor centralizado.
- [[DASHBOARD|🎛️ Dashboard]]: Status atual de cada funcionalidade.
- [[guides/NEW_OPERATION|➕ Guia de Operações]]: Como estender o sistema com novos conversores.

---
[[MAP|← Voltar ao Mapa]]
