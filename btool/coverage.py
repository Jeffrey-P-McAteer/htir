
import os
import sys
import subprocess
import time
import traceback
import webbrowser

import btool

from . import utils

from . import build_common_pre_exe
from . import build_linux
from . import build_macos
from . import build_windows
from . import build_common_post_exe


def main(args=sys.argv):
  utils.cd_up_to_repo_root()
  build_common_pre_exe.build_all()

  # Do we have tarpaulin?
  have_tarpaulin = False
  try:
    out = subprocess.check_output(['cargo', 'tarpaulin', '--help'])
    have_tarpaulin = True
  except:
    pass

  if not have_tarpaulin:
    subprocess.run(['cargo', 'install', 'cargo-tarpaulin'])

  # Finally run coverage
  subprocess.run(['cargo', 'tarpaulin', '--out', 'Html', '--output-dir', 'target'])

  html_report = os.path.abspath(
    os.path.join('target', 'tarpaulin-report.html')
  )

  webbrowser.open(html_report)




if __name__ == '__main__':
  main()

