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
        # Simulator modules
        'simulator_files.problem_manager',
        'simulator_files.calculator',
        'simulator_files.exam_stats',
        'simulator_files.latex_renderer',
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
        'PIL.ImageDraw',
        'PIL.ImageFont',
        
        # Tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        
        # Standard library
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
        'pathlib',
        'shutil',
        'tempfile',
        'urllib',
        'urllib.parse',
        'urllib.request',
        
        # Additional dependencies that might be needed
        'collections',
        'itertools',
        'functools',
        'weakref',
        'copy',
        'pickle',
        'base64',
        'hashlib',
        'zlib',
        'struct',
        'array',
        'math',
        'random',
        'statistics',
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
) 