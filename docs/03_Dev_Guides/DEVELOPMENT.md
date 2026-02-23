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

Executar testes (garantindo que o código em `src` seja encontrado):

```bash
$env:PYTHONPATH = ".;src"
pytest
```

> [!TIP]
> O projeto utiliza o arquivo `tests/conftest.py` como **Fábrica Central de Mocks**. Fixtures para `pdf_document`, `mock_settings` e `mock_ai_provider` devem ser reutilizadas em vez de redeclaradas.

## 🔄 Workflow de Git

- Usar **Conventional Commits**:
  - `feat:` para novas funcionalidades.
  - `fix:` para correção de bugs.
  - `docs:` para alterações na documentação.
  - `refactor:` para melhorias de código sem mudança de comportamento.

## 🛠️ Ferramentas de Desenvolvimento (`/scripts`)

O fotonPDF possui uma suíte de scripts para acelerar o desenvolvimento e garantir a qualidade visual.

### 1. Hot-Reload Centralizado

A ferramenta principal de desenvolvimento é o `hot_reload.py`. Ela permite visualizar mudanças em tempo real sem reiniciar o processo manualmente.

**Como usar:**

```bash
# Modo Design (Mockup com dados fakes) - Recomendado para UI/UX
python scripts/hot_reload.py --mode mock

# Modo App (Aplicação real com lógica completa)
python scripts/hot_reload.py --mode app
```

- **Início Imediato:** A interface abre logo que o comando é executado.
- **Monitoramento:** Reinicia automaticamente ao detectar mudanças em `.py`, `.qss` ou `.json`.
- **Exclusões:** Ignora pastas de cache e metadados (`docs/`, `.git/`, `build/`, etc.) para evitar loops.

### 2. Visão de Mockup e Dados Fake

- **`scripts/dev_gui_view.py`**: Ponto de entrada para a interface de design.
- **`scripts/dev_mocks.py`**: Centraliza os dados de teste (TOC, resultados de busca, etc.), garantindo que os mocks sejam consistentes.

### 3. Build e Distribuição

- **`build_exe.py`**: Gera o executável via PyInstaller.
- **`sign_exe.py`**: Aplica assinaturas digitais (essencial para integridade no Windows).
- **`generate_icons.py`**: Atualiza o `.ico` a partir do `.svg` da marca.

### 4. Captura de Mockup UI

O script `capture_concept.py` automatiza a geração de referências visuais a partir do design conceitual em HTML.

**Como usar:**

```bash
python scripts/capture_concept.py
```

- **Resultado:** Salva uma imagem em `docs/visuals/captures/concept_mockup.png`.
- **Dependência:** Utiliza a biblioteca `playwright`. Se não estiver instalada, o script tentará instalá-la automaticamente.

## 🎨 Análise Visual (GUI)

Para garantir a qualidade da interface e evitar regressões visuais:

1. **Snapshots Automáticos:** Ao rodar no modo de desenvolvimento (`--mode mock`), o sistema captura snapshots da UI em `docs/visuals/captures`.
2. **Registro de Evolução:** Compare os novos snapshots para validar mudanças de layout.

## ⚡ Benchmarks de Performance

Para garantir que o sistema mantenha o padrão de "Toolkit de PDFs mais rápido do mundo", existe um script de benchmark automatizado:

```bash
python scripts/performance_benchmark.py
```

- **Métricas:** Mede tempo de inicialização (Cold Start), consumo de RAM/CPU e velocidade de renderização de PDFs.
- **Auditoria:** Os resultados são salvos automaticamente em `logs/performance_report.txt`.
- **Meta:** O tempo total de inicialização e abertura de documentos deve ser mantido abaixo de **1 segundo**.

## 🔗 Referências

- [[ARCHITECTURE|Entenda a estrutura de pastas]]
- [[../LLM_CONTEXT|Instruções para seu CodeAssistant]]
- [[MAP|Voltar ao Mapa]]

---
[[MAP|← Voltar ao Mapa]]
