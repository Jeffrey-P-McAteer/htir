
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
    ('CXX', ['x86_64-w64-mingw32-g++']),
  )

  if utils.is_x64_host():
    if utils.is_windows_host():
      # Windows host are assumed to have MSVC available
      subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-pc-windows-msvc'] + utils.get_addtl_cargo_args(), check=True)
      
    else:
      # Everyone else is assumed to use gnu tools
      subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-pc-windows-gnu'] + utils.get_addtl_cargo_args(), check=True)
      
  elif utils.is_aarch64_host():
    if utils.is_windows_host():
      subprocess.run(['cargo', 'build', '--release', '--target', 'aarch64-pc-windows-msvc'] + utils.get_addtl_cargo_args(), check=True)

    else:
      #subprocess.run(['cargo', 'build', '--release', '--target', 'aarch64-pc-windows-gnu'] + utils.get_addtl_cargo_args(), check=True)
      raise Exception('GNU does not publish anything for the aarch64-pc-windows-gnu target triple!')


  else:
    raise Exception('Unknown host CPU type!')


if __name__ == '__main__':
  build_all()

