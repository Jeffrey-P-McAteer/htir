
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

def is_windows_host():
  return os.name == 'nt'

def is_macos_host():
  return 'darwin' in platform.system().lower()


# Normalize getting to repo root from any sub-directory
for _ in range(0, 12):
  if not (os.path.exists('.gitignore') and os.path.exists('readme.md')):
    os.chdir('..')

subprocess.run(['cargo', 'build', '--release'], check=True)

try:
  subprocess.run(['cargo', 'build', '--release'], check=True, cwd='htir_py')
  library_renames = [('libhtir.so', 'htir.so')]
  for name, target_name in library_renames:
    full_path = os.path.join('htir_py', 'target', 'release', name)
    if os.path.exists(full_path):
      target_path = os.path.join('htir_py', 'target', 'release', target_name)
      print('Copying {} to {} so python import will find it...'.format(full_path, target_path))
      try:
        shutil.copy(full_path, target_path)
      except shutil.SameFileError:
        pass # why bother? Ugh.
except:
  traceback.print_exc()


server_exe = os.path.abspath( os.path.join('target', 'release', 'server' if not is_windows_host() else 'server.exe') )
client_exe = os.path.abspath( os.path.join('target', 'release', 'client' if not is_windows_host() else 'client.exe') )

HTIR_app = None
if is_macos_host():
  # use client_exe to create target/HTIR.app, a directory
  # conforming to apple's app setup.
  HTIR_app = os.path.abspath( os.path.join('target', 'release', 'HTIR.app') )
  os.makedirs(HTIR_app, exist_ok=True)
  try:
    shutil.copy(client_exe, os.path.join(HTIR_app, 'HTIR'))
  except shutil.SameFileError:
    pass # why bother? Ugh.
  print('MacOS .app created at {}'.format(HTIR_app))

print('')

server_cmd = [server_exe]
print('Spawning background server: {}'.format(' '.join(server_cmd)))
sproc = subprocess.Popen(server_cmd, cwd=os.path.join('.'))

try:
  if is_macos_host():
    stdout_fifo = os.path.abspath( os.path.join('target', 'htir_app_stdout.fifo') )
    stderr_fifo = os.path.abspath( os.path.join('target', 'htir_app_stderr.fifo') )
    if not os.path.exists(stdout_fifo):
      os.mkfifo(stdout_fifo)
    if not os.path.exists(stderr_fifo):
      os.mkfifo(stderr_fifo)

    # Spawn a thread to poll each FIFO object
    os.environ['KILL_POLL_FIFO_T'] = 'f'
    def poll_fifo_write_to(fifo_file, out):
      with open(fifo_file, 'r') as fd:
        while not 't' in os.environ.get('KILL_POLL_FIFO_T', ''):
          select.select([fd],[],[fd]) # Wait until I/O available
          data = fd.read()
          if len(data) > 0:
            out.write(data)


    t1 = threading.Thread(target=poll_fifo_write_to, args=(stdout_fifo, sys.stdout))
    t1.start()
    t2 = threading.Thread(target=poll_fifo_write_to, args=(stderr_fifo, sys.stderr))
    t2.start()

    client_cmd = [
      '/usr/bin/open',
      '-W', # Wait for app to close
      '--stdin', '/dev/stdin',     # Forward stdin
      '--stdout', stdout_fifo,     # Forward stdout (causes permission errors if /dev/stdout)
      '--stderr', stderr_fifo,     # Forward stderr (causes permission errors if /dev/stderr)
      '-a', HTIR_app, # -a <application>.app
      '--args'] + list(sys.argv[1:])

    print('Running MacOS client app: {}'.format(' '.join(client_cmd)))
    subprocess.run(client_cmd, cwd=os.path.join('.'))
    os.environ['KILL_POLL_FIFO_T'] = 'true'
    time.sleep(0.1)

  else:
    client_cmd = [client_exe] + list(sys.argv[1:])
    print('Running client command: {}'.format(' '.join(client_cmd)))
    subprocess.run(client_cmd, cwd=os.path.join('.'))
except:
  traceback.print_exc()

print('')
print('Executing all example scripts...')
for file in os.listdir('examples'):
  cmd = []
  if file.endswith('.py'):
    cmd = [sys.executable, os.path.abspath(os.path.join('examples', file))]
  else:
    print('Unknown test for file {}'.format(file))
  
  print('')
  print('Executing: {}'.format(' '.join(cmd)))
  try:
    subprocess.run(cmd, check=True)
  except:
    traceback.print_exc()

print('')
print('Killing server...')
sproc.kill()





