# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect data files for transformers and sentence-transformers
transformers_data = collect_data_files('transformers')
sentence_transformers_data = collect_data_files('sentence_transformers')

# Collect all submodules for AI libraries
transformers_modules = collect_submodules('transformers')
sentence_transformers_modules = collect_submodules('sentence_transformers')
torch_modules = collect_submodules('torch')

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include data files
        *transformers_data,
        *sentence_transformers_data,
        # Include assets
        ('assets/zeus_icon.ico', 'assets'),
        ('assets/zeus_icon.png', 'assets'),
        # Include data directory
        ('data', 'data'),
    ],
    hiddenimports=[
        # Core modules
        'ui.main_window',
        'ui.chat_interface',
        'ui.document_viewer',
        'ui.keyboard_shortcuts',
        'ui.responsive_layout',
        'ui.styles',
        'core.ai_engine',
        'core.background_processor',
        'core.context_manager',
        'core.document_processor',
        'core.error_handler',
        'core.memory_optimizer',
        'core.performance_monitor',
        'core.persistence',
        'games.battleship',
        'games.connect_4',
        'games.game_manager',
        'games.tic_tac_toe',
        'models.data_models',
        # AI library modules
        *transformers_modules,
        *sentence_transformers_modules,
        *torch_modules,
        # Additional dependencies
        'PIL',
        'PIL._tkinter_finder',
        'tkinter',
        'tkinter.ttk',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'PyPDF2',
        'docx',
        'numpy',
        'json',
        'threading',
        'queue',
        'datetime',
        'pathlib',
        'logging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'matplotlib',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'notebook',
        'pytest',
        'test',
        'tests',
        'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Zeus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for windowed application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/zeus_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Zeus',
)