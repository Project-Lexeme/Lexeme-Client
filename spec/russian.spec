# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../main.py'],
    pathex=['venv'], #/Lib/site-packages
    binaries=[('C:/Program Files/Tesseract-OCR/tesseract.exe', '.'),
    ('C:/Program Files/Tesseract-OCR/*.dll', '.'),],
    datas=[
        ('../templates', 'templates'),  # html files other than index
        ('../index.html', '.'), 
        ("../tesseract.exe",'.'),
        ('../uploads/Screenshot.png', '.'),
        ('../venv/Lib/site-packages/ru_core_news_sm', 'spacy/data/ru_core_news_sm'),
        ('../venv/Lib/site-packages/spacy_pkuseg', 'spacy_pkuseg'),
        ('../venv/Lib/site-packages/pip', 'pip'),
        ('../venv/Lib/site-packages/pytesseract', 'pytesseract'),  # Included to avoid issues with 'fetch from recent screenshot'
        ('../data/prompts/.', 'data/prompts/.'),
        ＃ TODO: add dictionaries
    ],
    hiddenimports=['pip','pip._internal','spacy','pytesseract'], # redundant but hey it works
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
    name='Project Lexeme - Russian',
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

coll = COLLECT(exe,
                a.binaries,
                a.zipfiles,
                a.datas,
                strip=False,
                upx=True,
                name='Project Lexeme - Russian',  # Same name as above
                )