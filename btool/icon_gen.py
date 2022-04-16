
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
  povray_bin_name = 'povray'
  if utils.is_windows_host():
    povray_bin_name = 'pvengine'
    
  for req_bin in [povray_bin_name, 'magick']:
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
          shutil.which(povray_bin_name),
          *(['/EXIT', '/RENDER'] if utils.is_windows_host() else []), # windows used pvengine like an idiot which requires hand-holding: https://stackoverflow.com/a/2207533/9252743
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
        
        utils.run_silent_cmd(*cmd)

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

      
  # Write macos-specific output!
  if any([is_source_newer(x, icon_icns) for x in icon_pngs(icon_sizes)]):
    img = icnsutil.IcnsFile()
    for w, h in icon_sizes:
      icon_png = next( icon_pngs([(w, h)]) )
      with open(icon_png, 'rb') as fd:
        data = fd.read()
        try:
          img.add_media(file=os.path.basename(icon_png), data=data)
        except:
          # We get an error after 512x512@2x is added and then 1024x1024 is added, but this appears ignoreable?
          # KeyError: 'Image with identical key "ic10". File: 1024x1024.png'
          traceback.print_exc()
        

      possible_2x = next( icon_pngs([(w*2, h*2)]) )
      if os.path.exists(possible_2x):
        with open(possible_2x, 'rb') as fd:
          data_2x = fd.read() # read the 2x data
          img.add_media(file=os.path.basename( next(icon_pngs([(w, h)], suffix='@2x') ) ), data=data_2x)
          
    img.write(icon_icns, toc=True)

  icns_verify_errors = [x for x in icnsutil.IcnsFile.verify(icon_icns)]
  if len(icns_verify_errors) > 0:
    print('.icns verify output = {}'.format(icns_verify_errors))

  # Write windows-specific output! (use first OR closest to 256 size)
  best_icon_size = icon_sizes[0]
  for h,w in icon_sizes:
    if h > 200 and h < 300 and w > 200 and w < 300:
      best_icon_size = (h, w)
  icon_png = next( icon_pngs([best_icon_size]) )
  windows_ico_file = os.path.abspath(os.path.join('target', 'HTIR.ico'))
  if is_source_newer(icon_png, windows_ico_file):
    print('Generating {}'.format(windows_ico_file))
    img = PIL.Image.open(icon_png)
    img.save(windows_ico_file, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (255, 255)])


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





