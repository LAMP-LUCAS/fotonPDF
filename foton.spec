# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('C:\\LABORATORIO\\fotonPDF\\src', 'src'), ('C:\\LABORATORIO\\fotonPDF\\docs\\brand', 'docs/brand')]
binaries = []
hiddenimports = ['plyer.platforms.win.notification', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.sip', 'litellm', 'instructor', 'fitz', 'requests', 'plyer', 'click']
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('litellm')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('instructor')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


# ─── Analysis (compartilhada entre os dois executáveis) ───────────────────
a = Analysis(
    ['C:\\LABORATORIO\\fotonPDF\\src\\interfaces\\cli\\main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'matplotlib', 'pandas', 'numpy', 'PIL', 'tkinter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

# ─── EXE 1: foton.exe (GUI — sem console, para double-click) ─────────────
exe_gui = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='foton',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\LABORATORIO\\fotonPDF\\docs\\brand\\logo.ico'],
)

# ─── EXE 2: foton-cli.exe (Console — para terminal e menu de contexto) ───
exe_cli = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='foton-cli',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\LABORATORIO\\fotonPDF\\docs\\brand\\logo.ico'],
)

# ─── COLLECT: ambos os executáveis na mesma pasta dist/foton ──────────────
coll = COLLECT(
    exe_gui,
    exe_cli,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='foton',
)

