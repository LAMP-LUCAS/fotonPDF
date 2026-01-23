# Relatório de Análise Comparativa: Visão vs. Realidade (Ui/Ux)

Este relatório analisa o estado atual do **fotonPDF** frente às especificações ideais descritas nos documentos de "Ideias" e na "Arquitetura" do repositório. O foco está em identificar o que já foi conquistado e quais são os próximos passos críticos para atingir a excelência em usabilidade e interface.

---

## 📊 Visão Geral: O que já temos vs. O que falta

| Componente | Status Atual | Visão Ideal (Documentação) | Gap / Necessidade |
| :--- | :--- | :--- | :--- |
| **Arquitetura Base** | ✅ Implementada (Hexagonal) | Modular, desacoplada e resiliente. | Nenhuma. A base técnica é sólida. |
| **Navegação Principal** | ✅ Activity Bar + Sidebar | Estilo VS Code/Obsidian. | **Command Palette** (Ctrl+P) ausente. |
| **Visualizador (Engine)** | ⚠️ QScrollArea (Tradicional) | **Infinite Canvas** (QGraphicsView). | Falta a "fluidez" e "física" do zoom/pan. |
| **Organização (Mesa de Luz)** | ⚠️ Thumbnail List Básica | **Light Table** interativa e lúdica. | Melhorar animações de drag-and-drop. |
| **Integração com IA** | ❌ Não detectada na UI | **Composer** e **RAG Local** (Cursor-like). | Implementar Agente IA embutido na UI. |
| **Multitasking** | ✅ Editor Group (Split View) | Visões independentes do mesmo doc. | Funcional, mas pode ser mais "Peek"-like. |

---

## 🛠️ Detalhamento por Componente

### 1. Sistema de Layout e Navegação

- **O que temos:** Uma estrutura visual inspirada em IDEs modernos, com uma `ActivityBar` clara para troca de contexto e uma `SideBar` animada para ferramentas.
- **O que falta para melhorar:**
  - **Paleta de Comandos (Ctrl+P):** A pedra angular da UX de ferramentas modernas. É necessário um diálogo universal para busca de arquivos e execução de comandos por texto.
  - **Aceleração por Teclado:** Implementar atalhos globais que mimetizam o VS Code.

### 2. O Visualizador (O "Core" da Experiência)

- **O que temos:** Um visualizador baseado em `QScrollArea` que renderiza páginas uma após a outra. Funciona bem para leitura linear.
- **O que falta para melhorar:**
  - **Transição para QGraphicsView:** Conforme sugerido nos documentos de ideia, o uso de uma `QGraphicsScene` permitiria o "Mapa de Calor" de busca sobreposto e o zoom infinito centrado no mouse com inércia.
  - **Smooth Zoom:** O zoom atual é discreto; falta a transição contínua que dá a sensação de "tangibilidade digital".

### 3. Organização e Manipulação ("Mesa de Luz")

- **O que temos:** Um `ThumbnailPanel` funcional que permite reordenar páginas via drag-and-drop.
- **O que falta para melhorar:**
  - **Estética Lúdica:** Os cartões de miniaturas podem ser mais "físicos" (sombras, animação de snap ao soltar).
  - **Modo Mesa de Luz:** Uma visão em tela cheia (grid A0/A1) dedicada apenas à organização espacial das páginas, separada da lateral.

### 4. Inteligência Artificial e Conectividade

- **O que temos:** Funcionalidades de OCR e Busca de Texto desacopladas.
- **O que falta para melhorar:**
  - **AI Composer:** Uma interface flutuante (estilo Cursor) que permita ao usuário interagir com o conteúdo selecionado.
  - **Knowledge Graph / Deep Linking:** A capacidade de criar links para coordenadas exatas do PDF que possam ser usados em ferramentas externas (como Obsidian).

---

## 🚀 Recomendações Prioritárias

1. **Implantar a Command Palette (URGENTE):** Centralizar as ações de `Rotate`, `Merge`, `Extract` e busca de páginas em um único local acessível por teclado.
2. **Refatorar Viewer para "Infinite Canvas":** Se o objetivo é o setor AEC (plantas complexas), a performance e fluidez do `QGraphicsView` são diferenciais competitivos fundamentais.
3. **Aprimorar a Micro-interatividade:** Adicionar efeitos de hover e animações de transição mais ricas nos widgets manuais para passar a sensação de um produto "Premium".

---
> [!TIP]
> A base arquitetural em `src/interfaces/gui` é muito limpa e facilita a inserção desses novos componentes. O uso de `ResilientWidget` e `safe_ui_callback` garante que essas novas funcionalidades experimentais não comprometam a estabilidade do sistema.
