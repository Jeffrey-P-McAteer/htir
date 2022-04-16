
import importlib
import os
import sys
import subprocess
import shutil
import time
import platform
import json

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
  return is_windows_host() or (
    is_linux_host() and
    shutil.which('x86_64-w64-mingw32-cc') is not None
  )

def can_compile_macos():
  # x86_64-apple-darwin15-clang comes from https://wapl.es/rust/2019/02/17/rust-cross-compile-linux-to-macos.html
  return is_macos_host() or (
    is_linux_host() and (
      shutil.which('x86_64-apple-darwin15-clang') is not None or # Older libs for 10.x stuff
      shutil.which('x86_64-apple-darwin14-clang') is not None or
      shutil.which('o64-clang') is not None # newer osxcross compiler
    )
  )

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


def maybe_set_env_vals_if_bin_exists(*args):
  for env_var, bins in list(args):
    b_to_set = None
    for b in bins:
      if shutil.which(b):
        b_to_set = shutil.which(b)

    if b_to_set is not None:
      print('{}={}'.format(env_var, b_to_set))
      os.environ[env_var] = b_to_set

def del_env_vars(*args):
  for env_var in list(args):
    if env_var in os.environ:
      del os.environ[env_var]


def get_first_existing(*files):
  for f in list(files):
    if os.path.exists(f):
      return f
  return None

def get_most_recent_mtimed(*files):
  
  if len(files) < 1:
    return None

  file_mtime_dict = {}
  for f in list(files):
    if os.path.exists(f):
      file_mtime_dict[f] = os.path.getmtime(f)
  
  most_recent_f = files[0]
  for f in list(files):
    if f in file_mtime_dict:
      if file_mtime_dict[f] > file_mtime_dict[most_recent_f]:
        most_recent_f = f

  return most_recent_f

# Thanks https://stackoverflow.com/a/1392549/9252743
def directory_size_bytes(directory):
  total_size = 0
  for dirpath, dirnames, filenames in os.walk(directory):
    for f in filenames:
      file_path = os.path.join(dirpath, f)
      # skip if it is symbolic link
      if not os.path.islink(file_path):
        total_size += os.path.getsize(file_path)

  return total_size

# Runs given command, printing errors if return code != 0
def run_silent_cmd(*cmd_args, cwd=None):
  cmd = list([x for x in cmd_args if x is not None])
  try:
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
  except subprocess.CalledProcessError as error:
    traceback.print_exc()
    print('Error running:')
    print('> {}'.format(' '.join(cmd)))
    print('exit code {}\n{}\n'.format(error.returncode, error.output.decode('utf-8') ))

def set_addtl_cargo_args(args):
  os.environ['BTOOL_CARGO_ADDTL_ARGS'] = json.dumps(args)

def get_addtl_cargo_args():
  args = []
  try:
    args = json.loads(os.environ.get('BTOOL_CARGO_ADDTL_ARGS', '[]'))
  except:
    traceback.print_exc()
  return args

def maybe(callback):
  try:
    return callback()
  except:
    traceback.print_exc()
    return None

