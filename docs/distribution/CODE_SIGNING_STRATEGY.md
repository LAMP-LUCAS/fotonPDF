# 🔏 Estratégia de Assinatura de Código (Code Signing)

Este documento detalha a estratégia para garantir a integridade do **fotonPDF** e reduzir os alertas de segurança do Windows (SmartScreen).

---

## 1. Abordagem Atual: Self-Signed (Preparação)

Como medida inicial e de custo zero, utilizamos certificados "Auto-Assinados".

### Vantagens

* **Identidade Técnica**: O executável possui um "Dono" definido nos metadados.
* **Integridade**: Garante que o arquivo não foi alterado por terceiros após o build.
* **Infraestrutura**: O pipeline de build já fica preparado para receber um certificado profissional no futuro.

### Limitações

* O Windows ainda exibirá o alerta "Editor Desconhecido" na primeira execução, pois o certificado não está em uma "Raiz de Confiança" pública.

---

## 2. Abordagem Gratuita/Comunitária (Sigstore)

Uma alternativa moderna e gratuita é o **[Sigstore](https://www.sigstore.dev/)**.

* Utiliza identidades OpenID (Google, GitHub) para assinar artefatos.
* Focado em transparência e auditoria.
* **Status**: Em avaliação para integração com ferramentas de automação (Actions).

---

## 3. Caminho para Certificação Profissional (Microsoft/CA)

Para eliminar totalmente os avisos do Windows SmartScreen, o projeto deve obter um certificado de uma Autoridade Certificadora (CA) reconhecida.

### Opções de Certificado

1. **Standard Code Signing**: Remove o aviso de "Editor Desconhecido". Requer validação da identidade do desenvolvedor.
2. **EV (Extended Validation) Code Signing**: Garante reputação imediata no SmartScreen. Requer empresa aberta e validação rigorosa.

### Fornecedores Recomendados (Baixo Custo)

* **Certum**: Conhecido por ser amigável para desenvolvedores Open Source (Open Source Code Signing).
* **SignPath.io**: Oferece serviços de assinatura gratuita para projetos Open Source selecionados.

---

## 4. Implementação Técnica Futura

O processo de assinatura deve ser integrado ao `scripts/build_exe.py` utilizando a ferramenta `signtool.exe` (parte do Windows SDK):

```powershell
# Exemplo de comando de assinatura
signtool sign /f "caminho/do/certificado.pfx" /p "senha" /tr http://timestamp.digicert.com /td sha256 /fd sha256 "dist/foton/foton.exe"
```

### Automação via GitHub Actions

Segredos a serem configurados no repositório:

* `CERTIFICATE_BASE64`: O arquivo .pfx em base64.
* `CERTIFICATE_PASSWORD`: A senha do certificado.

---
*Documento preparado como guia de evolução do fotonPDF.*
