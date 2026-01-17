# 🏃 Gerenciamento de Sprints

Este documento detalha o **micro-gerenciamento** da Fase 1, com o que deve ser desenvolvido em cada intervalo de tempo menor (Sprint).

## 🏁 Sprint Atual: Sprint 4 - MVP Polish & Conversores 🟡

**Objetivo:** Refinar a experiência do usuário e implementar as últimas funcionalidades do MVP.

### Backlog da Sprint

- [ ] Extração de páginas específicas via GUI (Integração com SplitUseCase).
- [ ] Conversores PDF ↔ Imagem integrados (Exportar páginas).
- [ ] Scripts de instalação e finalização de binários (PyInstaller).
- [ ] Refinar UI (Layout adaptativo e ícones premium).
- [ ] Documentação de usuário final (Manual rápido).

---

## 📅 Histórico de Sprints

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
- [x] Implementação de testes unitários e integração para novas operações.

### Sprint 1: Core Engine & CLI Basics ✅

**Objetivo:** Configurar o ambiente de desenvolvimento e implementar Rotação básica.

- [x] Setup do motor PyMuPDF e estrutura de diretórios seguindo Hexagonal.
- [x] Implementação do `Domain` e `Application` (RotateUseCase).
- [x] Implementação de Adapter para PyMuPDF.
- [x] CLI simples para invocar a rotação.
- [x] Testes unitários e de integração básicos.

### Sprint 0: Kickoff ✅

- [x] README, Arquitetura e Estrutura de Pastas.
- [x] Contexto para CodeAssistants (LLM_CONTEXT.md).

---

[[MAP|Voltar ao Mapa]] | [[ROADMAP|Voltar ao Roadmap (Fases)]]
