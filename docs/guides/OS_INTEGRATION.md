# 🖥️ Integração com Sistema Operacional

Este guia detalha como o **fotonPDF** se integra nativamente aos menus de contexto do Windows e Linux.

## 🪟 Windows (Registry-based)

### Visão Geral

No Windows, a integração é feita através do **Registro do Sistema** (`HKEY_CLASSES_ROOT`), modificando as associações de arquivos `.pdf`.

### Estrutura do Registro

```
HKEY_CLASSES_ROOT
└── *
    └── shell
        └── FotonPDF
            ├── (Default) = "fotonPDF"
            ├── Icon = "C:\Program Files\fotonPDF\icon.ico"
            └── command
                └── (Default) = "C:\Program Files\fotonPDF\foton.exe --file "%1""
```

### Implementação (`windows_registry.py`)

```python
import winreg
from pathlib import Path

class WindowsRegistryAdapter:
    """Gerencia integração com menu de contexto do Windows."""
    
    def register_action(self, action_name: str, command: str, icon: Path):
        """Registra uma ação no menu de contexto."""
        key_path = rf"*\shell\FotonPDF.{action_name}"
        
        # Criar chave principal
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, key_path) as key:
            winreg.SetValue(key, "", winreg.REG_SZ, f"fotonPDF - {action_name}")
            winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, str(icon))
        
        # Criar subchave de comando
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, f"{key_path}\\command") as cmd_key:
            winreg.SetValue(cmd_key, "", winreg.REG_SZ, command)
    
    def unregister_all(self):
        """Remove todas as entradas do fotonPDF."""
        try:
            winreg.DeleteKey(winreg.HKEY_CLASSES_ROOT, r"*\shell\FotonPDF")
        except FileNotFoundError:
            pass
```

### Permissões

⚠️ **Requer privilégios de administrador** para modificar `HKEY_CLASSES_ROOT`.

### Instalador

Use um script de instalação que solicita elevação:

```python
import ctypes
import sys

def is_admin():
    """Verifica se está rodando como admin."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    # Re-executar como administrador
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
```

## 🐧 Linux (Desktop Entries)

### Visão Geral

No Linux, usamos arquivos `.desktop` e integração com gerenciadores de arquivos (Nautilus, Dolphin).

### Arquivo Desktop Entry

**Localização:** `~/.local/share/applications/fotonpdf.desktop`

```ini
[Desktop Entry]
Type=Application
Name=fotonPDF
Comment=Editor rápido de PDF
Exec=foton-cli --file %f
Icon=/opt/fotonpdf/icon.png
Terminal=false
MimeType=application/pdf
Categories=Office;Utility;
```

### Scripts Nautilus/Nemo

Para adicionar ao menu de contexto do Nautilus:

**Localização:** `~/.local/share/nautilus/scripts/FotonPDF-Rotate90`

```bash
#!/bin/bash
# Rotacionar 90º no sentido horário

foton-cli --rotate 90 --file "$NAUTILUS_SCRIPT_SELECTED_FILE_PATHS"

notify-send "fotonPDF" "PDF rotacionado com sucesso!"
```

Tornar executável:

```bash
chmod +x ~/.local/share/nautilus/scripts/FotonPDF-Rotate90
```

### DBus Integration (Avançado)

Para integração mais profunda com GNOME/KDE:

```python
import dbus

def send_notification(message: str):
    """Envia notificação via DBus."""
    bus = dbus.SessionBus()
    notify = bus.get_object(
        'org.freedesktop.Notifications',
        '/org/freedesktop/Notifications'
    )
    
    notify.Notify(
        'fotonPDF',  # app_name
        0,           # replaces_id
        'pdf-icon',  # app_icon
        'Operação Concluída',
        message,
        [],          # actions
        {},          # hints
        5000         # timeout (ms)
    )
```

## 🔄 Abstração Cross-Platform

Para manter o código portável, use uma camada de abstração:

### Interface Genérica

```python
from typing import Protocol
from pathlib import Path

class SystemIntegrationPort(Protocol):
    """Porta para integração com SO."""
    
    def register_context_menu_action(
        self,
        action_id: str,
        label: str,
        command: str
    ) -> None:
        """Registra ação no menu de contexto."""
        ...
    
    def show_notification(self, message: str) -> None:
        """Exibe notificação nativa."""
        ...
```

### Factory de Implementações

```python
import sys

def get_system_integration() -> SystemIntegrationPort:
    """Retorna implementação adequada ao SO."""
    if sys.platform == "win32":
        return WindowsRegistryAdapter()
    elif sys.platform.startswith("linux"):
        return LinuxDesktopAdapter()
    else:
        raise NotImplementedError(f"SO não suportado: {sys.platform}")
```

## 📋 Checklist de Integração

### Windows

- [ ] Implementar adaptador de Registro
- [ ] Criar instalador com elevação de privilégios
- [ ] Adicionar ícones às entradas de menu
- [ ] Testar em diferentes versões do Windows (10, 11)

### Linux

- [ ] Criar arquivos `.desktop`
- [ ] Adicionar scripts para Nautilus/Dolphin/Thunar
- [ ] Configurar notificações via DBus
- [ ] Testar em diferentes DEs (GNOME, KDE, XFCE)

## 🔗 Referências

- [[../ARCHITECTURE|Arquitetura de Adaptadores]]
- [[NEW_OPERATION|Adicionar Nova Operação]]
- [[../MAP|Voltar ao Mapa]]
