
import importlib
import os
import sys
import subprocess
import shutil
import time
import traceback

from . import utils


def gen_icons(pov_scene_file, icon_sizes=None, display_cmd=None):
  
  def icon_pngs(sizes):
    for w,h in sizes:
      yield os.path.abspath(os.path.join('target', '{}x{}.png'.format(w,h) ))
  
  icon_icns = os.path.abspath(os.path.join('target', 'HTIR.icns'))
  if icon_sizes is None:
    icon_sizes = [
      # Ensure we use sizes icnsutil supports: https://github.com/relikd/icnsutil/blob/8243534f650c3b00fd59b141debf92fd30800aa5/icnsutil/IcnsType.py#L118
      #(16, 16), (32, 32), (48, 48),
      (128, 128), (256, 256), (512, 512), (1024, 1024),
    ]

  for f in [icon_icns] + [x for x in icon_pngs(icon_sizes)]:
    if os.path.exists(f):
      os.remove(f)

  icnsutil = utils.import_maybe_installing_with_pip('icnsutil')
  if not shutil.which('povray'):
    raise Exception('''
WARNING: you do not have the command "povray" installed, we depend on for rendering icons!
WARNING: please install "povray" for your OS and add it to your PATH before continuing.
'''.strip())
  
  print('Rendering {}'.format(pov_scene_file))

  # Render it!
  for w, h in icon_sizes:
    icon_png = next( icon_pngs([(w, h)]) )
    # https://www.mankier.com/1/povray
    cmd = [
      shutil.which('povray'),
      pov_scene_file,
      '+H{}'.format(h),
      '+W{}'.format(w),
      '+Q{}'.format(9), # 0=rough, 9=full ray tracing, 10 and 11 add radiosity
      '+A{}'.format(0.001), # antialiasing
      'Output_Alpha=on',
      '-D', # do not display image after render
      'Output_File_Type={}'.format('N'), # ???
      'Verbose=false',
      '+O{}'.format(icon_png),
    ]
    print('> {}'.format(' '.join(cmd)))
    # Only print output on errors, direct stderr to stdout for subprocess
    try:
      out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
      traceback.print_exc()
      print('\nError running povray, exit code {}\n\n{}\n'.format(error.returncode, error.output))
      
  # Write more output!
  img = icnsutil.IcnsFile()
  for w, h in icon_sizes:
    icon_png = next( icon_pngs([(w, h)]) )
    #img.add_media(key='icon_{}x{}'.format(w, h), file=icon_png)
    print('icon_png={}'.format(icon_png))
    with open(icon_png, 'rb') as fd:
      data = fd.read()
      img.add_media(file=os.path.basename(icon_png), data=data)
  img.write(icon_icns, toc=True)

  print('.icns verify output = {}'.format([x for x in icnsutil.IcnsFile.verify(icon_icns)]))

  if display_cmd is not None:
    largest_icon = [x for x in icon_pngs([(w, h)])][-1]
    subprocess.run(display_cmd + [ largest_icon ], check=False)

  
if __name__ == '__main__':
  # Allow testing va a render of 256x256 size via
  # python -m btool.icon_gen
  display_cmd = None
  if shutil.which('feh'):
    display_cmd = ['feh']
  elif shutil.which('open'):
    display_cmd = ['open']
  gen_icons('htir_app_icon.pov', icon_sizes=[(512, 512)], display_cmd=display_cmd)





