# Padrões de Seleção UI/UX - fotonPDF

Este documento descreve a lógica de seleção de texto e objetos implementada no `PDFViewerWidget`, inspirada em softwares de engenharia (AutoCAD) e design (Blender/Inkscape).

## 1. Seleção Geométrica (Box Selection)

A seleção utiliza o movimento direcional para alternar entre dois comportamentos distintos:

### Crossing Selection (Verde)

- **Direção**: Da **Esquerda para a Direita** (L → R).
- **Lógica**: Seleciona tudo o que o retângulo de seleção **toca** ou intercepta.
- **Visual**: Retângulo verde semi-transparente com borda tracejada.
- **Uso**: Ideal para selecionar parágrafos inteiros ou itens múltiplos de forma rápida.

### Window Selection (Azul)

- **Direção**: Da **Direita para a Esquerda** (R → L).
- **Lógica**: Seleciona apenas os objetos que estão **totalmente contidos** no retângulo.
- **Visual**: Retângulo azul semi-transparente com borda tracejada.
- **Uso**: Ideal para isolar uma única palavra ou valor numérico dentro de uma tabela densa.

## 2. Modos de Operação (Modificadores)

O visualizador mantém um estado persistente de seleção, permitindo operações complexas:

- **Seleção Padrão (Sem Teclado)**: Limpa a seleção anterior e inicia uma nova.
- **Adição (Shift + Drag)**: Adiciona os itens da nova "caixa" à seleção já existente. O feedback visual da caixa atual fica em tom **Ciano/Verde**.
- **Subtração (Ctrl + Drag)**: Remove os itens da nova "caixa" da seleção existente. O feedback visual da caixa atual fica em tom **Vermelho suave**.

## 3. Feedback Visual de Feedback (Real-time)

- **Seleção Consolidada**: Itens já selecionados são exibidos com um preenchimento azul sólido.
- **Seleção Pendente**: Durante o arrasto, os itens que serão afetados pela operação piscam ou exibem uma borda de destaque para que o usuário saiba exatamente o resultado antes de soltar o mouse.

## 4. Evolução Futura: O Pincel (Paint-based)

Planejado para a próxima iteração:

- **Pintura Livre**: O usuário "pinta" o texto como se estivesse usando um marca-texto físico.
- **Placeholder de Marcação**: Toda seleção (mesmo efêmera) gera um placeholder na aba de "Notas".
- **Conversão Automática**: Se o usuário decidir salvar, a seleção pintura vira uma anotação definitiva no PDF.
