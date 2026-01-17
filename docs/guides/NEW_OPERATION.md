# ➕ Como Adicionar Nova Operação PDF

Este guia detalha o processo de adicionar uma nova operação de PDF ao **fotonPDF**, seguindo os princípios da arquitetura hexagonal.

## 🎯 Exemplo: Adicionar "Compressão de PDF"

Vamos usar a funcionalidade de **compressão** como exemplo prático.

## 📋 Passo a Passo

### 1️⃣ Definir a Porta (Interface)

Crie a interface no domínio que define o contrato:

**Arquivo:** `src/domain/ports/pdf_compressor_port.py`

```python
from typing import Protocol
from pathlib import Path
from dataclasses import dataclass

@dataclass
class CompressionConfig:
    """Configuração de compressão."""
    quality: int  # 0-100
    optimize_images: bool = True
    remove_duplicates: bool = True

class PDFCompressorPort(Protocol):
    """Porta para compressão de PDFs."""
    
    def compress(
        self, 
        input_path: Path, 
        output_path: Path,
        config: CompressionConfig
    ) -> None:
        """Comprime um PDF."""
        ...
```

### 2️⃣ Criar o Adapter (Implementação)

Implemente a porta usando uma biblioteca específica:

**Arquivo:** `src/infrastructure/adapters/pdf_libs/pymupdf_compressor.py`

```python
import fitz
from pathlib import Path
from src.domain.ports.pdf_compressor_port import PDFCompressorPort, CompressionConfig

class PyMuPDFCompressor(PDFCompressorPort):
    """Compressor usando PyMuPDF."""
    
    def compress(
        self, 
        input_path: Path, 
        output_path: Path,
        config: CompressionConfig
    ) -> None:
        doc = fitz.open(str(input_path))
        
        # Aplicar compressão
        doc.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True
        )
        
        doc.close()
```

### 3️⃣ Criar o Caso de Uso

Orquestre a operação na camada de aplicação:

**Arquivo:** `src/application/use_cases/compress_pdf.py`

```python
from pathlib import Path
from src.domain.ports.pdf_compressor_port import PDFCompressorPort, CompressionConfig

class CompressPDFUseCase:
    """Caso de uso: Comprimir PDF."""
    
    def __init__(self, compressor: PDFCompressorPort):
        self.compressor = compressor
    
    def execute(self, pdf_path: Path, quality: int = 75) -> Path:
        """Executa a compressão."""
        output_path = pdf_path.with_stem(f"{pdf_path.stem}_compressed")
        
        config = CompressionConfig(quality=quality)
        self.compressor.compress(pdf_path, output_path, config)
        
        return output_path
```

### 4️⃣ Registrar no Menu de Contexto

Adicione a entrada no sistema de integração:

**Arquivo:** `src/interfaces/context_menu/windows_menu.py`

```python
def register_compress_action():
    """Registra ação de compressão no menu."""
    registry_key = r"*\shell\FotonPDF.Compress"
    
    # Registrar entrada no Registry
    # (implementação específica)
```

### 5️⃣ Criar Interface CLI

Exponha via linha de comando:

**Arquivo:** `src/interfaces/cli/commands.py`

```python
@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--quality', default=75, help='Qualidade (0-100)')
def compress(file, quality):
    """Comprime um arquivo PDF."""
    use_case = CompressPDFUseCase(PyMuPDFCompressor())
    output = use_case.execute(Path(file), quality)
    click.echo(f"PDF comprimido: {output}")
```

### 6️⃣ Escrever Testes

**Arquivo:** `tests/unit/test_compress_pdf.py`

```python
from src.application.use_cases.compress_pdf import CompressPDFUseCase
from tests.mocks import MockCompressor

def test_compress_pdf():
    """Testa compressão básica."""
    use_case = CompressPDFUseCase(MockCompressor())
    result = use_case.execute(Path("test.pdf"))
    
    assert result.exists()
    assert result.stem.endswith("_compressed")
```

## ✅ Checklist de Conclusão

- [ ] Porta definida em `domain/ports/`
- [ ] Adapter implementado em `infrastructure/adapters/`
- [ ] Caso de uso criado em `application/use_cases/`
- [ ] Integração com menu de contexto (Windows/Linux)
- [ ] Comando CLI adicionado
- [ ] Testes unitários escritos
- [ ] Documentação atualizada

## 🔗 Referências

- [[../ARCHITECTURE|Arquitetura Hexagonal]]
- [[../DEVELOPMENT|Padrões de Testes]]
- [[../MAP|Voltar ao Mapa]]
