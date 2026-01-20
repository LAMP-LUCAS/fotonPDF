# 🏃 Gerenciamento de Sprints

Este documento detalha o **micro-gerenciamento** das fases, com o que deve ser desenvolvido em cada intervalo de tempo menor (Sprint).

## 🏁 Sprint Atual: Sprint 8 - UI Evolution & Modo Profissional 🏗️

**Objetivo:** Refinar a interface para produtividade de alto nível.

- **Dual/Multi-View:** Visualização de duas páginas lado a lado ou documentos diferentes.
- **Modo Madrugada/Leitura:** Filtros de cor customizados para redução de fadiga ocular.
- **Annotations Basics:** Implementar realce (highlight) e sublinhado persistente.
- **Configurações Globais:** Persistência de zoom, última página lida e preferências de tema.

---

## 🔜 Próximas Sprints

### Sprint 9: Ecossistema & Plugins 🔋

- **Objetivo:** Tornar o fotonPDF extensível.

---

## 📅 Histórico de Sprints Concluídas

### Fase 2: Interface & Funcionalidade

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
