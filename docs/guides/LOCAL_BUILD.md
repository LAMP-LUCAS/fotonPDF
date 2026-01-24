# 🏗️ Guia de Build Local (fotonPDF)

Este guia descreve como gerar o executável standalone e o instalador do **fotonPDF** em sua máquina local.

---

## 🛠️ Pré-requisitos

1. **Python 3.11+**: Certifique-se de que o Python está no seu PATH.
2. **Dependências**:

    ```bash
    pip install -r requirements.txt
    pip install pyinstaller
    ```

3. **Inno Setup (Opcional)**: Para gerar o arquivo `.exe` de instalação profissional, instale o [Inno Setup 6+](https://jrsoftware.org/isdl.php) e adicione o diretório ao seu PATH.

---

## 🚀 Passo a Passo

### 1. Limpeza de Ambiente

Remova pastas de builds anteriores para evitar conflitos:

```bash
rmdir /s /q build dist
```

### 2. Compilação do Executável

Execute o script de orquestração do PyInstaller:

```bash
python scripts/build_exe.py
```

> [!IMPORTANT]
> O executável será gerado em `dist/foton_v1.0.0/foton_v1.0.0.exe`. Ele utiliza o modo `--onedir` para maior estabilidade.

### 3. Assinatura Digital (Opcional/Dev)

Para reduzir alertas do Windows SmartScreen:

```bash
python scripts/sign_exe.py
```

*Nota: Requer privilégios administrativos no terminal para gerar certificados auto-assinados.*

### 4. Geração do Instalador

Se o Inno Setup estiver instalado, execute:

```bash
iscc foton_installer.iss
```

O arquivo final `fotonPDF_Setup_v*.exe` será criado na raiz do projeto.

---

## 🔍 Verificação

Após o build, verifique se a pasta `dist/_internal` contém todos os módulos críticos, especialmente:

- `PyQt6`
- `fitz` (PyMuPDF)
- `litellm`
- `instructor`

---
*fotonPDF - Construído para performance e portabilidade.*
