# 🏃 Gerenciamento de Sprints

Este documento detalha o **micro-gerenciamento** das fases, com o que deve ser desenvolvido em cada intervalo de tempo menor (Sprint).

## 🏁 Sprint Atual: Sprint 6 - Inteligência de Busca & Navegação �

**Objetivo:** Adicionar capacidade de busca textual instantânea e melhorar a navegação interna nos documentos.

### Backlog da Sprint

- **🔍 Busca Inteligente:**
  - [ ] **Engine de Busca:** Implementar buscador indexado (PyMuPDF) para localização ultra-rápida de termos.
  - [ ] **Interface de Busca:** Adicionar barra de busca (`Ctrl+F`) com destaque (highlight) visual nos termos encontrados.
  - [ ] **Painel de Resultados:** Lista lateral com snippets de texto e navegação rápida para a página/posição.
- **📍 Navegação Avançada:**
  - [ ] **Suporte a Sumário (Bookmarks):** Renderização da árvore de conteúdos do PDF na sidebar.
  - [ ] **Histórico de Navegação:** Botões "Voltar" e "Avançar" para saltos entre páginas e links internos.

---

## 🔜 Próximas Sprints

### Sprint 7: OCR & Camada de Texto (A Visão Fóton) 🏗️

- **Objetivo:** Dar inteligência a documentos baseados em imagens.
- [ ] **Integração OCR:** Adicionar motor OCR (Tesseract ou similar) como plugin/dependência.
- [ ] **Reconhecimento Automático:** Detectar PDFs sem camada de texto e sugerir OCR.
- [ ] **Camada de Texto Invisível:** Gerar e injetar texto pesquisável sobre PDFs escaneados.
- [ ] **Extração Inteligente:** Copiar texto de áreas selecionadas, mesmo em imagens (OCR on-demand).

### Sprint 8: UI Evolution & Modo Profissional 💎

- **Objetivo:** Refinar a interface para produtividade de alto nível.
- [ ] **Dual/Multi-View:** Visualização de duas páginas lado a lado ou documentos diferentes.
- [ ] **Modo Madrugada/Leitura:** Filtros de cor customizados para redução de fadiga ocular.
- [ ] **Annotations Basics:** Implementar realce (highlight) e sublinhado persistente.
- [ ] **Configurações Globais:** Persistência de zoom, última página lida e preferências de tema.

---

## 📅 Histórico de Sprints Concluídas

### Fase 2: Interface & Funcionalidade

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
