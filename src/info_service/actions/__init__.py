import os
import sys
import glob

from importlib import import_module
from inspect import ismodule, isclass, isfunction


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


DYN_FUNC_PROVIDERS = AttrDict()

_modules = glob.glob(os.path.join(os.path.dirname(__file__)) + "/*.py")
_modules = [os.path.basename(x)[:-3] for x in _modules if os.path.isfile(x)]
_modules = [x for x in _modules if not x.startswith('_')]


for _module_name in _modules:
    _modul = __import__(_module_name, globals(), locals(), [_module_name, ], 1)
    _provider = getattr(_modul, str('main'), None)
    if not _provider:
        _provider = getattr(_modul, str(_module_name), None)

    if isfunction(_provider):
        DYN_FUNC_PROVIDERS[_module_name] = _provider
        setattr(sys.modules[__name__], _module_name, _provider)
