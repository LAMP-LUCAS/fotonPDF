# 🏗️ Arquitetura do Sistema

O **fotonPDF** utiliza uma abordagem híbrida que une a **Arquitetura Hexagonal (Ports & Adapters)** com o conceito de **Monólito Modular**.

## 🧬 O Conceito Híbrido

1. **Hexagonal:** Garante que a lógica de "como girar um PDF" seja independente de "qual biblioteca usamos" ou "se foi clicado no Windows ou Linux".
2. **Modular:** Organiza o código por funcionalidades (Core, Conversão, Automação), facilitando que um dev foque em apenas uma área sem quebrar o resto.

## 📐 Camadas

### 1. Domínio (`src/domain`)

- Onde residem as regras de negócio puras.
- **Entidades:** `PDFDocument`, `Page`, `Coordinates`.
- **Portas (Interfaces):** `PDFProcessorPort`, `FileSystemPort`.

### 2. Aplicação (`src/application`)

- Orquestra os casos de uso.
- Exemplos: `RotatePDFUseCase`, `MergeFilesUseCase`.
- Não conhece detalhes de implementação (não importa `fitz` ou `winreg`).

### 3. Infraestrutura (`src/infrastructure`)

- Implementações concretas e pesadas.
- **Adapters:** `PyMuPDFAdapter`, `WindowsRegistryAdapter`.
- Aqui lidamos com o "mundo real" (disco, rede, SO).

### 4. Interfaces (`src/interfaces`)

- Pontos de entrada para o usuário.
- `ContextMenuItem`: Aciona comandos via Shell.
- `QuickViewer`: UI de visualização ultra-rápida em PyQt6.

## 🔄 Fluxo de Uma Operação

1. Usuário clica em "Girar 90º" no Menu de Contexto.
2. O SO executa o comando `foton-cli --rotate 90 --file path/to.pdf`.
3. A `CLI Interface` recebe o comando e chama o `RotatePDFUseCase`.
4. O `UseCase` solicita ao `PyMuPDFAdapter` (via porta) que execute a rotação.
5. O arquivo é salvo e uma notificação de sistema é disparada.

## 🔗 Veja Também

- [[DEVELOPMENT|Workflow e Padrões]]
- [[MAP|Voltar ao Mapa]]
