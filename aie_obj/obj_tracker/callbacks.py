import re

_camel_re1 = re.compile('(.)([A-Z][a-z]+)')
_camel_re2 = re.compile('([a-z0-9])([A-Z])')


def camel2snake(name):
    s1 = re.sub(_camel_re1, r'\1_\2', name)
    s2 = re.sub(_camel_re2, r'\1_\2', s1).lower()
    return s2

class Callback():
    _order = 0

    def set_runner(self, run): self.run = run

    def __getattr__(self, k): return getattr(self.run, k)

    @property
    def name(self):
        name = re.sub(r'Callback$', '', self.__class__.__name__)
        return camel2snake(name or 'callback')

    def __call__(self, cb_name):
        f = getattr(self, cb_name, None)
        if f and f(): return True
        return False

class CancelFitException(Exception): pass
class CancelPredictionException(Exception): pass
class CancelLoopException(Exception): pass