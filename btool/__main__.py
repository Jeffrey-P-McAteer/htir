
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

server_exe = os.path.join('target', 'release', 'server' if not is_windows_host() else 'server.exe')
client_exe = os.path.join('target', 'release', 'client' if not is_windows_host() else 'client.exe')

sproc = subprocess.Popen([server_exe], cwd=os.path.join('.'))

try:
  subprocess.run([client_exe] + list(sys.argv[1:]) , cwd=os.path.join('.'))
except:
  traceback.print_exc()

print('Killing server...')
sproc.kill()



