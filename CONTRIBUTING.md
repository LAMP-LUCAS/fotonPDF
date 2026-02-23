# 🤝 Guia de Contribuição

Obrigado por considerar contribuir com o **fotonPDF**! Este documento orienta como participar do desenvolvimento.

## 🌟 Formas de Contribuir

- 🐛 **Reportar Bugs:** Abra uma issue descrevendo o problema.
- 💡 **Sugerir Features:** Discuta ideias na seção de Discussions.
- 📝 **Melhorar Documentação:** PRs de docs são sempre bem-vindos!
- 🔧 **Corrigir Código:** Escolha uma issue com label `good-first-issue`.
- 🌍 **Traduzir:** Adicione suporte a novos idiomas.

## 🚀 Primeiros Passos

### 1. Fork e Clone

```bash
git clone https://github.com/SEU_USER/fotonPDF.git
cd fotonPDF
```

### 2. Configurar Ambiente

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
pip install -r requirements-dev.txt  # Ferramentas de desenvolvimento
```

### 3. Criar Branch

Use nomes descritivos:

```bash
git checkout -b feat/add-compression
git checkout -b fix/rotation-bug
git checkout -b docs/update-readme
```

### 4. Fazer Alterações

Siga os padrões do projeto ([[docs/DEVELOPMENT|Guia de Desenvolvimento]]).

### 5. Testar

```bash
pytest                        # Todos os testes
# Recomendado (com PYTHONPATH):
# $env:PYTHONPATH = ".;src"; pytest

pytest tests/unit            # Apenas unitários
pytest --cov=src             # Com cobertura
```

### 6. Commit

Use **Conventional Commits**:

```bash
git commit -m "feat: adiciona compressão de PDF"
git commit -m "fix: corrige rotação de páginas em lote"
git commit -m "docs: atualiza guia de plugins"
```

### 7. Pull Request

- Certifique-se de que todos os testes passam.
- Descreva claramente o que foi alterado.
- Referencie issues relacionadas (`Closes #123`).

## 📏 Padrões de Código

### Python

- **Formatação:** Black (line-length=100)
- **Linting:** Flake8
- **Type Hints:** Obrigatórios em funções públicas
- **Docstrings:** Google style

Verificar antes de commitar:

```bash
black src/
isort src/
flake8 src/
mypy src/
```

### Estrutura de Commits

```text
tipo(escopo): descrição curta

Descrição detalhada do que foi feito e por quê.

Closes #123
```

**Tipos válidos:**

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `refactor`: Refatoração sem mudança de comportamento
- `test`: Adição/modificação de testes
- `chore`: Tarefas de manutenção

## 🧪 Testes

### Estrutura

- `tests/unit/`: Testes rápidos, sem I/O
- `tests/integration/`: Testes com bibliotecas reais e integração de adaptadores
- `tests/gui/`: Testes de unidade e integridade para widgets PyQt6
- `tests/e2e/`: Testes de ponta a ponta (instalação e fluxos do SO)

> [!NOTE]
> Testes de GUI que dependem de renderização complexa (como Shadow Effects) são ignorados automaticamente em ambientes **Headless** (CI/CD) para evitar deadlocks, mas devem ser validados localmente.

### Exemplo de Teste

```python
def test_rotate_pdf():
    """Testa rotação de 90º."""
    adapter = PyMuPDFAdapter()
    use_case = RotatePDFUseCase(adapter)
    
    result = use_case.execute(
        pdf_path=Path("tests/data/sample.pdf"),
        degrees=90
    )
    
    assert result.exists()
    # Verificar que rotação foi aplicada
```

## 📋 Checklist de PR

Antes de submeter um Pull Request:

- [ ] Código segue os padrões (Black, Flake8)
- [ ] Testes adicionados/atualizados
- [ ] Todos os testes passam localmente
- [ ] Documentação atualizada (se aplicável)
- [ ] Commit messages seguem Conventional Commits
- [ ] Branch está atualizado com `main`

## 🏷️ Labels de Issues

- `bug`: Algo não funciona
- `enhancement`: Nova feature ou melhoria
- `good-first-issue`: Bom para iniciantes
- `help-wanted`: Precisamos de ajuda!
- `documentation`: Relacionado a docs
- `question`: Dúvida ou discussão

## 🤔 Dúvidas?

- Abra uma **Discussion** no GitHub
- Consulte [[docs/MAP|Documentação Completa]]
- Entre em contato com os mantenedores

## 📜 Código de Conduta

Seja respeitoso, construtivo e inclusivo. Estamos construindo uma comunidade saudável.

---

**Obrigado por contribuir!** 🎉

[[docs/MAP|Voltar ao Mapa]]
