
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

from . import icon_gen
from . import utils

from . import build_common_pre_exe
from . import build_linux
from . import build_macos
from . import build_windows
from . import build_common_post_exe

utils.cd_up_to_repo_root()

build_common_pre_exe.build_all()

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

print('TODO move test logic someplace & call it here!')

sys.exit(0)

# Uses a 3rd-party renderer & python code to render high-quality .png and generate a .icns file under ./target/
icon_gen.gen_icons(os.path.abspath(os.path.join('htir_app_icon.pov')))

subprocess.run(['cargo', 'build', '--release'], check=True)

if not is_macos_host():
  try:
    subprocess.run(['cargo', 'build', '--release'], check=True, cwd='htir_py')
    library_renames = [('libhtir.so', 'htir.so'), ]
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
  HTIR_app = os.path.abspath( os.path.join('target', 'HTIR.app') )
  os.makedirs(HTIR_app, exist_ok=True)
  os.makedirs(os.path.join(HTIR_app, 'Contents', 'Resources'), exist_ok=True)
  
  files_to_copy = [
    (client_exe, os.path.join(HTIR_app, 'HTIR')),
    (os.path.join('target', 'HTIR.icns'), os.path.join(HTIR_app, 'Contents', 'Resources', 'AppIcon.icns')),
  ]
  for src_f, dst_f in files_to_copy:
    try:
      shutil.copy(src_f, dst_f)
    except shutil.SameFileError:
      pass # why bother? Ugh.

  # Finally create Contents/Info.plist
  plistlib = utils.import_maybe_installing_with_pip('plistlib')

  plist_data = dict(
    CFBundleDisplayName='HTIR',
    CFBundleName='HTIR',
    CFBundleExecutable=os.path.join('HTIR'),
    CFBundleIconFile=os.path.join('Contents', 'Resources', 'AppIcon.icns'), # Legacy apparently?
    #CFBundleIconName='', # TODO research asset catalog & use this; potential light + dark-mode icons?
    CFBundleIdentifier='pw.jmcateer.htir-client',
    NSHighResolutionCapable=True,
  )

  with open(os.path.join(HTIR_app, 'Contents', 'Info.plist'), 'wb') as fd:
    plistlib.dump(plist_data, fd)


  print('MacOS .app created at {}'.format(HTIR_app))

print('')
print('HTIR Server and Client application built, running tests....')
print('')

server_cmd = [server_exe]
print('Spawning background server: {}'.format(' '.join(server_cmd)))
sproc = subprocess.Popen(server_cmd, cwd=os.path.join('.'))

try:
  if is_macos_host():
    stdout_file = os.path.abspath( os.path.join('target', 'htir_app_stdout.txt') )
    stderr_file = os.path.abspath( os.path.join('target', 'htir_app_stderr.txt') )

    for f in [stdout_file, stderr_file]:
      with open(f, 'w') as fd:
        fd.write('') # empty & create the file in the same call

    client_cmd = [
      '/usr/bin/open',
      '-W', # Wait for app to close
      '--stdout', stdout_file,     # Forward stdout (causes permission errors if /dev/stdout)
      '--stderr', stderr_file,     # Forward stderr (causes permission errors if /dev/stderr)
      '-a', HTIR_app, # -a <application>.app
      '--args'] + list(sys.argv[1:])

    print('Running MacOS client app: {}'.format(' '.join(client_cmd)))
    #subprocess.run(client_cmd, cwd=os.path.join('.'))
    client_p = subprocess.Popen(client_cmd, cwd=os.path.join('.'))

    printed_stdout = ''
    printed_stderr = ''
    while client_p.poll() is None:
      for f in [stdout_file, stderr_file]:
        with open(f, 'r') as fd:
          contents = fd.read()
          if len(contents) > 0:
            new_contents = contents[len(printed_stdout):]
            if len(new_contents) > 0:
              sys.stdout.write(new_contents)
              sys.stdout.flush()
              printed_stdout += new_contents

      time.sleep(0.05)

    print('HTIR.app exited with {}'.format(client_p.returncode))
    
  else:
    
    client_cmd = [client_exe] + list(sys.argv[1:])
    print('Running client command: {}'.format(' '.join(client_cmd)))
    subprocess.run(client_cmd, cwd=os.path.join('.'))

except:
  traceback.print_exc()

if not is_macos_host():
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





