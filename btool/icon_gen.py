
import importlib
import os
import sys
import subprocess
import shutil
import time
import traceback

from . import utils


def gen_icons(pov_scene_file, icon_sizes=None, display_cmd=None):
  
  def is_source_newer(source_file, output_file):
    if not os.path.exists(output_file):
      return True
    return os.path.getmtime(source_file) > os.path.getmtime(output_file)
    
  def icon_pngs(sizes, suffix=''):
    for w,h in sizes:
      yield os.path.abspath(os.path.join('target', '{}x{}{}.png'.format(w,h,suffix) ))
  
  icon_icns = os.path.abspath(os.path.join('target', 'HTIR.icns'))
  if icon_sizes is None:
    icon_sizes = [
      # Ensure we use sizes icnsutil supports: https://github.com/relikd/icnsutil/blob/8243534f650c3b00fd59b141debf92fd30800aa5/icnsutil/IcnsType.py#L118
      #(16, 16), (32, 32), (48, 48),
      (128, 128), (256, 256), (512, 512), (1024, 1024),
    ]

  icnsutil = utils.import_maybe_installing_with_pip('icnsutil')
  PIL = utils.import_maybe_installing_with_pip('PIL', pkg_name='Pillow')
  for req_bin in ['povray', 'magick']:
    if not shutil.which(req_bin):
      raise Exception('''
  WARNING: you do not have the command "{req_bin}" installed, we depend on for rendering icons!
  WARNING: please install "{req_bin}" for your OS and add it to your PATH before continuing.
  '''.strip().format(req_bin=req_bin) )
  
  print('Rendering {}'.format(pov_scene_file))

  # Render it!
  for w, h in icon_sizes:

    icon_imgs_to_merge = []
    for scene_light in ['0', '1']:
      icon_png = next( icon_pngs([(w, h)], suffix='_lit_{}'.format('_'.join( filter(str.isalnum, scene_light) ) ) ) )
      icon_imgs_to_merge.append(icon_png)

      if is_source_newer(pov_scene_file, icon_png):
        # https://www.mankier.com/1/povray
        cmd = [
          shutil.which('povray'),
          pov_scene_file,
          'DECLARE=SL_r={}'.format(scene_light), # used in the .pov scene to render different chunks which are merged into final icon image
          'DECLARE=SL_g={}'.format(scene_light),
          'DECLARE=SL_b={}'.format(scene_light),
          '+H{}'.format(h),
          '+W{}'.format(w),
          '+Q{}'.format(9), # 0=rough, 9=full ray tracing, 10 and 11 add radiosity
          '+A{}'.format(0.001), # antialiasing
          #'Output_Alpha=on',
          'Output_Alpha=off', # unused since we added imagemagick to extract shadows
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
          print('\nError running povray, exit code {}\n\n{}\n'.format(error.returncode, error.output.decode('utf-8') ))

    icon_png = next( icon_pngs([(w, h)]) )

    icon_img_black = icon_imgs_to_merge[0]
    icon_img_white = icon_imgs_to_merge[1]

    if is_source_newer(icon_img_black, icon_png) or is_source_newer(icon_img_white, icon_png):
      # Two background technique: https://stackoverflow.com/a/54198549/9252743 , https://legacy.imagemagick.org/Usage/masking/#two_background
      cmd = [
        shutil.which('magick'),
        icon_img_black, icon_img_white,
        '-alpha', 'off',
        '(', '-clone', '0,1', '-compose', 'difference', '-composite', '-negate', ')',
        '(', '-clone', '0,2', '+swap', '-compose', 'divide', '-composite', ')',
        '-delete', '0,1', '+swap', '-compose', 'CopyOpacity', '-composite',
        icon_png
      ]
      print('> {}'.format(' '.join(cmd)))
      subprocess.run(cmd, check=True)

      
  # Write more output!
  if any([is_source_newer(x, icon_icns) for x in icon_pngs(icon_sizes)]):
    img = icnsutil.IcnsFile()
    for w, h in icon_sizes:
      icon_png = next( icon_pngs([(w, h)]) )
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





