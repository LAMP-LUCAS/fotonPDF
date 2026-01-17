# 🏃 Gerenciamento de Sprints

Este documento detalha o **micro-gerenciamento** da Fase 1, com o que deve ser desenvolvido em cada intervalo de tempo menor (Sprint).

## 🏁 Sprint Atual: Sprint 1 - Core Engine & CLI Basics ✅

**Objetivo:** Configurar o ambiente de desenvolvimento, estrutura `src/` e implementar Rotação básica.

### Backlog da Sprint

- [x] Setup do motor PyMuPDF e estrutura de diretórios seguindo Hexagonal.
- [x] Implementação do `Domain` (Entidades/Portas) e `Application` (RotateUseCase).
- [x] Implementação de Adapter para PyMuPDF.
- [x] CLI simples para invocar a rotação.
- [x] Testes unitários e de integração básicos.

---

## 🔜 Próximas Sprints

### Sprint 2: OS Integration & Multi-file Ops

- **Objetivo:** Integração com sistema para uso prático.
- Integração com Registro do Windows (Girar 90/180).
- Casos de uso de Juntar (Merge) e Separar (Split) PDFs.
- Suporte a múltiplos arquivos selecionados no Explorer.

### Sprint 3: Visualizador & Renderização

- **Objetivo:** Iniciar a GUI de visualização.
- Protótipo do `Visualizador Fóton` em PyQt6.
- Otimização para abertura instantânea (< 1s).
- Renderização de páginas sob demanda (Lazy Loading).

### Sprint 4: MVP Polish & Conversores

- **Objetivo:** Refinar para entrega final do MVP.
- Extração de páginas específicas.
- Conversores PDF ↔ Imagem integrados.
- Scripts de instalação e finalização de binários.

---

## 📅 Histórico de Sprints

### Sprint 0: Kickoff ✅

**Objetivo:** Formalizar documentação.

- [x] README, Arquitetura e Estrutura de Pastas.
- [x] Contexto para CodeAssistants (LLM_CONTEXT.md).
- [x] Definição clara de Fases vs Sprints.

---

[[MAP|Voltar ao Mapa]] | [[ROADMAP|Voltar ao Roadmap (Fases)]]
