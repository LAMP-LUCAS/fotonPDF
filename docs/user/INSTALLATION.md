# 📦 Instalação do fotonPDF

Este guia irá ajudá-lo a instalar o fotonPDF no seu computador Windows.

## 📥 Download e Instalação

O fotonPDF foi projetado como uma ferramenta agnóstica de elevado isolamento. Ele está disponível de duas formas:

1. **Instalador Oficial Inno Setup (Recomendado)**: Baixe o arquivo `fotonPDF_Setup_v1.0.0.exe` da pasta `/dist` ou diretório de Releases. Este binário foi gerado através de um compilador de distribuição sólido e provisiona toda a automação do sistema em formato *Zero-Click Configuration*.
2. **Versão Portátil (Stand-Alone)**: Baixe o arquivo `.zip` e extraia-o em uma pasta qualquer (ex: `C:\Programas\fotonPDF\`). Destinado apenas para usuários experientes que queiram inserir a aplicação localmente de forma isolada do Painel de Controle, mas à custa da integração OS nativa e limpa garantida pelo instalador.

> [!NOTE]
> Distribuímos a aplicação compilada através do padrão PyInstaller **Diretório (`--onedir`)**. Enquanto `onefile` causaria travamentos de dezenas de segundos a cada abertura devido ao unpacking nativo do Python, nós garantimos estabilidade extrema e abertura visual instantânea das interfaces gráficas PyQt6 embutindo todos os pacotes num diretório unificado.

## 🚀 Instalador Automático (Zero-Click OS Integration)

O instalador `fotonPDF_Setup_v1.0.0.exe` resolve três dores estruturais no background sem a necessidade de comandos manuais:

1. **Associação de Visualizador**: Permite definir o fotonPDF como "Leitor de PDF Oficial" via Checkbox durante a UI de instalação através de chaves do `winreg` (ação executada pelo módulo CLI python compilado).
2. **Integração de Menu**: Adiciona opções (`fotonPDF ▸ Abrir`, `fotonPDF ▸ Girar 90°`) de forma enclausurada e não intrusiva nas chaves customizadas em `HKEY_CURRENT_USER\Software\Classes\*\shell\FotonPDF.*`.
3. **Registro Automático em PATH**: Modifica variáveis de sistema local injetando as rotas da sua pasta `AppData\Local` em `Path`, liberando a palavra chave nativa global `foton` para o terminal (Command Prompt, VSCode, Powershell) instantaneamente.

## ⚙️ Configuração Manual (Apenas Instalação Portátil)

Se você ignorou o Inno Setup e preferiu mover a versão zipada do foton para uma pasta privada, precisará integrar os menus do Windows de forma manual invocando as bibliotecas via linha de comando principal nativa (`foton.exe`).

Abra o prompt de comando focado na raiz da sua instalação foton e execute a seguinte infraestrutura CLI de integração manual:

```powershell
./foton.exe setup
```

O *Setup Wizard* rodará de forma interativa ou autônoma no terminal:

- Solicitando verificação para injetar a árvore Foton no Menu de Contexto do Computador.
- Testando integridade local e permissões de escrita de disco.

### Comandos de Atalhos Adicionais

Para acionar um vínculo interativo de PDF Default *fora do instalador*, force a chamada na raiz:

```powershell
./foton.exe setup --set-default
```

Para uso sem interação ou bloqueio visual (CI/CD / Provisionamento Massivo de Máquinas de Empresa), utilize a flag nativa (desenvolvida na v1.1.0):

```powershell
./foton.exe setup -q --set-default
```

## ✅ Verificar Status do Computador

Para comprovar que o sistema nativo (Installer Automático) ou Terminal (Guia Acima) concluíram com sucesso os *branches* exigidos no Windows, digite em qualquer terminal aéreo:

```powershell
foton status
```

Se apontar estado de êxito para `Menu de Contexto: ✅ Instalado`, toda sua distribuição OS foi interconectada positivamente!

---

## 🐍 Pipeline do Repositório (Para Engenheiros)

Se você preferir rodar a build a partir da raiz local `.py` ao invés da raiz `.exe`:

1. Clone o repositório (`git clone`).
2. Instale as dependências robustamente listadas via Pipenv ou Virtualenv: `pip install -r requirements.txt`. (Isso absorverá a biblioteca fundamental PyQt6, PyMuPDF e arquiteturas generativas locais llm).
3. Execute o script principal de orquestração do módulo Click (CLI):
   `python -m src.interfaces.cli.main setup`

Esta é a única rota que depende obrigatoriamente da injeção do pacote interpretador nativo do Python 3.11+ no disco, operando da exata mesma maneira que o sistema enclausurado em .exe do pacote Windows nativo finalizado de mercado fará.
