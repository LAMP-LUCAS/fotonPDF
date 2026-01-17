# 🏃 Gerenciamento de Sprints

Este documento detalha o **micro-gerenciamento** da Fase 1, com o que deve ser desenvolvido em cada intervalo de tempo menor (Sprint).

## 🏁 Sprint Atual: Sprint 4 - Lógica de Interface & UX Premium 🟡

**Objetivo:** Integrar as capacidades do motor à GUI e elevar a estética do produto.

### Backlog da Sprint

- **🛠️ Lógica de Interface (Ponte GUI-Motor):**
  - [ ] **Extração de Páginas (GUI):** Integrar o `SplitPDFUseCase` à interface, permitindo selecionar páginas visualmente via miniaturas e salvar como novo arquivo.
  - [ ] **Conversores (Exportação):** Implementar funcionalidade de "Exportar como Imagem" (PNG/JPG) diretamente no visualizador.
- **💎 UX e Refino Estético:**
  - [ ] **Design Premium:** Aplicar paleta de cores vibrantes, ícones consistentes e layout adaptativo/moderno.
  - [ ] **Interatividade Senior:** Refinar atalhos de teclado e feedbacks visuais durante o processamento.

---

## 🔜 Próximas Sprints

### Sprint 5: Distribuição & Sistema de Atualização ✅

**Objetivo:** Gerar o entregável final (MVP) e garantir que ele seja autossustentável.

- **📦 Distribuição (O Entregável MVP):**
  - [ ] **Geração do Binário (foton.exe):** Configurar `PyInstaller` para empacotar Python, PyQt6 e PyMuPDF em um único executável.
  - [ ] **Scripts de Instalação Final:** Integrar o registro no Menu de Contexto do Windows diretamente no binário para setup automático.
- **🔄 Ciclo de Vida do Produto:**
  - [ ] **Sistema de Auto-Update:** Implementar verificador de versão e notificação/download automático para novas versões.
- **📘 Documentação de Saída:**
  - [ ] **Manual do Usuário:** Documentar instalação e operação (Explorer e Visualizador) para o usuário final.

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
