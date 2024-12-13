# -*- mode: python ; coding: utf-8 -*-
import os

os.environ['LEXEME_LANGUAGE'] = "Persian"

a = Analysis( # type: ignore
    ['../main.py'],
    pathex=['venv'], #/Lib/site-packages
    binaries=[],
    datas=[
        ("C:/Users/afggo/Downloads/tesseract-ocr-w64-setup-5.4.0.20240606.exe",'./tesseract_installer'),
        ('../templates', 'templates'),  # html files other than index
        ('../index.html', '.'), 
        ('../uploads/Screenshot.png', '.'),
        ('../bootstrapped_models/fa_boot_sm', 'spacy/data/fa_boot_sm'),
        ('../venv/Lib/site-packages/spacy_pkuseg', 'spacy_pkuseg'),
        ('../venv/Lib/site-packages/pytesseract', 'pytesseract'),  # Included to avoid issues with 'fetch from recent screenshot'
        ('../data/prompts/.', 'data/prompts/.'),
        ('../data/dictionaries/fa_dictionary.csv', 'data/dictionaries/.'),
    ],
    hiddenimports=['spacy','pytesseract'], # redundant but hey it works
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure) # type: ignore

exe = EXE( # type: ignore
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Project Lexeme - Persian',
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
    icon=['../Lexemus.ico'],
)

coll = COLLECT(exe, # type: ignore
                a.binaries,
                a.zipfiles,
                a.datas,
                strip=False,
                upx=True,
                name='Project Lexeme - Persian',  # Same name as above
                )