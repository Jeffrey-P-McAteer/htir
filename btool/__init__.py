
# This python module provides a higher-level control over
# the `cargo` build that supports building the library (under ./src/lib.rs),
# multiple binaries (./src/{server,client}.rs), and running tests
# using the built artifacts.

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

from . import utils

from . import build_common_pre_exe
from . import build_linux
from . import build_macos
from . import build_windows
from . import build_common_post_exe

def main(args=sys.argv):

  utils.cd_up_to_repo_root()

  build_common_pre_exe.build_all()

  # Arguments passed to btool will be forwarded to cargo
  utils.set_addtl_cargo_args( sys.argv[1:] )

  if utils.can_compile_linux():
    print('Compiling all Linux targets...')
    build_linux.build_all()

  if utils.can_compile_macos():
    print('Compiling all MacOS targets...')
    build_macos.build_all()

  if utils.can_compile_windows():
    print('Compiling all Windows targets...')
    build_windows.build_all()

  build_common_post_exe.build_all()


