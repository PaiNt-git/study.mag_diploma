# -*- mode: python ; coding: utf-8 -*-


import pymorphy2_dicts_ru
pymorph_data = pymorphy2_dicts_ru.get_path()


import time
import glob

_modules_actions = glob.glob('M:\\home\\git\\magistry2022\\study.mag_diploma\\src\\info_service\\actions\\*.py')
_modules_actions = [os.path.basename(x)[:-3] for x in _modules_actions if os.path.isfile(x)]
_modules_actions = ['info_service.actions.'+x for x in _modules_actions if not x.startswith('_')]
_modules_actions = ['info_service.actions'] + _modules_actions

_modules_events = glob.glob('M:\\home\\git\\magistry2022\\study.mag_diploma\\src\\info_service\\events\\*.py')
_modules_events = [os.path.basename(x)[:-3] for x in _modules_events if os.path.isfile(x)]
_modules_events = ['info_service.events.'+x for x in _modules_events if not x.startswith('_')]
_modules_events = ['info_service.events'] + _modules_events

_modules_initializators = glob.glob('M:\\home\\git\\magistry2022\\study.mag_diploma\\src\\info_service\\initializators\\*.py')
_modules_initializators = [os.path.basename(x)[:-3] for x in _modules_initializators if os.path.isfile(x)]
_modules_initializators = ['info_service.initializators.'+x for x in _modules_initializators if not x.startswith('_')]
_modules_initializators = ['info_service.initializators'] + _modules_initializators



_tensorflow = ['tensorflow', 'h5py', 'h5py.defs', 'h5py.utils', 'h5py.hSac', 'h5py._proxy', 'tensorflow.python._pywrap_tensorflow_internal']
# Исключим _tensorflow, пока не нужон
_tensorflow = []

_natasha = [ 'pymorphy2', 'natasha', 'razdel', 'navec', 'slovnet', 'yargy', 'ipymarkup', 'nerus', 'corus', ]



block_cipher = None


a = Analysis(['src\\info_service\\main.py'],
             pathex=['M:\\home\\git\\magistry2022\\study.mag_diploma'],
             binaries=[],
             datas=[

                (pymorph_data, 'pymorphy2_dicts_ru/data'),
                ('src/info_service/info_service.ui', '.'),
                ('src/info_service/info_service_del_instance.ui', '.'),
                ('src/info_service/info_service_new_instance.ui', '.'),
                ('src/info_service/polyfill.min.js', '.'),
                ('src/info_service/tex-mml-chtml.js', '.'),
                ('src/info_service/icon.png', '.'),

             ],
             hiddenimports=_tensorflow+_natasha+_modules_actions+_modules_events+_modules_initializators,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)




a.datas += Tree('src/info_service/_redist_root', prefix='.')


a.datas += Tree('M:/conda/miniconda-x64/envs/M-conda_study-natasha/Lib/site-packages/natasha/data', prefix='natasha/data')


a.datas += Tree('src/info_service/data_for_program', prefix='data_for_program')
a.datas += Tree('src/info_service/secrets', prefix='secrets')


a.datas += Tree('src/info_service/actions', prefix='actions')
a.datas += Tree('src/info_service/events', prefix='events')
a.datas += Tree('src/info_service/initializators', prefix='initializators')







pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='info_service',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='src/info_service/icon.ico',
          )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='info_service',
               )


