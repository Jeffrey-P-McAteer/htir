
import sys
import os

# Tell python where htir.pyd is
htir_folder = os.path.abspath(os.path.join(
  os.path.dirname(__file__), '..', 'htir_py', 'target', 'release'
))
print('Addding {} to sys.path...'.format(htir_folder))
sys.path.append(htir_folder)

import htir

print(htir.test01("Python String"))


