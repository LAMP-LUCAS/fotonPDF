# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\LABORATORIO\\fotonPDF\\src\\interfaces\\cli\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\LABORATORIO\\fotonPDF\\src', 'src')],
    hiddenimports=['plyer.platforms.win.notification', 'plyer.platforms.linux.notification', 'PyQt6', 'fitz', 'requests', 'plyer'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'matplotlib', 'pandas', 'numpy', 'PIL', 'tkinter'],
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
