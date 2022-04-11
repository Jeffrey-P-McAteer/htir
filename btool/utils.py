
import importlib
import os
import sys
import subprocess
import shutil
import time
import platform

# Utility method to wrap imports with a call to pip to install first.
# > "100% idiot-proof!" -- guy on street selling rusty dependency chains.
def import_maybe_installing_with_pip(import_name, pkg_name=None):
  if pkg_name is None:
    pkg_name = import_name # 90% of all python packages share their name with their module
  pkg_spec = importlib.util.find_spec(import_name)
  install_cmd = []
  if pkg_spec is None:
    # package missing, install via pip to user prefix!
    print('Attempting to install module {} (package {}) with pip...'.format(import_name, pkg_name))
    install_cmd = [sys.executable, '-m', 'pip', 'install', '--user', pkg_name]
    subprocess.run(install_cmd, check=False)
  pkg_spec = importlib.util.find_spec(import_name)
  if pkg_spec is None:
    raise Exception('Cannot find module {}, attempted to install {} via pip: {}'.format(import_name, pkg_name, ' '.join(install_cmd) ))
  
  return importlib.import_module(import_name)

def create_misc_directories_we_assume_exist():
  cd_up_to_repo_root()
  if not os.path.exists('target'):
    os.makedirs('target')


def cd_up_to_repo_root():
  # Normalize getting to repo root from any sub-directory
  for _ in range(0, 12):
    if not (os.path.exists('.gitignore') and os.path.exists('readme.md')):
      os.chdir('..')
  

def is_windows_host():
  return os.name == 'nt'

def is_macos_host():
  return 'darwin' in platform.system().lower()

def is_linux_host():
  return 'linux' in platform.system().lower()


def can_compile_windows():
  return is_windows_host() or (is_linux_host() and shutil.which('x86_64-w64-mingw32-cc') is not None)

def can_compile_macos():
  # x86_64-apple-darwin15-clang comes from https://wapl.es/rust/2019/02/17/rust-cross-compile-linux-to-macos.html
  return is_macos_host() or (is_linux_host() and (shutil.which('x86_64-apple-darwin15-clang') is not None or shutil.which('x86_64-apple-darwin14-clang') is not None))

def can_compile_linux():
  return is_linux_host()


def is_x64_host():
  return (
    'x86_64' in platform.processor().lower() or
    'x86_64' in platform.machine().lower() or
    'amd64' in platform.processor().lower() or
    'amd64' in platform.machine().lower()
  )

def is_aarch64_host():
  return (
    'aarch64' in platform.processor().lower() or
    'aarch64' in platform.machine().lower()
  )





