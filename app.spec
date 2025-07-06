# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

project_path = os.path.abspath('.')

a = Analysis(
    ['app.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        (os.path.join(project_path, 'templates', '*.html'), 'templates'),
        (os.path.join(project_path, 'static'), 'static'),
        (os.path.join(project_path, 'database.db'), '.')  # si usas base de datos SQLite
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='app',
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
