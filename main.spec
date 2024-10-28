# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['venv/Lib/site-packages'],
    binaries=[],
    datas=[('venv/Lib/site-packages/zh_core_web_sm', 'spacy/data/zh_core_web_sm'),
    ('venv/Lib/site-packages/spacy_pkuseg', 'spacy_pkuseg'),
    ('venv/Lib/site-packages/pip', 'pip'),
    ('venv/Lib/site-packages/pytesseract','pytesseract'),
    ('templates', 'templates'),
    ('index.html', '.' ),
    ("C:/Program Files/Tesseract-OCR/tesseract.exe",'.'),
    ('uploads/Screenshot.png','.'),
    ],
    hiddenimports=['pip','pip._internal','spacy','pytesseract'],
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
    name='Project Lexeme',
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
    icon=['Lexemus.ico'],
)
