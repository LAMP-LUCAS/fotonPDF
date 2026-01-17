# 🔌 Sistema de Plugins

O **fotonPDF** possui um sistema de plugins extensível que permite adicionar novas funcionalidades sem modificar o código-fonte principal.

## 🏗️ Arquitetura de Plugins

Os plugins seguem uma arquitetura baseada em **eventos** e **registros**. Eles podem:

- Adicionar novas operações ao menu de contexto.
- Registrar novos conversores de formato.
- Escutar eventos do sistema (PDF processado, erro, etc.).
- Adicionar painéis à interface gráfica.

## 📦 Estrutura de um Plugin

Cada plugin é uma pasta com a seguinte estrutura:

```
meu-plugin/
├── plugin.json         # Manifesto (metadados)
├── __init__.py         # Entry point
├── operations.py       # Lógica do plugin
├── assets/             # Ícones, traduções
│   └── icon.png
└── README.md           # Documentação
```

## 📄 Manifesto (`plugin.json`)

```json
{
  "name": "pdf-watermark",
  "version": "1.0.0",
  "author": "Seu Nome",
  "description": "Adiciona marca d'água em PDFs",
  "permissions": [
    "pdf.read",
    "pdf.write",
    "filesystem.temp"
  ],
  "entry_point": "operations.WatermarkPlugin"
}
```

## 🐍 Implementação

### Entry Point (`__init__.py`)

```python
from src.domain.plugin import PDFPlugin

class WatermarkPlugin(PDFPlugin):
    """Plugin de marca d'água."""
    
    name = "pdf-watermark"
    version = "1.0.0"
    
    def __init__(self, container, event_bus):
        self.container = container
        self.event_bus = event_bus
    
    def on_load(self):
        """Chamado quando o plugin é carregado."""
        self.register_actions()
        self.subscribe_events()
    
    def register_actions(self):
        """Registra novas ações no menu."""
        registry = self.container.resolve("ActionRegistry")
        
        registry.add_action(
            name="add_watermark",
            label="Adicionar Marca D'água",
            callback=self.add_watermark,
            icon="assets/icon.png"
        )
    
    def subscribe_events(self):
        """Escuta eventos do sistema."""
        self.event_bus.subscribe("PDFProcessed", self.on_pdf_processed)
    
    def add_watermark(self, context):
        """Adiciona marca d'água ao PDF."""
        pdf_path = context.pdf_path
        # Lógica de watermark aqui
        pass
    
    def on_pdf_processed(self, event):
        """Chamado quando um PDF é processado."""
        print(f"PDF processado: {event.pdf_path}")
```

## 🔐 Sistema de Permissões

Plugins declaram permissões necessárias no `plugin.json`:

- `pdf.read`: Ler PDFs.
- `pdf.write`: Modificar PDFs.
- `filesystem.temp`: Criar arquivos temporários.
- `network.http`: Fazer requisições HTTP.
- `ui.modal`: Exibir diálogos.

O sistema negará acesso a operações não autorizadas.

## 📚 API Disponível

### Registros

```python
# Adicionar ação ao menu
registry.add_action(name, label, callback, icon)

# Adicionar conversor
converter_registry.register(from_format, to_format, converter_fn)

# Adicionar automação
automation_registry.register_trigger(trigger_type, handler)
```

### Event Bus

```python
# Publicar evento
event_bus.publish(PDFProcessedEvent(pdf_path, operation))

# Assinar evento
event_bus.subscribe(EventType, callback_function)
```

## 🧪 Testando Plugins

Crie testes isolados para seu plugin:

```python
def test_watermark_plugin():
    """Testa plugin de marca d'água."""
    plugin = WatermarkPlugin(mock_container, mock_event_bus)
    plugin.on_load()
    
    # Simular chamada
    context = PluginContext(pdf_path=Path("test.pdf"))
    plugin.add_watermark(context)
    
    assert Path("test_watermarked.pdf").exists()
```

## 📦 Publicando no Marketplace

1. Teste localmente com `foton-cli plugin install ./meu-plugin`.
2. Crie repositório no GitHub.
3. Submeta para curadoria em `plugins.fotonpdf.org`.

## 🔗 Referências

- [[../ARCHITECTURE|Sistema de Eventos]]
- [[NEW_OPERATION|Como Criar Operações]]
- [[../MAP|Voltar ao Mapa]]
