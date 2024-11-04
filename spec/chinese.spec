# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['../main.py'], # because each .spec is in a subfolder, use relative paths to go back to project root dir
    pathex=['venv'], #/Lib/site-packages
    binaries=[],
    datas=[
        ('../templates', 'templates'),  # html files other than index
        ('../index.html', '.'), 
        #("C:/Program Files/Tesseract-OCR/tesseract.exe", '.'),  # deprecated
        ("../tesseract.exe",'.'),
        ('../uploads/Screenshot.png', '.'),
        ('../venv/Lib/site-packages/zh_core_web_sm', 'spacy/data/zh_core_web_sm'),
        ('../venv/Lib/site-packages/spacy_pkuseg', 'spacy_pkuseg'),
        ('../venv/Lib/site-packages/pip', 'pip'),
        ('../venv/Lib/site-packages/pytesseract', 'pytesseract'),  # Included to avoid issues with 'fetch from recent screenshot'
        ('../data/prompts/beginner_scaffolded_prompts.csv', 'data/prompts/.'),
        ('../data/prompts/intermediate_subtitle_prompts.csv', 'data/prompts/.'),
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
    name='Project Lexeme - Chinese',
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
                name='Project Lexeme - Chinese',  # Same name as above
                )