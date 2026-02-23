# 🎡 Estratégia de CI/CD e Releases

Este guia explica como o **fotonPDF** gerencia automação de código, testes e distribuição profissional.

---

## 1. Fluxo de Trabalho (Branching Model)

Adotamos uma versão simplificada do **GitHub Flow**:

* **`main`**: Branch de produção. Deve conter sempre código estável e testado.
* **`develop`**: Branch de integração. Onde as novas funcionalidades "se encontram" antes de irem para a `main`.
* **Feature Branches**: Criadas a partir da `develop` (ex: `feat/busca-texto`).

---

## 2. Automação (GitHub Actions)

O projeto possui dois gatilhos principais:

### 🧪 Pull Requests (CI)

Toda vez que você abrir um PR para `main` ou `develop`:

1. **Testes**: O GitHub cria uma máquina virtual Windows.
2. **Verificação**: Roda `pytest` em todos os módulos.
   * *Nota: Testes de interface pesados são detectados e ignorados em ambiente Headless para garantir estabilidade do runner.*
3. **Status**: O PR só pode ser mesclado se os testes passarem.

### 📦 Nova Release (CD)

Para lançar uma nova versão oficial do sistema:

1. **Tag**: Crie uma tag Git seguindo o padrão semântico (ex: `git tag v1.1.0` e `git push --tags`).
2. **Build Automático**: O GitHub detecta a tag e inicia o build.
3. **Validação do Centro de Verdade**: O sistema verifica se a versão definida em `src/__init__.py` coincide exatamente com a Tag criada. Se houver divergência, o build é cancelado para evitar erros.
4. **Build, Assinatura & Setup**: O servidor compila o código, gera o instalador (injetando a versão dinamicamente) e aplica a assinatura digital.
5. **Entrega**: Uma página de **Release** é criada automaticamente com o arquivo `.exe` pronto para download.

---

## 3. Templates de Comunicação

Para manter o projeto "User-Friendly" e organizado:

* **Pull Requests**: Devem descrever o "quê" e o "porquê" da mudança.
* **Issue Templates**: Ajudam o usuário a reportar bugs detalhados.
* **Release Notes**: São geradas automaticamente com base nos nomes dos Pull Requests mesclados.

---

## 🚀 Como lançar uma nova versão corretamente?

Para garantir que o pipeline funcione sem erros, siga esta ordem:

1. **Atualize a Versão**: Mude o valor de `__version__` em `src/__init__.py` (ex: "1.2.0").
2. **Commit**: Faça o commit dessa alteração (ex: `chore: bump version to 1.2.0`).
3. **Tag**: No terminal, crie a tag idêntica: `git tag v1.2.0`.
4. **Push**: Envie a tag para o GitHub: `git push origin --tags`.
5. **Aguarde**: O pipeline irá validar a paridade, compilar e gerar a Release automaticamente.

> [!IMPORTANT]
> Se a tag for diferente da versão no código, o GitHub Actions falhará e a release não será publicada.

---
*fotonPDF - De desenvolvedores para produtividade máxima.*
