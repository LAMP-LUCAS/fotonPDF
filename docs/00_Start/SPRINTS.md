# 🏃 Gerenciamento de Sprints

## 🏁 Sprint Atual: Sprint 23 - Certificação Premium UX 💎 (Concluída)

### Objetivo

Implementar uma suíte de testes de **Usabilidade e Interatividade** que valide os diferenciais "IDE-like" e "AEC-focused" definidos no Roadmap, garantindo que a fluidez prometida no mockup seja uma realidade técnica estável.

### Progresso

- [x] **Testes de Física Interativa (25 testes)**: Drag-and-Drop, RubberBand Selection, Zoom Cirúrgico, Recuperação de Qualidade Pós-Zoom e Navegação por Teclado na `LightTableView` e `InfiniteCanvasView`.
- [x] **Testes de Command Palette (15 testes)**: Estrutura frameless/popup, filtragem case-insensitive, seleção automática, e validação de descoberta de comandos (Girar, Mesclar, Buscar).
- [x] **CI/CD Atualizado**: Inclusão dos passos `tests/gui` e `tests/bdd` no workflow do GitHub Actions.
- [x] **Dependências Corrigidas**: Adição de `psutil`, `requests` e `pydantic` ao `requirements.txt` para compatibilidade com o runner de CI.
- [x] **0 RuntimeError de C++**: Nenhum erro de C++ introduzido pelas simulações de mouse.

### Cenários BDD Validados

#### Manipulação Espacial na Mesa de Luz

- **Cenário:** Reordenação Tangível.
  - **Given:** Um documento de 3 páginas aberto na Mesa de Luz.
  - **When:** O usuário arrasta a Página 3 para a posição entre a 1 e a 2.
  - **Then:** O `PDFDocument` virtual deve atualizar sua lista de índices para `[0, 2, 1]` e a renderização deve refletir a nova ordem visual.

- **Cenário:** Seleção em Lote (RubberBand).
  - **Given:** 10 páginas em grid.
  - **When:** O usuário desenha um retângulo capturando 5 páginas.
  - **Then:** O sinal `selectionChanged` deve reportar exatamente 5 IDs de página e as bordas devem ficar em Ciano Neon (#00E5FF).

#### Precisão de Engenharia no Infinite Canvas

- **Cenário:** Zoom Cirúrgico (Anchor-under-Mouse).
  - **Given:** Uma planta A0 carregada.
  - **When:** O mouse está posicionado na coordenada (500, 500) e o scroll de zoom é disparado.
  - **Then:** O ponto central do viewport deve ser movido proporcionalmente para manter a coordenada (500, 500) sob o cursor.

- **Cenário:** Recuperação de Qualidade Pós-Zoom.
  - **When:** O nível de zoom é alterado para 4.0x.
  - **Then:** Um `QTimer` de 300ms deve ser disparado, seguido por uma nova chamada à `RenderEngine` solicitando pixmaps de alta resolução para as páginas visíveis.

#### Produtividade via Command Palette

- **Cenário:** Execução Operacional sem Mouse.
  - **Given:** Documento aberto e Paleta de Comandos ativa.
  - **When:** Usuário digita "Girar 90" e pressiona `Enter`.
  - **Then:** O comando deve ser roteado para o `RotatePDFUseCase` e a UI deve notificar o sucesso no `BottomPanel`.

### Arquivos Criados/Modificados

| Arquivo | Tipo | Testes |
| ------- | ---- | ------ |
| `tests/gui/test_interactive_physics.py` | GUI Physics | 25 |
| `tests/bdd/test_command_workflow.py` | BDD Workflow | 15 |
| `.github/workflows/ci.yml` | CI Config | — |
| `requirements.txt` | Deps | — |

---

## 📅 Histórico de Sprints Concluídas

### Sprint 22: Consolidação e Lançamento ✅

- [x] **Menu Lúdico v2**: Nova organização categórica com emojis e cores para máxima ergonomia.
- [x] **Reordenação Espacial**: Manipulação de ordem de páginas via "drag-and-drop" na Mesa de Luz com sincronização debounced.
- [x] **Extração Pro**: Ferramenta real de extração de subconjuntos de páginas selecionadas de forma assíncrona.
- [x] **Viewport Dinâmica**: Ajuste automático de dimensões ao girar páginas no editor (fim do bug de viewport fixa).
- [x] **Merge 2.0 incremental**: Correção de redundâncias no carregamento de múltiplos arquivos.
- [x] **Resolução de Identidade Virtual**: Fim da confusão entre índices físicos e visuais em TOC, Busca e Notas.
- [x] **Bug Fix de Anotações**: Sincronização garantida de highlights mesmo após reordenação.
- [x] **Diagnóstico 100+**: Novo arquivo `test_complex.pdf` e otimização para documentos longos.
- [x] **Correção de Visibilidade da Sidebar e Batch Loading** (Fix Crítico).
- [x] **Lógica de Limpeza de Estado UI** (Fix TabContainer / Single-Document V4).
- [x] **Zoom por Área (RubberBand)**: Seleção retangular para zoom preciso.
- [x] **Renderização Assíncrona da Primeira Página**: Carregamento instantâneo.
- [x] **Testes E2E e Robustez para Navegação**.
- [x] **Build com PyInstaller**: Empacotamento `onedir` funcional.
- [x] **Estabilidade 100% e Merge para `develop`**.

### Fase 3.5: Navegação Premium e UX Avançada

#### Sprint 21: Navegação Universal Premium ✅

- [x] **ModernNavBar**: Barra flutuante com transparência dinâmica (30%/90%) e submenus colapsáveis.
- [x] **NavHub**: Widget de controle circular para troca rápida de ferramentas.
- [x] **Atalhos Okular**: Integração completa com `+`, `-`, `0`, `Backspace`, `Space`, `N`.
- [x] **Zoom Focado no Mouse**: Ponto sob o cursor permanece fixo durante zoom (Scroll e Mesa).
- [x] **Mesa de Luz Hi-Res**: Renderização dinâmica de alta qualidade ao aproximar o zoom.
- [x] **Suporte A0/A1**: Dimensões fixas e Tiling Inteligente para grandes formatos.
- [x] **Correções de Estabilidade**: Fim do "pulo" de layout e restauração de movimentação de páginas.

### Fase 3: Ecossistema & Inteligência AEC

#### Sprint 18: Gestão do Aplicativo & Control Center ✅

- [x] **Control Center**: Hub centralizado para telemetria, configurações e atualizações.
- [x] **Real-time Health**: Monitoramento de CPU/RAM via `psutil` integrado à UI.
- [x] **Lifecycle Hub**: Gestão visual de atualizações via GitHub release.

#### Sprint 17: Inteligência AEC (Multi-Provider) ✅

- [x] **Multi-Provider Brain**: Integração universal via `LiteLLM` (Ollama, OpenAI, Gemini).
- [x] **Smart Shell**: Tradução de linguagem natural para comandos estruturados via `Instructor`.
- [x] **AI Settings**: Painel de gestão de modelos e chaves de API.

#### Sprint 16: UI Refactor: Geometria & Camadas ✅

- [x] **AEC Inspector**: Sidebar direita para identificação de formatos (A0-A4) e metadados.
- [x] **Layer Control**: Manipulação direta de camadas OCG (elétrica, hidráulica, etc).
- [x] **Metric Telemetry**: Exibição de coordenadas e dimensões em milímetros (mm).
- [x] **Stage Persistence**: Salvamento automático de layouts na Mesa de Luz em SQLite.

#### Sprint 15: UI Refactor: Layout & Branding ✅

- [x] **TopBar Modular**: Barra superior centralizada e desacoplada da MainWindow.
- [x] **Visual Identity**: Injeção da paleta Solar Gold e Logo oficial.
- [x] **Resilient UI**: Panels (Thumbnail, TOC) refatorados com placeholders e handlers de erro.
- [x] **Smart Shell**: Conexão do CommandOrchestrator à barra de busca global.

#### Sprint 14: Geometria Física & Paridade AEC ✅

#### Sprint 13: UI Test Hardening (Pytest-Qt) ✅

- [x] **Configuração Pytest-Qt**: Ambiente de testes automatizados para PyQt6.
- [x] **Smoke Tests de UI**: Validação de abertura de janelas e carregamento de widgets.
- [x] **Headless CI**: Preparação para execução de testes no pipeline do GitHub.

#### Sprint 12: Resiliência & Tolerância a Falhas ✅

- [x] **UI Error Boundaries**: Implementação do decorador `@safe_ui_callback` para isolamento de falhas.
- [x] **Global Exception Hook**: Captura de exceções não tratadas no nível da aplicação (PyQt).
- [x] **Hardenização de Widgets**: Estados de falha resilientes para `EditorGroup` e `SideBar`.
- [x] **Logs Inteligentes**: Suporte a cores (Red/Yellow) no Painel Inferior para sinalização de erros.

#### Sprint 11: Ultimate VS Code Experience (Tabs & Panels) ✅

- [x] **Multi-Document Tabs**: Sistema de abas profissional para múltiplos arquivos simultâneos.
- [x] **Async Dual-Split**: Visualização independente de duas partes do mesmo documento.
- [x] **Auxiliary Panels**: Inclusão de Painel Inferior (Logs) e Barra Lateral Direita (AI Placeholder).
- [x] **Layout Modular**: Orquestração via sinais para desacoplar componentes da UI.

#### Sprint 10: Dev Experience & UI Controls ✅

- [x] **Hot Reload (Dev Mode)**: Lançador automático que reinicia o app ao detectar mudanças no código.
- [x] **Layout Toggles**: Botões na StatusBar para ocultar/exibir barras laterais e atividade.
- [x] **Split Toggle**: Controle direto na Floating NavBar para ativar visualização lado-a-lado.

#### Sprint 9: Ultra-Clean UI/UX Overhaul ✅

- [x] **VS Code Layout**: Estrutura base com Activity Bar, Side Bar e main area modular.
- [x] **Floating NavBar**: Barra flutuante transparente com controles essenciais de navegação.
- [x] **Search Visualization**: Marcadores estilo IDE na scrollbar e "peek" highlight temporário.
- [x] **Context Menu**: Menu popup ao selecionar texto para cópia e busca rápida.

#### Sprint 8: UI Evolution & Modo Profissional ✅

- [x] **Settings Service**: Persistência de zoom, tema e último arquivo aberto.
- [x] **Modos de Leitura**: Filtros de cor (Sépia, Noturno, Invertido) para conforto visual.
- [x] **Dual-View**: Layout lado-a-lado para comparação e leitura densa.
- [x] **Anotações Básicas**: Ferramenta de realce (Highlight) persistente.
- [x] **Premium UI**: Micro-animações e refinamento estético (Glow effect e Tabs).

#### Sprint 7: OCR & Camada de Texto ✅

- [x] **Detecção de Camada**: Identificação inteligente de PDFs baseados em imagem.
- [x] **Injeção de OCR**: Geração de PDFs pesquisáveis usando Tesseract.
- [x] **Extração de Área**: Ferramenta interativa para OCR on-demand (Copiado para Clipboard).
- [x] **Banner de Sugestão**: UI proativa sugerindo OCR quando necessário.

#### Sprint 6: Inteligência de Busca & Navegação ✅

- [x] **Engine de Busca:** Motor indexado PyMuPDF para localização instantânea.
- [x] **UI de Busca:** Painel lateral com snippets e navegação por clique.
- [x] **Highlights Visuais:** Destaque automático de termos encontrados no viewer.
- [x] **Sumário (Bookmarks):** Árvore hierárquica completa para navegação rápida.
- [x] **Histórico "Back/Forward":** Navegação intuitiva entre saltos de página.
- [x] **Shortcuts:** `Ctrl+F` integrado para acesso rápido à busca.

#### Sprint 6: Evolução UI & Conversão (Premium) ✅

- [x] **Nova Toolbar**: Organizada por categorias: Navegação, Edição e Conversão.
- [x] **Navegação Inteligente**: "Ajustar Largura" agora foca na página atual visível.
- [x] **Suíte de Conversão**: Exportação direta para PNG, JPG, WebP, SVG e Markdown.
- [x] **Ux Tooling**: Adição de botões "Salvar" e "Salvar Como".
- [x] **Paridade CLI/GUI**: Conversão disponível via CLI e Menu de Contexto.
- [x] **Refatoração Hexagonal**: Lógica de exportação movida para Use Cases.

#### Sprint de Estabilização Crítica (Hotfix) ✅

- [x] **Refatoração Thread-Safe**: Implementação do `RenderEngine` centralizado com `QThreadPool`.
- [x] **Gestão de Recursos**: Fila de renderização limitada (max 2 threads) para evitar crashes por exaustão de handles.
- [x] **Correção de UI**: Miniaturas com fundo branco (RGB) e sincronização de layout via `QTimer`.

### Fase 1: Fundação & MVP

#### Sprint 5: Distribuição 2.0 & Inteligência de Onboarding ✅

- [x] **Auto-Update Engine**: Notificação inteligente de nova versão via API do GitHub.
- [x] **Intelligent Bootstrap**: Mecanismo de reparo automático do Registro do Windows (Opção `R`).
- [x] **Code Signing Infra**: Script de assinatura (Self-signed) para integridade de binários.
- [x] **Instalador Zero-Click**: Inno Setup otimizado para instalação por usuário e sem interrupções.
- [x] **Registro Contextual**: Integração robusta via `SystemFileAssociations`.

#### Sprint 4: Lógica de Interface & UX Premium ✅

- [x] Barra de ferramentas com Extração e Exportação.
- [x] Design Premium e Feedbacks em tempo real.

#### Sprint 3: Visualizador & Renderização ✅

- [x] Interface Gráfica base e Lazy Loading.
- [x] Navegação por Miniaturas.

#### Sprint 2: OS Integration & Multi-file Ops ✅

- [x] Merge/Split no motor e Menu de Contexto.

#### Sprint 1: Core Engine & CLI Basics ✅

- [x] Fundação Hexagonal e PyMuPDF Adapter.

#### Sprint 0: Kickoff ✅

- [x] Estratégia de documentação e arquitetura.

---

[[MAP|Voltar ao Mapa]] | [[ROADMAP|Voltar ao Roadmap (Fases)]]
