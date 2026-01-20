# 🎨 Entrega: Identidade Visual e Branding fotonPDF

Concluí o desenvolvimento da nova identidade visual premium para o **fotonPDF**, focando no conceito de **"Velocidade da Luz e Clareza"**.

## 💎 O Novo Logotipo

O logotipo foi desenhado em **SVG Nativo** para garantir nitidez infinita em qualquer resolução.

* **Conceito**: Um rastro de luz (fóton) em gradiente solar que atravessa e ilumina um documento translúcido.
* **Arquivos**:
  * `docs/brand/logo.svg`: Vetor original para UI e Web.
  * `docs/brand/logo.ico`: Ícone do Windows (256px) gerado via script para o executável.

## 🌈 Padrões Estéticos

* **Cores**: Solar Gold (`#FFC107`) e Deep Space (`#0F172A`).
* **Tipografia**: Recomendação de uso da família `Inter` para clareza técnica.
* **Manual**: Consulte `docs/brand/VISUAL_IDENTITY.md` para detalhes de implementação.

## 🖥️ Implementação na GUI

A Interface Gráfica agora reflete essa nova identidade:

* **Stylesheet (QSS)**: Toda a aplicação PyQt6 foi estilizada com as cores "Deep Space" no fundo e acentos em "Solar Gold".
* **Placeholder Premium**: Ao abrir o app sem arquivos, o usuário agora vê o logotipo e uma mensagem de boas-vindas sofisticada.
* **Ícone da Janela**: O logotipo agora aparece na barra de título e na barra de tarefas.

## 📦 Automação de Build

* **Executável**: O `foton.exe` agora é compilado automaticamente com o novo ícone.
* **Instalador**: O instalador do Inno Setup também utiliza o ícone oficial, passando uma imagem de confiança profissional desde o primeiro clique.

---

### Como visualizar

1. Abra o arquivo `docs/brand/logo.svg` em seu navegador para ver o design.
2. Execute `python -m src.interfaces.gui.app` para ver a nova interface estilizada.
