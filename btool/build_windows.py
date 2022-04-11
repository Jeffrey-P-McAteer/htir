
import os
import sys
import subprocess
import shutil
import traceback
import platform
import threading
import select
import time
import multiprocessing
import inspect

from . import icon_gen
from . import utils

def build_all():
  utils.del_env_vars('CC', 'CXX')
  utils.maybe_set_env_vals_if_bin_exists(
    ('CC', ['x86_64-w64-mingw32-gcc']),
    ('CXX', ['x86_64-w64-mingw32-g++'])
  )

  if utils.is_x64_host():
    subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-pc-windows-msvc'], check=True)

  elif utils.is_aarch64_host():
    subprocess.run(['cargo', 'build', '--release', '--target', 'aarch64-pc-windows-msvc'], check=True)

  else:
    raise Exception('Unknown host CPU type!')

