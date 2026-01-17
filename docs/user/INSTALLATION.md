# 📦 Instalação do fotonPDF

Este guia irá ajudá-lo a instalar o fotonPDF no seu computador Windows.

## 📥 Download

1. Acesse a página de [Releases do GitHub](https://github.com/LAMP-LUCAS/fotonPDF/releases)
2. Baixe o arquivo `foton.exe` da versão mais recente
3. Salve em uma pasta de sua preferência (ex: `C:\Programas\fotonPDF\`)

## 🚀 Configuração (Setup)

Após o download, abra o terminal (PowerShell ou CMD) na pasta onde salvou o `foton.exe` e execute:

```powershell
./foton.exe setup
```

O assistente irá guiá-lo pelo processo de configuração, exibindo cada etapa:

- Verificação de permissões
- Registro no Menu de Contexto do Windows
- Verificação de integridade

## ✅ Verificar Instalação

Para confirmar que tudo está funcionando:

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
