# 📦 Instalação do fotonPDF

Este guia irá ajudá-lo a instalar o fotonPDF no seu computador Windows.

## 📥 Download e Instalação

O fotonPDF é distribuído de duas formas:

1. **Instalador Profissional (Recomendado)**: Baixe o `fotonPDF_Setup_v1.0.0.exe`. Ele instalará o software em seu computador e criará atalhos automaticamente.
2. **Versão Portátil**: Baixe o arquivo `.zip`, extraia-o em uma pasta (ex: `C:\Programas\fotonPDF\`).

> [!NOTE]
> Utilizamos a distribuição em **Diretório (`--onedir`)** para garantir estabilidade máxima com a interface gráfica (PyQt6) e abertura instantânea do aplicativo.

## 🚀 Configuração (Setup)

Se você optou pela **Versão Portátil**, abra a pasta extraída e execute o arquivo `INSTALAR.bat`.

Ou, via terminal na pasta `foton/`:

```powershell
./foton.exe setup
```

O assistente irá guiá-lo pelo processo:

- Registro no Menu de Contexto (com prefixo **fotonPDF ▸**)
- Verificação de integridade

## ✅ Verificar Status

Para confirmar que os menus foram registrados:

```powershell
./foton.exe status
```

Se aparecer "Menu de Contexto: ✅ Instalado", você está pronto para usar!

---

## 🐍 Via Python (Para Desenvolvedores)

Se você preferir rodar via Python:

1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Execute: `python -m src.interfaces.cli.main setup`

---

## 🎉 Pronto

Agora você pode clicar com o botão direito em qualquer arquivo PDF e escolher **"Abrir com fotonPDF"**.
