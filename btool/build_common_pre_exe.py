
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
  # Uses a 3rd-party renderer & python code to render high-quality .png and generate a .icns file under ./target/
  icon_gen.gen_icons(os.path.abspath(os.path.join('htir_app_icon.pov')))





