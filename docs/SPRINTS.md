# 🏃 Gerenciamento de Sprints

Este documento detalha o **micro-gerenciamento** da Fase 1, com o que deve ser desenvolvido em cada intervalo de tempo menor (Sprint).

## 🏁 Sprint Atual: Fase 2 - Interface & Funcionalidade 🚀

**Objetivo:** Evoluir para uma interface gráfica robusta e adicionar inteligência ao processamento.

---

## 📅 Histórico de Sprints

### Sprint 5: Distribuição & Sistema de Atualização ✅

**Objetivo:** Gerar o entregável final (MVP) e garantir que ele seja autossustentável.

- [x] **Geração do Binário (foton.exe):** Configurado `PyInstaller` para empacotamento completo.
- [x] **Scripts de Instalação Final:** Registro inteligente no Menu de Contexto (Portable/Binary).
- [x] **Sistema de Auto-Update:** Implementado `UpdateService` com GitHub API e notificações.
- [x] **Manual do Usuário:** Documentação básica de instalação incluída no README.

### Sprint 4: Lógica de Interface & UX Premium ✅

**Objetivo:** Integrar as capacidades do motor à GUI e elevar a estética do produto.

- [x] Extração de Páginas (GUI): Seleção múltipla e integração com `SplitPDFUseCase`.
- [x] Conversores (Exportação): Renderização e salvamento em PNG/JPG.
- [x] Design Premium: Tema dark, barra de ferramentas e CSS moderno.
- [x] Interatividade: Atalhos senior e feedback visual na barra de status.

### Sprint 3: Visualizador & Renderização ✅

**Objetivo:** Iniciar a interface gráfica (GUI) minimalista focada em velocidade extrema.

- [x] Interface Gráfica (GUI) em PyQt6 e estrutura `interfaces/gui`.
- [x] Visualizador com Lazy Loading e Renderização Assíncrona.
- [x] Navegação por Miniaturas (Thumbnails) e Integração CLI.
- [x] Atalhos de teclado senior e suporte a Drag & Drop.

### Sprint 2: OS Integration & Multi-file Ops ✅

**Objetivo:** Integração com sistema para uso prático e expansão do motor.

- [x] Implementação de `MergePDFUseCase` e `SplitPDFUseCase`.
- [x] Integração com Registro do Windows (Menu de Contexto).
- [x] Sistema de Notificações Nativas (Plyer).
- [x] Refatoração CLI para múltiplas operações e arquivos.

### Sprint 1: Core Engine & CLI Basics ✅

**Objetivo:** Configurar o ambiente de desenvolvimento e implementar Rotação básica.

- [x] Setup do motor PyMuPDF e estrutura de diretórios seguindo Hexagonal.
- [x] Implementação do `Domain` e `Application` (RotateUseCase).
- [x] Implementação de Adapter para PyMuPDF.
- [x] CLI simples para invocar a rotação.

### Sprint 0: Kickoff ✅

- [x] README, Arquitetura e Estrutura de Pastas.
- [x] Contexto para CodeAssistants (LLM_CONTEXT.md).

---

[[MAP|Voltar ao Mapa]] | [[ROADMAP|Voltar ao Roadmap (Fases)]]
