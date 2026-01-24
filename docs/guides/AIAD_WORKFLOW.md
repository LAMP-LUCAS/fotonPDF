# 🧠 Guia: foton-AIAD (AI-Augmented Design)

Este documento define o framework oficial para o desenvolvimento de interface e experiência do usuário (UI/UX) assistido por IA no projeto **fotonPDF**.

---

## 🏗️ 1. Centros de Verdade (SSOT)

O sucesso da colaboração com assistentes de IA depende da existência de "Centros de Verdade" claros:

* **Design Tokens (`src/interfaces/gui/styles.py`):** Centraliza cores, fontes e espaçamentos. A IA deve consultar este arquivo para manter a consistência com o tema **AEC-Dark**.
* **Mocks de Dados (`scripts/dev_mocks.py`):** Centraliza dados de teste. A IA deve utilizar estes mocks para testar componentes isoladamente antes da integração.
* **Contexto de Longo Prazo (`LLM_CONTEXT.md`):** O "cérebro" do projeto para IAs.

---

## 📸 2. O Loop de Visão Analítica

Para alinhar a implementação real com a visão de design, seguimos este ciclo:

1. **Geração de Snapshot:** Utilize `scripts/hot_reload.py --mode mock` para capturar o estado atual da UI.
2. **Análise Comparativa:** Forneça o arquivo `docs/visuals/concept.html` e a última captura de tela para a IA.
3. **Refinamento Cirúrgico:** A IA propõe mudanças específicas em `styles.py` ou nos widgets para corrigir discrepâncias visuais (padding, alignment, contrast).

---

## 🔄 3. Pipeline de Exposição de Features

Toda nova funcionalidade deve ser exposta seguindo esta hierarquia:

1. **Ação (Command Pattern):** Criar a lógica no `CommandOrchestrator`.
2. **Acesso Universal:** Registrar o comando na `CommandPalette`.
3. **Porta de IA (IntelligenceCore):** Criar uma interface que permita que a IA execute a ação através de processamento de linguagem natural ou triggers de UX.
4. **Feedback Visual:** Registrar o sucesso/erro no `BottomPanel` (Information Bar).

---

## 🛠️ 4. Protocolo de Comunicação Assistant-Developer

Para minimizar fricção:

* **Walkthroughs em tempo real:** A cada ciclo de UI, a IA deve gerar/atualizar um `walkthrough.md` descrevendo o que mudou visualmente.
* **Git Atomic Commits:** Commits detalhados em `pt-BR` seguindo as regras do `LLM_CONTEXT.md`.
* **Validation First:** Use o Hot-Reload para validar cada mudança antes de declarar a tarefa como concluída.

---

## 🚀 Próximos Passos (Evolução do Framework)

* [ ] Implementar análise automatizada de contraste via script.
* [ ] Criar template de `UX_MANIFEST.md` para novas áreas da aplicação.
* [ ] Integrar logs de interação real no `dev_mocks.py` para simular cenários de usuário.

---
[[../MAP|← Voltar ao Mapa]]
