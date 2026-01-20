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
3. **Status**: O PR só pode ser mesclado se os testes passarem.

### 📦 Nova Release (CD)

Para lançar uma nova versão oficial do sistema:

1. **Tag**: Crie uma tag Git seguindo o padrão semântico (ex: `git tag v1.1.0` e `git push --tags`).
2. **Build Automático**: O GitHub detecta a tag e inicia o build.
3. **Assinatura & Setup**: O servidor compila o código, gera o instalador e aplica a assinatura digital.
4. **Entrega**: Uma página de **Release** é criada automaticamente com o arquivo `.exe` pronto para download.

---

## 3. Templates de Comunicação

Para manter o projeto "User-Friendly" e organizado:

* **Pull Requests**: Devem descrever o "quê" e o "porquê" da mudança.
* **Issue Templates**: Ajudam o usuário a reportar bugs detalhados.
* **Release Notes**: São geradas automaticamente com base nos nomes dos Pull Requests mesclados.

---

## 🚀 Como lançar uma nova versão rápida?

Se você terminou uma feature e quer entregar ao usuário:

1. Garanta que o código está na `main`.
2. No terminal: `git tag v1.X.X` (substitua pelo número correto).
3. Execute: `git push origin --tags`.
4. Aguarde 5-10 minutos e verifique a aba **Releases** no GitHub.

---
*fotonPDF - De desenvolvedores para produtividade máxima.*
