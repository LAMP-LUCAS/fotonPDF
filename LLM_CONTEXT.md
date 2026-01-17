# 🧠 Contexto para CodeAssistants (LLM)

Este arquivo serve como a "Memória de Longo Prazo" para qualquer IA assistente que trabalhe neste projeto.

## 📌 Visão Geral

- **Nome:** fotonPDF
- **Paradigma:** Arquitetura Hexagonal Simplificada + Monólito Modular.
- **Objetivo:** Velocidade máxima em operações de PDF via menu de contexto.

## 🏗️ Padrões Arquiteturais (Regras Inegociáveis)

1. **Inversão de Dependência:** A camada de `domain` e `application` nunca importa nada de `infrastructure` ou `interfaces`.
2. **Ports & Adapters:** Bibliotecas externas (PyMuPDF, Registry API) devem ser encapsuladas em adaptadores que implementam protocolos definidos no domínio.
3. **Imutabilidade:** Operações em PDFs devem, por padrão, gerar novos arquivos ou cópias temporárias antes de sobrescrever, garantindo segurança de dados.
4. **I/O Assíncrono:** Todas as operações de processamento de PDF devem ser executadas em threads separadas para não bloquear a UI.
5. **Filosofia Senior (Obrigatório):**
   - **DRY (Don't Repeat Yourself):** Reutilize código, centralize lógicas comuns nos domínios.
   - **CLEAN Code:** Código legível, nomes auto-explicativos e funções com responsabilidade única.
   - **SOLID:** Princípios de design para garantir escalabilidade e facilitar manutenção.
   - **Centros de Verdade:** Centralize definições e lógicas críticas em locais únicos e bem definidos no `domain`. Evite dispersão de lógica de negócio para garantir estabilidade, confiabilidade e facilidade de documentação.

## 📝 Documentação e Rastreamento (Crucial)

Para a saúde do projeto, é obrigatório registrar:

- **O que foi desenvolvido:** Novas funcionalidades e lógica implementada.
- **O que foi concluído:** Itens do ROADMAP e DASHBOARD atingidos.
- **O que foi corrigido/excluído:** Explicação clara de bugs resolvidos ou códigos legados removidos, e o porquê.

## 📓 Padrão de Commits (Obrigatório)

Sempre que gerar um commit, siga este template rigorosamente:

1. **Idioma:** Português Brasileiro (pt-BR).
2. **Base:** Analise o output de `git status` e `git diff`.
3. **Detalhamento:** Liste as alterações relevantes.
4. **Sincronização de Docs:** Sempre após o commit de desenvolvimento do código, realize uma verificação da documentação para registrar, compatibilizar e documentar o avanço do trabalho (ROADMAP, SPRINTS, DASHBOARD).

**Formato:**

```text
<tipo>: <descrição curta e objetiva>

<descrição detalhada das mudanças>

Arquivos alterados:
- <arquivo>: <motivo da mudança>
```

## 💻 Tech Stack & Convenções

- **Python:** 3.11+
- **Bibliotecas PDF:** Priorizar `PyMuPDF` (fitz) para performance; `pypdf` para metadados simples.
- **Interface:** `PyQt6` para janelas e `QML` para o visualizador rápido.
- **Paths:** Usar SEMPRE `pathlib.Path` em vez de manipulação de strings.
- **Tipagem:** Python Type Hints são OBRIGATÓRIOS em todas as funções públicas.
- **Logs:** Usar o módulo `logging` estruturado (JSON format).

## 📂 Estrutura de Diretórios

- `src/domain`: Entidades puras e protocolos (Portas).
- `src/application`: Casos de uso e orquestração.
- `src/infrastructure`: Implementações concretas (Adapters, Sistema de Arquivos).
- `src/interfaces`: UI, CLI e integração com Menu de Contexto.

## 🔗 Links Relacionados

- [[docs/ARCHITECTURE|Detalhes da Arquitetura]]
- [[docs/DEVELOPMENT|Padrões de Código]]
- [[README|Voltar para Início]]
