# 🛠️ Guia de Desenvolvimento

Bem-vindo ao desenvolvimento do **fotonPDF**. Este documento define os padrões para manter o código limpo, testável e manutenível.

## ⚙️ Setup do Ambiente

1. **Python:** 3.11 ou superior.
2. **VirtualEnv:**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Instalação:**

   ```bash
   pip install -r requirements.txt
   pip install -e .  # Instala no modo editável
   ```

## 📏 Padrões de Código

- **Formatter:** Black
- **Linter:** Flake8 / MyPy (para tipos)
- **Imports:** Organizados por `isort`.
- **Naming:**
  - Classes: `PascalCase`
  - Funções/Variáveis: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`

## 🧪 Estratégia de Testes

- **Unitários:** Focados no `src/domain` e `src/application`. Devem ser rápidos e sem I/O pesado.
- **Integração:** Testam os `Adapters` contra arquivos PDF reais em `tests/test_data`.
- **E2E:** Testam a integração com o explorador de arquivos (simulação de registro/desktop entries).

Executar testes:

```bash
pytest
```

## 🔄 Workflow de Git

- Usar **Conventional Commits**:
  - `feat:` para novas funcionalidades.
  - `fix:` para correção de bugs.
  - `docs:` para alterações na documentação.
  - `refactor:` para melhorias de código sem mudança de comportamento.

## 🔗 Referências

- [[ARCHITECTURE|Entenda a estrutura de pastas]]
- [[../LLM_CONTEXT|Instruções para seu CodeAssistant]]
- [[MAP|Voltar ao Mapa]]
