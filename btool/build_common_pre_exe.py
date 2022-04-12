
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
  create_misc_directories_we_assume_exist()

  create_cargo_config_if_necessary()
  
  # Uses a 3rd-party renderer & python code to render high-quality .png and generate a .icns file under ./target/
  icon_gen.gen_icons(os.path.abspath(os.path.join('htir_app_icon.pov')))



def create_misc_directories_we_assume_exist():
  utils.cd_up_to_repo_root()
  
  os.makedirs('target', exist_ok=True)

def create_cargo_config_if_necessary():
  if utils.is_linux_host():
    os.makedirs('.cargo', exist_ok=True)
    with open(os.path.join('.cargo', 'config'), 'w+') as fd:
      fd.write('''
# We assume the following is installed: https://github.com/tpoechtrager/osxcross
[target.x86_64-apple-darwin]
linker = "o64-clang"
ar = "x86_64-apple-darwin20.4-ar"

# We assume the following is installed: https://www.mingw-w64.org/
[target.x86_64-pc-windows-gnu]
linker = "x86_64-w64-mingw32-gcc"
ar = "x86_64-w64-mingw32-ar"
'''.strip()+'\n')


