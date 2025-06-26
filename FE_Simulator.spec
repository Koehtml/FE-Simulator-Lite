# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['FE_Simulator.py'],
    pathex=[],
    binaries=[],
    datas=[
    ('simulator_files/problems_database.json', 'simulator_files'),
    ('simulator_files/exam_stats.json', 'simulator_files'),
    ('media', 'media'),
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
    [],
    exclude_binaries=True,
    name='FE_Simulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FE_Simulator',
)
