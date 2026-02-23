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

## 🗑️ Desinstalação (Processo Nativo OS)

O processo de desinstalação do fotonPDF foi rigorosamente remodelado (v1.1.0+) para se integrar de forma completamente nativa às **Configurações e Painel de Controle do Windows**, garantindo que não restem arquivos órfãos ("lixo") ou entradas perdidas no Registro.

Para remover o fotonPDF completamente do seu sistema:

### Passo 1: Desinstalação Oficial via Windows

1. Acesse **Configurações do Windows** > **Aplicativos** (ou **Painel de Controle** > **Programas e Recursos**).
2. Procure por `fotonPDF` na barra de pesquisa.
3. Clique em **Desinstalar**.

O processo será executado pela suíte do *Inno Setup* (via `unins000.exe`), que orquestrará as seguintes etapas em *background*:

- Acionamento silencioso do serviço CLI interno (`foton-cli.exe uninstall -y`) para limpar recursivamente chaves vinculadas ao fotonPDF (`HKEY_CURRENT_USER\Software\Classes\*\shell\FotonPDF.*`).
- Ocultamento de prompts e chamadas de console que exigiriam interação manual, prevenindo "travamentos" (hangs) no painel de desinstalação.
- Exclusão da pasta de instalação (localizada por padrão na raiz de `AppData\Local\fotonPDF`) das variáveis de ambiente (`PATH`), desregistrando o comando de terminal global.

### Passo 2: Limpeza de Cache de Execução (Opcional)

A desinstalação ofical focará nos artefatos instalados e binários embutidos pelo PyInstaller/Inno Setup.
Por medidas conservadoras arquiteturais, logs processuais em tempo-de-execução não são excluídos proativamente para preservar o histórico em casos onde você esteja desinstalando o foton apenas como medida de "Reinstalação para Conserto" (Troubleshooting).

Se você deseja limpar a máquina **completamente**:

1. Pressione `Win + R`, digite `%localappdata%\fotonPDF` e pressione `Enter`.
2. Se houver uma pasta residual (ex: diretório `logs`), você pode excluí-la manualmente e de forma totalmente segura.

### Por que não via CLI (`foton.exe uninstall`) em Produção?

Embora a CLI nativa continue possuindo poderosos mecanismos expostos pelo subcomando de `uninstall`, eles foram desenhados como motores de "backbone" para o orquestrador global (Inno Setup).
Executar o comando manual para limpar o registro não removerá atalhos na Área de Trabalho ou as bibliotecas PyInstaller pesadas, fracionando o estado de distribuição na sua máquina. Sendo assim, o fluxo correto para um *"Clean Slate"* passa inevitavelmente pelas Configurações do Windows.
