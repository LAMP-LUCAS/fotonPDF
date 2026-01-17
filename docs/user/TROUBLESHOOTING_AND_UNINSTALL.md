# 🛠️ Resolução de Problemas & Desinstalação

Abaixo você encontra soluções para os problemas mais comuns e o guia para remover o sistema.

## ⛑️ Troubleshooting (Correções)

### 1. A opção "Abrir com fotonPDF" não aparece

- Certifique-se de que executou o comando `foton install` como administrador se o seu usuário não tiver permissões de escrita no registro.
- Tente reiniciar o Explorador de Arquivos (ou o computador).

### 2. O aplicativo abre e fecha instantaneamente

- Verifique se o arquivo PDF não está corrompido.
- Se estiver rodando a versão Python, verifique se todas as dependências do `requirements.txt` foram instaladas.

### 3. Erro ao tentar extrair páginas

- Verifique se você tem permissão de escrita na pasta onde está tentando salvar o novo arquivo.
- Certifique-se de que o arquivo original não está bloqueado por outro programa (como o Adobe Reader).

---

## 🗑️ Desinstalação

Para remover o fotonPDF completamente do seu sistema:

### Passo 1: Remover do Menu de Contexto

Antes de deletar o arquivo, abra o terminal na pasta do app e digite:
`foton remove` (em implementação) ou use o utilitário de limpeza de registro.

### Passo 2: Deletar Arquivos

Delete a pasta onde o `foton.exe` está localizado.

### Passo 3: Limpeza de Cache

O fotonPDF não deixa "lixo" no sistema, apenas uma pequena chave de registro que pode ser removida conforme o Passo 1.
