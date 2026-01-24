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

## 📏 Padrões de Código & Filosofia

- **Filosofia Senior:** Todo código deve buscar ser **CLEAN**, **DRY** e seguir os princípios **SOLID**.
- **Centros de Verdade:** Desenvolvedores devem identificar e criar centros de verdade para lógicas compartilhadas. Isso reduz a redundância, fortalece as bases do sistema e garante que o código seja estável e confiável tanto na execução quanto na documentação.
- **Naming:**
  - Classes: `PascalCase`
  - Funções/Variáveis: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`
- **Documentação de Evolução:**
  - É mandatório documentar o que está sendo desenvolvido, o que foi concluído e, principalmente, **o que foi corrigido ou excluído** (com a justificativa técnica). Isso é vital para a saúde e histórico do projeto.

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

## 🎨 Análise Visual (GUI)

Para garantir a qualidade da interface e evitar regressões visuais:

1. **Snapshots Automáticos:** Ao rodar o `development_view.py`, o sistema captura automaticamente o estado inicial da UI em `docs/visuals/captures`.
2. **Registro de Evolução:** Sempre compare os novos snapshots com os anteriores para validar mudanças de layout e estilo.
3. **Padrão de Nomenclatura:** Os arquivos são salvos como `{nome}_{timestamp}.png`.

## 🔗 Referências

- [[ARCHITECTURE|Entenda a estrutura de pastas]]
- [[../LLM_CONTEXT|Instruções para seu CodeAssistant]]
- [[MAP|Voltar ao Mapa]]

---
[[MAP|← Voltar ao Mapa]]
