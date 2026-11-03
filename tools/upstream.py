"""Load the pinned upstream engine read-only, with a Windows epoch adapter."""
from datetime import datetime, timedelta, timezone
import importlib
from pathlib import Path
import subprocess
import sys
import types

COMMIT='d6a2397fc31517147ddd09f58e0d153bc8cf0588'


def load(source, verify=True):
    source=Path(source).resolve()
    if verify:
        rev=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        if rev!=COMMIT:
            raise ValueError(f'Expected source commit {COMMIT}, got {rev}')
        changes=subprocess.check_output(['git','-C',str(source),'status','--porcelain','--untracked-files=no','--','.'],text=True).strip()
        if changes:
            raise ValueError('Source has tracked modifications; use an unchanged pinned checkout')
    sys.path.insert(0,str(source))
    p=importlib.import_module('purplelab')
    if Path(p.__file__).resolve()!=source/'purplelab.py':
        raise ValueError('Another purplelab module is already loaded')
    # Upstream modules compute query constants with Scenario(anchor=0).
    # Windows time.gmtime rejects their negative dates. Keep all timestamps.
    real_time=p.time
    attrs={k:getattr(real_time,k) for k in dir(real_time) if not k.startswith('__')}
    attrs['gmtime']=lambda seconds=None: (datetime.now(timezone.utc) if seconds is None else datetime(1970,1,1,tzinfo=timezone.utc)+timedelta(seconds=seconds)).utctimetuple()
    p.time=types.SimpleNamespace(**attrs)
    return p
