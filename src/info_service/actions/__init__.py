import sys
import os
import glob

from os.path import dirname, basename, isfile
from inspect import isclass

PY_VERSION = sys.version_info
IS_PY27 = PY_VERSION < (3, 0)
level = -1 if IS_PY27 else 1


_modules = glob.glob(dirname(__file__) + "/*.py")
_modules = [basename(x)[:-3] for x in _modules if isfile(x)]
_modules = [x for x in _modules if not x.startswith('_')]

__all__ = _modules

ACTION_PROVIDERS = {}

for _module_name in _modules:
    is_callable = False
    _modul = __import__(str('{}').format(_module_name), globals(), locals(), [str(_module_name), ], level)
    _provider = getattr(_modul, str('main'), None)
    if not _provider:
        _provider = getattr(_modul, str(_module_name), None)

    if _provider:
        mod_module = _modul.__name__
        prov_module = _provider.__module__

        is_callable = hasattr(_provider, '__call__')

        if is_callable and _provider and mod_module == prov_module:
            ACTION_PROVIDERS[_module_name] = _provider
            setattr(sys.modules[__name__], _module_name, _provider)
