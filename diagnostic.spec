# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['diagnostic.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('simulator_files/problems_database.json', 'simulator_files'),
        ('simulator_files/exam_stats.json', 'simulator_files'),
        ('icon.ico', '.'),
    ],
    hiddenimports=[
        # Simulator modules
        'simulator_files.custom_pdf_viewer',
        'simulator_files.pdf_viewer',
        
        # PyMuPDF (fitz) - multiple import paths
        'fitz',
        'fitz.fitz',
        'PyMuPDF',
        'PyMuPDF.fitz',
        
        # PIL/Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        
        # Tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        
        # Standard library
        'sys',
        'os',
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
    name='diagnostic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Enable console for diagnostic output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
) 