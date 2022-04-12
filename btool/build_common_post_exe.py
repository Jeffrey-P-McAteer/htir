
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
  # Now that we have all target .exes built, package them
  if utils.can_compile_macos():
    build_macos_app_bundle()
  
  print_macos_exe_locations()

  print_windows_exe_locations()

  print_linux_exe_locations()


def print_linux_exe_locations():
  linux_client_exe = utils.get_first_existing(
    os.path.join('target', 'x86_64-unknown-linux-gnu', 'release', 'client'),
    os.path.join('target', 'aarch64-unknown-linux-gnu', 'release', 'client'),
  )
  linux_server_exe = utils.get_first_existing(
    os.path.join('target', 'x86_64-unknown-linux-gnu', 'release', 'server'),
    os.path.join('target', 'aarch64-unknown-linux-gnu', 'release', 'server'),
  )

  if linux_client_exe:
    print('Linux client is located at {}'.format(os.path.abspath(linux_client_exe)))

  if linux_server_exe:
    print('Linux server is located at {}'.format(os.path.abspath(linux_server_exe)))


def print_windows_exe_locations():
  windows_client_exe = utils.get_first_existing(
    os.path.join('target', 'x86_64-pc-windows-gnu', 'release', 'client.exe'),
    os.path.join('target', 'x86_64-pc-windows-msvc', 'release', 'client.exe'),
    os.path.join('target', 'aarch64-pc-windows-msvc', 'release', 'client.exe'),
  )
  windows_server_exe = utils.get_first_existing(
    os.path.join('target', 'x86_64-pc-windows-gnu', 'release', 'server.exe'),
    os.path.join('target', 'x86_64-pc-windows-msvc', 'release', 'server.exe'),
    os.path.join('target', 'aarch64-pc-windows-msvc', 'release', 'server.exe'),
  )

  if windows_client_exe:
    print('Windows client.exe is located at {}'.format(os.path.abspath(windows_client_exe)))

  if windows_server_exe:
    print('Windows server.exe is located at {}'.format(os.path.abspath(windows_server_exe)))

def print_macos_exe_locations():
  macos_client_exe = utils.get_first_existing(
    os.path.join('target', 'x86_64-apple-darwin', 'release', 'client'),
    os.path.join('target', 'aarch64-apple-darwin', 'release', 'client'),
  )
  macos_server_exe = utils.get_first_existing(
    os.path.join('target', 'x86_64-apple-darwin', 'release', 'server'),
    os.path.join('target', 'aarch64-apple-darwin', 'release', 'server'),
  )

  if macos_client_exe:
    print('MacOS client is located at {}'.format(os.path.abspath(macos_client_exe)))

  if macos_server_exe:
    print('MacOS server is located at {}'.format(os.path.abspath(macos_server_exe)))
    

def build_macos_app_bundle():
  client_exe = os.path.abspath( os.path.join( 'target', 'x86_64-apple-darwin', 'release', 'client' ) )

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


  print('MacOS HTIR Client .app created at {}'.format(HTIR_app))


  # Now put .app in .dmg w/ background image!
  if shutil.which('mkfs.hfsplus'):
    dmg_image_size_bytes = utils.directory_size_bytes(HTIR_app)
    dmg_image_size_bytes *= 1.35 # assume hfs+ needs 35% overhead for bookkeeping

    dmg_image_size_mbytes = int(dmg_image_size_bytes / 1000000)

    dmg_file = os.path.abspath(os.path.join('target', 'HTIR.dmg'))
    dmg_mountpoint = os.path.abspath(os.path.join('target', 'HTIR.dmg_mount'))

    if os.path.exists(dmg_mountpoint):
      subprocess.run(['sudo', 'umount', dmg_mountpoint], check=False) # not fatal if process dies, we just need to try before removing .dmg file
    os.makedirs(dmg_mountpoint, exist_ok=True)

    if os.path.exists(dmg_file):
      os.remove(dmg_file)

    utils.run_silent_cmd('dd', 'if=/dev/zero', 'of={}'.format(dmg_file), 'bs=1M', 'count={}'.format(dmg_image_size_mbytes))
    utils.run_silent_cmd('mkfs.hfsplus', '-v', 'InstallHTIR', '-M', '777', dmg_file)

    utils.run_silent_cmd('sudo', 'mount', '-o', 'loop', dmg_file, dmg_mountpoint)

    shutil.copytree(HTIR_app, os.path.join(dmg_mountpoint, os.path.basename(HTIR_app)))
    # .dmg contains ./HTIR.app, anything else?

    subprocess.run(['sudo', 'umount', dmg_mountpoint], check=False)
    os.rmdir(dmg_mountpoint)

    print('MacOS HTIR Client .cmd created at {}'.format(dmg_file))


  elif shutil.which('hdiutil'):
    dmg_file = os.path.abspath(os.path.join('target', 'HTIR.dmg'))
    dmg_mountpoint = os.path.abspath(os.path.join('target', 'HTIR.dmg_mount'))
    if os.path.exists(dmg_mountpoint):
      shutil.rmtree(dmg_mountpoint)
    os.makedirs(dmg_mountpoint, exist_ok=True)

    shutil.copytree(HTIR_app, os.path.join(dmg_mountpoint, os.path.basename(HTIR_app)))
    # .dmg contains ./HTIR.app, anything else?

    utils.run_silent_cmd(
      'hdiutil', 'create', '-volname', 'InstallHTIR', '-srcfolder', dmg_mountpoint, '-ov', '-format', 'UDZO', dmg_file
    )

    print('MacOS HTIR Client .cmd created at {}'.format(dmg_file))









