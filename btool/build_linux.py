
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
  if utils.is_x64_host():
    subprocess.run(['cargo', 'build', '--release', '--target', 'x86_64-unknown-linux-gnu'], check=True)

  elif utils.is_aarch64_host():
    subprocess.run(['cargo', 'build', '--release', '--target', 'aarch64-unknown-linux-gnu'], check=True)

  else:
    raise Exception('Unknown host CPU type!')



