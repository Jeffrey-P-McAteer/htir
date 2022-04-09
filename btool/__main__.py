
# This python module provides a higher-level control over
# the `cargo` build that supports building the library (under ./src/lib.rs),
# multiple binaries (./src/{server,client}.rs), and running tests
# using the built artifacts.

import os
import sys
import subprocess
import shutil
import traceback

def is_windows_host():
  return os.name == 'nt'

# Normalize getting to repo root from any sub-directory
for _ in range(0, 12):
  if not (os.path.exists('.gitignore') and os.path.exists('readme.md')):
    os.chdir('..')

subprocess.run(['cargo', 'build', '--release'], check=True)

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

server_exe = os.path.join('target', 'release', 'server' if not is_windows_host() else 'server.exe')
client_exe = os.path.join('target', 'release', 'client' if not is_windows_host() else 'client.exe')

print('')

sproc = subprocess.Popen([server_exe], cwd=os.path.join('.'))

try:
  subprocess.run([client_exe] + list(sys.argv[1:]) , cwd=os.path.join('.'))
except:
  traceback.print_exc()


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





