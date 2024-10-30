# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=['venv/Lib/site-packages'],
    binaries=[],
    datas=[
        ('templates', 'templates'),  # html files other than index
        ('index.html', '.'), 
        ("C:/Program Files/Tesseract-OCR/tesseract.exe", '.'),  # Adjust as needed
        ('uploads/Screenshot.png', '.'),
        ('venv/Lib/site-packages/zh_core_web_sm', 'spacy/data/zh_core_web_sm'),
        ('venv/Lib/site-packages/spacy_pkuseg', 'spacy_pkuseg'),
        ('venv/Lib/site-packages/pip', 'pip'),
        ('venv/Lib/site-packages/pytesseract', 'pytesseract'),  # Included to avoid issues with 'fetch from recent screenshot'
    ],
    hiddenimports=['pip','pip._internal','spacy','pytesseract'], # redundant but hey it works
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,

)

### this section is not working but haven't dug into why, instead hand-jammed module references above in a.datas
# add modules here as they get missed in compile
#modules = [
#    ('venv/Lib/site-packages/zh_core_web_sm', 'spacy/data/zh_core_web_sm'),
#    ('venv/Lib/site-packages/spacy_pkuseg', 'spacy_pkuseg'),
#    ('venv/Lib/site-packages/pip', 'pip'),
#    ('venv/Lib/site-packages/pytesseract', 'pytesseract'),
#]

#a.datas += modules

# add prompt csv here as they get added to project
#prompt_csvs = [
#    ('prompts/beginner_scaffolded_prompts.csv', '.'),
#    ('prompts/intermediate_subtitle_prompts.csv', '.'),
#]

#a.datas += prompt_csvs
###

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
    icon=['Lexemus.ico'],
)
