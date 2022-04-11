
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
  create_misc_directories_we_assume_exist()
  
  # Uses a 3rd-party renderer & python code to render high-quality .png and generate a .icns file under ./target/
  icon_gen.gen_icons(os.path.abspath(os.path.join('htir_app_icon.pov')))



def create_misc_directories_we_assume_exist():
  utils.cd_up_to_repo_root()
  
  os.makedirs('target', exist_ok=True)




