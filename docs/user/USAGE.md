# 📖 Guia de Utilização

O **fotonPDF** foi desenhado para ser simples e produtivo. Aqui estão as principais formas de interagir com ele.

## 🖥️ Usando o Visualizador (Interface Gráfica)

### Abertura de Arquivo

- **Arrastar e Soltar:** Basta arrastar qualquer arquivo PDF para dentro da janela do fotonPDF.
- **Botão Abrir:** Use o botão na barra de ferramentas superior.
- **Clique Direito:** No Explorador de Arquivos, use "Abrir com fotonPDF".

### Navegação

- **Barra Lateral:** Use as miniaturas à esquerda para saltar rapidamente entre as páginas.
- **Scroll Infinito:** Role o documento livremente; o carregamento é automático e instantâneo.

### Ferramentas de Edição Rápida

- **Extrair Páginas:** Selecione uma ou mais páginas na barra lateral (segurando `Ctrl` para múltiplas) e clique em **"Extrair Selecionadas"**.
- **Exportar Imagem:** Salve páginas específicas como imagens PNG de alta qualidade clicando em **"Exportar como Imagem"**.

---

## ⌨️ Atalhos de Teclado (Produtividade)

| Tecla | Ação |
| --- | --- |
| `J` | Rolar para Baixo |
| `K` | Rolar para Cima |
| `Esc` | Fechar Aplicativo |
| `Ctrl + Scroll` | Zoom (Em breve) |

---

## 💻 Via Linha de Comando (CLI)

Para usuários avançados:

- `foton view arquivo.pdf` - Abre o visualizador.
- `foton rotate arquivo.pdf -d 90` - Gira o PDF sem abrir a interface.
- `foton merge arq1.pdf arq2.pdf -o final.pdf` - Une arquivos.
