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

---

## 🛡️ Simulação Obrigatória de Release (Local)

**Qualquer modificação que vise ser integrada nas branches `develop` ou `main` deve, OBRIGATORIAMENTE, ser validada localmente através do nosso simulador de pipeline CI/CD.**

Antes de abrir um Pull Request, execute em um terminal PowerShell na raiz do projeto:

```powershell
.\scripts\test_release_pipeline.ps1
```

### Por que isso é obrigatório?

Ao longo do desenvolvimento, novos `imports` em Python podem não ser resolvidos automaticamente pelo PyInstaller, ou novos arquivos estáticos podem ficar fora do instalador Inno Setup (`foton_installer.iss`).
Se você fizer o push sem validar localmente, o GitHub Actions falhará silenciosamente no momento da Tag, poluindo o histórico e exigindo commits obscuros de "fix build".

### O que o script simula e audita

1. **Extração de C.V:** Identifica a versão oficial em `src/__init__.py`.
2. **PyInstaller:** Gera os executáveis otimizados simulando restrições de ambiente isolado (`build_exe.py`).
3. **Assinatura:** Processso digital assíncrono (simulado/real) para garantir infraestrutura do `.pfx`.
4. **Inno Setup:** Aciona o compilador `iscc` nativo injetando o versionamento para gerar o `Setup.exe`.
5. **Portable ZIP:** Compacta o artefato binário standalone simulando a portabilidade pesada do Windows.
6. **Release Notes:** Templates Markdown são populados para antecipar o release body do GitHub.

### Checklist Pós-Simulação

Após a conclusão do script `test_release_pipeline.ps1`, acesse a pasta `dist/` gerada na raiz do projeto e garanta que os seguintes arquivos estejam presentes, e tente rodar o instalador na sua própria máquina local:

* `fotonPDF_Setup_v{SUA_VERSAO}.exe`
* `fotonPDF-portable-v{SUA_VERSAO}.zip`
* `release_notes.md`

Se houver qualquer erro de compilação local (como *ModuleNotFoundError*, problemas de encoding ou falta do compilador iscc), corrija os imports / hooks / caminhos absoutos na sua branch de origem antes de continuar o processo cíclico do PR.

---### 📦 Nova Release (CD)

Para lançar uma nova versão oficial do sistema:

1. **Tag**: Crie uma tag Git seguindo o padrão semântico (ex: `git tag v1.2.0` e `git push origin v1.2.0`).
2. **Build Automático**: O GitHub detecta a tag e inicia o build no runner `windows-latest`.
3. **Validação do Centro de Verdade**: O sistema verifica se a versão definida em `src/__init__.py` coincide exatamente com a Tag criada. Se houver divergência, o build é cancelado para evitar erros.
4. **Build, Assinatura & Setup**: O servidor compila o código via PyInstaller, assina os executáveis, e compila o instalador Inno Setup injetando a versão dinamicamente.
5. **ZIP Portátil**: A pasta `dist/foton/` é compactada em `fotonPDF-portable-v{version}.zip` para distribuição leve.
6. **Release Notes**: Um template profissional (`.github/RELEASE_TEMPLATE.md`) é preenchido automaticamente com a versão e usado como corpo da Release.
7. **Entrega**: Uma página de **Release** é criada automaticamente com dois artefatos:
   * `fotonPDF_Setup_v{version}.exe` — Instalador profissional (recomendado)
   * `fotonPDF-portable-v{version}.zip` — Versão portátil (descompactar e usar)

> [!NOTE]
> O workflow define `PYTHONIOENCODING=utf-8` globalmente para garantir compatibilidade de encoding com o runner Windows.

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
