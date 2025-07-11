# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/images/*.png', 'resources/images'),
        ('resources/languages/*.json', 'resources/languages'),
        ('resources/images/*.ico', 'resources/images'),
        ('resources/theme/*.json', 'resources/theme'),
        ('libs/ctk_components', 'libs/ctk_components'),
        ('libs/ctk_components/src/util', 'libs/ctk_components/src/util'),
        ('libs/ctk_components/src/icons/*.png', 'libs/ctk_components/src/icons'),
        ('libs/ctk_components/src/icons/*.jpg', 'libs/ctk_components/src/icons'),
        ('libs/ctk_components/src/icons/*.gif', 'libs/ctk_components/src/icons'),
    ],
    hiddenimports=[
        'interface',
        'modules.utils',
        'modules.language_manager',
        'modules.downloader_manager',
        'modules.config',
        'modules.update_checker',
        'modules',
        'ui.about_tab',
        'ui.advanced_tab',
        'ui.download_tab',
        'ui.settings_tab',
        'ui'
        'libs',
        'libs.ctk_components',
        'libs.ctk_components.ctk_components',
        'libs.ctk_components.__init__',
        'libs.ctk_components.src',
        'libs.ctk_components.src.util',
        'libs.ctk_components.src.util.ctk_tooltip',
        'libs.ctk_components.src.util.CTkGif',
        'libs.ctk_components.src.util.py_win_style',
        'libs.ctk_components.src.util.window_position',
        'CTkMessagebox',
        'CTkToolTip'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

splash = Splash(
    'resources/images/EasyTuber_Banner.png',
    binaries=a.binaries,
    datas=a.datas,
    always_on_top=True,
    time_to_display=1.0
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    splash,
    splash.binaries,
    [],
    name='EasyTuber',
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
    icon='resources/images/icon.ico',
    version='version_info.txt',
)
