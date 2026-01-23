# ✨ Funcionalidades do fotonPDF

Este documento detalha as capacidades técnicas do **fotonPDF**, explicando sua implementação profunda, modos de uso avançados e as melhores práticas recomendadas para produtividade máxima.

---

## 🛠️ 1. Manipulação Core (Motor PDF)

As funcionalidades core são implementadas sobre o adaptador `PyMuPDF` (fitz), garantindo alta fidelidade e performance.

### 1.1 Girar Páginas (Rotate)

- **O que faz:** Rotaciona páginas específicas ou todo o documento em incrementos de 90°.
- **Interno:** Implementado via `src/application/use_cases/rotate_pdf.py`. No modo visual, a rotação é aplicada no `PDFStateManager` como um `rotation_offset`, permitindo que o usuário visualize a mudança instantaneamente sem modificar o arquivo original até o momento do "Salvar".
- **Como utilizar:**
  - **GUI:** Selecione as miniaturas na barra lateral (use `Ctrl` para múltiplas) e clique em **Girar -90°** ou **Girar +90°**.
  - **CLI:** `foton rotate --file "doc.pdf" --pages 1,3 --degrees 90`
- **Integridade**: O sistema sincroniza o índice visual com o estado interno, garantindo que a página rotacionada seja exatamente a que você selecionou, mesmo após reordenações.

### 1.2 Unir PDFs (Merge 2.0 - Documento Virtual)

- **O que faz:** Combina múltiplos arquivos PDF em um único fluxo de trabalho contínuo.
- **Diferencial Técnico:** Introduz o conceito de **Documento Virtual**. Em vez de unir arquivos fisicamente no disco e recarregar, o fotonPDF gerencia uma lista dinâmica de referências para páginas de diferentes arquivos fonte. Isso torna a "unificação" instantânea.
- **Interface Inteligente:**
  - Arraste arquivos para a **Sidebar** para anexá-los ao documento atual.
  - Arraste para o **Centro** para abrir como um novo projeto.
- **Boas Práticas:** Utilize a reordenação por Drag & Drop na sidebar para organizar o documento final antes de salvar.

---

## 🖥️ 2. Visualizador Fóton (GUI Premium)

Interface gráfica em **PyQt6**, projetada para ser o centro de controle do seu fluxo de trabalho documental.

### 2.1 Motor de Renderização Concorrente (`RenderEngine`)

- **Implementação**: Localizada em `src/interfaces/gui/state/render_engine.py`. Utiliza `QThreadPool` com limite de concorrência (2 threads) para evitar que o Windows esgote recursos ao abrir PDFs massivos.
- **Estabilidade**: Cada página é renderizada em uma tarefa isolada. Se uma página estiver corrompida, o visualizador continua operando normalmente para as demais.

### 2.2 Navegação Adaptativa

- **Ajuste de Tela**: Os botões de **Largura** e **Altura** são "conscientes do contexto". Eles identificam qual página está mais visível no topo do viewport e ajustam o zoom baseado nas dimensões reais *daquela página específica*.
- **Suporte Mixed-Size**: Perfeito para documentos que misturam páginas A4 vertical com plantas de engenharia no formato paisagem (A3/A2).

### 2.4 Async Split (Visão Dual Independente)

- **O que faz**: Permite ao usuário visualizar duas regiões distintas do *mesmo* arquivo PDF lado a lado.
- **Diferencial**: Diferente do "Dual View" tradicional (que foca em documentos diferentes), o Async Split desacopla o scroll e o zoom. Você pode manter o sumário visual da página 1 em uma metade enquanto detalha os termos técnicos da página 90 na outra.
- **Interface**: Ativável via ícone "Dividir" na Floating NavBar ou atalho direto.

### 2.3 Extração Visual Premium

- **O que faz:** Cria um novo arquivo PDF contendo apenas as páginas que você selecionou visualmente.
- **Processo**:
    1. Selecione as páginas desejadas na sidebar (ordenadas como desejar).
    2. Clique em **Extrair** na Toolbar.
    3. O sistema compila um novo PDF binário unindo as fontes originais e preservando a nova ordem e rotações aplicadas.
- **Uso Comum**: Separar páginas de um contrato ou criar um resumo de um relatório extenso.

---

## 🏗️ 4. Infraestrutura de Resiliência (Fault Tolerance)

O fotonPDF foi desenvolvido com uma filosofia de "Crash-Proofing" para garantir que erros locais não interrompam o trabalho do usuário.

### 4.1 UI Error Boundaries (@safe_ui_callback)

- **Implementação**: Decorador centralizado que envolve eventos do Qt.
- **Comportamento**: Se um erro ocorrer ao girar uma página ou abrir um painel lateral, a exceção é capturada, logada em **Red** no `BottomPanel` e o usuário pode continuar usando outras partes do software sem crash.

### 4.2 Global Exception Hook

- **O que faz**: Captura erros fatais que escapam dos decorators e garante que eles sejam registrados e notificados via logs estruturados, facilitando o diagnóstico técnico remoto.

---

## 🚀 3. Suíte de Conversão Profissional

Converta o conteúdo estático do PDF em ativos úteis para outros softwares.

### 3.1 Exportação para Imagem (High-DPI)

- **Formatos**: **PNG** (Lossless), **JPG** (Web), **WebP** (Moderno).
- **Qualidade Técnica**: Gera buffers de imagem a **300 DPI** (dots per inch). Diferente de capturas de tela, a exportação utiliza o motor vetorial do PDF para rasterizar o texto com nitidez cirúrgica.
- **Fluxo**: Utiliza o componente `QImage` para garantir compressão otimizada e compatibilidade total com visualizadores de imagem padrão.

### 3.2 Exportação SVG (Vetor Nativo)

- **O que faz**: Converte a geometria da página em XML vetorial.
- **Vantagem**: O arquivo gerado pode ser aberto em ferramentas como **Figma**, **Illustrator** ou browsers, mantendo a capacidade de redimensionamento infinito sem perda de definição.

### 3.3 Exportação Markdown (Text Logic)

- **O que faz**: Extrai a estrutura semântica do documento para um arquivo `.md`.
- **Implementação**: Tenta identificar cabeçalhos, tabelas e parágrafos. Cada página do PDF é separada por um divisor `---` e um título `# Página X`.
- **Ideal para**: Usuários de **Obsidian**, **Logseq** ou **Notion** que precisam processar textos de PDFs de forma rápida e estruturada.

---

## 🖥️ 4. Integração com Sistema Operacional

Conforto e rapidez diretamente da área de trabalho.

### 4.1 Menu de Contexto (Windows)

- **Acesso**: Botão direito no Explorer ▸ `fotonPDF ▸`.
- **Timestamps**: Todas as ações rápidas (Girar, Unir) geram novos arquivos com a marca de tempo no nome (ex: `documento_ROTATE_20260118.pdf`). Isso garante que você nunca perca o arquivo original por um erro de operação.

---

## 📦 5. Inteligência de Distribuição

Garantindo que o usuário tenha sempre a versão mais segura e funcional com o mínimo esforço.

### 5.1 Notificação de Nova Versão (`UpdateService`)

- **O que faz**: Verifica silenciosamente na API do GitHub se existe uma release mais recente que a versão atual (`__version__`).
- **Comportamento**:
  - Exibe um alerta visual no menu interativo caso uma atualização esteja disponível.
  - Comando CLI: `foton update` fornece o link direto e o changelog da nova versão.

### 5.2 Bootstrap Inteligente (Auto-Reparo)

- **O que faz**: Resolve problemas comuns de integração, como quando o menu de contexto some após o software ser movido de pasta ou chaves de registro serem alteradas por outros programas.
- **Acesso**: Opção **[R] Reparar Integração** no menu principal.
- **Lógica**: O sistema detecta o caminho absoluto atual e força a atualização das chaves de registro do Windows, garantindo que o `fotonPDF ▸` sempre aponte para o local correto no disco.

### 5.3 Infraestrutura de Assinatura de Código (Integridade)

- **O que faz**: O pipeline de build está preparado para assinar os binários (`.exe`), garantindo que o software não foi alterado após a compilação por agentes maliciosos.
- **Implementação**: Script `scripts/sign_exe.py` que gera certificados de desenvolvimento e aplica assinaturas digitais via `SignTool`.

---

## 🔗 Relacionamentos e Navegação

- [[ARCHITECTURE|🏗️ Arquitetura]]: Saiba mais sobre o motor centralizado.
- [[DASHBOARD|🎛️ Dashboard]]: Status atual de cada funcionalidade.
- [[guides/NEW_OPERATION|➕ Guia de Operações]]: Como estender o sistema com novos conversores.

---
[[MAP|← Voltar ao Mapa]]
