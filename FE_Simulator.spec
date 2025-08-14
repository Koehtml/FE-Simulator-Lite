# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['FE_Simulator.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('simulator_files/problems_database.json', 'simulator_files'),
        ('simulator_files/exam_stats.json', 'simulator_files'),
        ('media/*.jpg', 'media'),
        ('icon.ico', '.'),
        ('test_pdf_viewer.py', '.'),
    ],
    hiddenimports=[
        'simulator_files.problem_manager',
        'simulator_files.calculator',
        'simulator_files.exam_stats',
        'simulator_files.latex_renderer',
        'simulator_files.custom_pdf_viewer',
        'simulator_files.pdf_viewer',
        'fitz',  # PyMuPDF
        'fitz.fitz',  # Alternative import path
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'json',
        'time',
        'os',
        'sys',
        're',
        'io',
        'datetime',
        'webbrowser',
        'threading',
        'traceback',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FE_Simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    distpath=r'C:\Users\tskts\OneDrive\Desktop\FE-Simulator',
) 