
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
  build_macos_app_bundle()




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


  print('MacOS .app created at {}'.format(HTIR_app))






