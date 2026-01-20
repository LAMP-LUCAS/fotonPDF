# 📊 Relatório Comparativo: fotonPDF vs. Okular vs. Acrobat Reader

Este documento apresenta uma análise técnica e funcional comparando o **fotonPDF** (solução interna) com os dois maiores paradigmas do mercado: o **Okular** (referência open-source/KDE) e o **Adobe Acrobat Reader** (padrão proprietário/corporativo).

---

## 🏗️ 1. Arquitetura e Motor de Renderização

| Característica | **fotonPDF** | **Okular (KDE)** | **Acrobat Reader** |
| :--- | :--- | :--- | :--- |
| **Motor Principal** | **PyMuPDF (fitz)** / PDFium | **Poppler** | Adobe PDF Engine (Vetor Próprio) |
| **Interface** | PyQt6 / QML (Ultra-leve) | Qt (KDE Frameworks) | Adobe Desktop UI (Pesada) |
| **Abordagem** | Hexagonal + Monólito Modular | Plugin-based (Universal) | Monólito Proprietário |
| **Performance I/O** | Assíncrona via `RenderEngine` | On-demand (Scroll) | Cache pesado e pré-carregamento |

> [!TIP]
> O **fotonPDF** utiliza o PyMuPDF, que é frequentemente documentado como sendo até **5x mais rápido** que o Poppler (usado no Okular) em renderização de páginas complexas.

---

## 🖥️ 2. Experiência do Usuário e Integração

### fotonPDF: Velocidade Cirúrgica

- **Diferencial:** Focado em **Contexto**. A maioria das operações (Girar, Unir) é feita sem abrir o editor, diretamente pelo Explorador de Arquivos (Shell Extension).
- **Inovação:** Documentos Virtuais. Permite manipular páginas e referências instantaneamente antes de salvar o binário final.

### Okular: O Canivete Suíço Universal

- **Diferencial:** Versatilidade. Abre PDFs, EPubs, MDs e até imagens.
- **Limitação:** Como é um visualizador universal, as ferramentas de edição e manipulação são "camadas superiores" (anotações não-destrutivas por padrão), o que pode dificultar a alteração direta da estrutura do PDF.

### Acrobat Reader: O Padrão Corporativo

- **Diferencial:** Fidelidade absoluta a formulários complexos e assinaturas digitais certificadas pela Adobe.
- **Crítica:** Elevado uso de recursos (bloatware). Notório por processos em segundo plano constantes e insistência em serviços de nuvem (Adobe Cloud).

---

## 🚀 3. Matriz de Funcionalidades

| Recurso | fotonPDF | Okular | Acrobat Reader |
| :--- | :--- | :--- | :--- |
| **Girar/Salvar** | Instantâneo (Contexto) | Requer salvar como/exportar | Requer Pro ou exportação |
| **Merge (Unir)** | Nativo e Visual | Via interface de impressão/ferramentas | Apenas versão Pro (paga) |
| **Exportação MD** | Inclusa (Foco Obsidian) | Não nativa | Não disponível |
| **Assinatura Digital** | Em desenvolvimento | Suporte avançado | Padrão ouro da indústria |
| **OCR** | Planejado (EasyOCR) | Requer plugins externos | Apenas versão Pro |

---

## 📈 4. Performance e Pegada de Sistema

1. **fotonPDF:** Projetado para "Entrar, Resolver, Sair". Ocupa pouca memória RAM pois não carrega serviços de telemetria ou nuvem persistentes.
2. **Okular:** Muito eficiente em Linux, mas pode carregar muitas dependências das bibliotecas KDE no Windows.
3. **Acrobat Reader:** O mais pesado. Frequentemente criticado pela lentidão ao abrir o primeiro arquivo devido ao carregamento de módulos corporativos desnecessários para tarefas simples.

---

## 🎯 5. Veredito: Quando usar cada um?

- **Use fotonPDF quando:** Precisar de produtividade extrema, automação de arquivos via menu de contexto, unir/girar documentos rapidamente e exportar textos para ferramentas de nota (Markdown).
- **Use Okular quando:** Precisar de um visualizador consistente para múltiplos formatos (EPub, CBR) e anotações ricas em um ambiente de código aberto.
- **Use Acrobat Reader quando:** Estiver lidando com formulários governamentais complexos ou precisar de validação legal de assinaturas digitais proprietárias.

---

## 🔗 Navegação

- [[ARCHITECTURE|🏗️ Arquitetura do fotonPDF]]
- [[FEATURES|✨ Funcionalidades Detalhadas]]
- [[MAP|🗺️ Voltar ao Mapa]]

---
*Relatório gerado em 2026-01-20 como parte da análise de posicionamento de mercado.*
