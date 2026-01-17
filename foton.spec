# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['plyer.platforms.win.notification', 'plyer.platforms.linux.notification', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.sip', 'fitz', 'fitz.fitz', 'pymupdf', 'requests', 'plyer', 'click']
hiddenimports += collect_submodules('PyQt6')
hiddenimports += collect_submodules('fitz')


a = Analysis(
    ['C:\\LABORATORIO\\fotonPDF\\src\\interfaces\\cli\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\LABORATORIO\\fotonPDF\\src', 'src')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'matplotlib', 'pandas', 'numpy', 'PIL', 'tkinter', 'scipy', 'cv2'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='foton',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
