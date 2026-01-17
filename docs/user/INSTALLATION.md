# 📥 Guia de Instalação

Bem-vindo ao **fotonPDF**! Siga os passos abaixo para preparar sua ferramenta de PDF ultra-rápida.

## 🪟 Windows (Recomendado)

O fotonPDF é distribuído como um executável "portátil", o que significa que você não precisa de um instalador complexo para começar a usar.

1. **Download:** Baixe a versão mais recente (`foton.exe`) na aba de [Releases](https://github.com/LAMP-LUCAS/fotonPDF/releases).
2. **Localização:** Mova o arquivo para uma pasta segura em seu computador (ex: `C:\Program Files\fotonPDF` ou uma pasta em seus Documentos).
3. **Ativação do Menu de Contexto:**
   - Abra o terminal (PowerShell ou CMD) na pasta do executável.
   - Digite: `./foton.exe install`
   - Uma notificação aparecerá confirmando que o fotonPDF agora está integrado ao seu Explorador de Arquivos.

---

## 🐍 Via Python (Para Desenvolvedores)

Se você preferir rodar via Python:

1. Clone o repositório.
2. Instale as dependências: `pip install -r requirements.txt`
3. Instale o comando global: `pip install -e .`
4. Use o comando `foton install` para integrar ao Windows.

---

## ✅ Verificação

Após a instalação, clique com o botão direito em qualquer arquivo `.pdf` no seu computador. Você deverá ver a opção **"Abrir com fotonPDF"**.
