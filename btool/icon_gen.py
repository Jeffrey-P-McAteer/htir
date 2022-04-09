
import importlib
import os
import sys
import subprocess
import shutil
import time

from . import utils


def gen_icons():
  
  def icon_pngs(sizes):
    for w,h in sizes:
      yield os.path.abspath(os.path.join('target', '{}x{}.png'.format(w,h) ))
  
  icon_icns = os.path.abspath(os.path.join('target', 'HTIR.icns'))
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
    print('')
    print('WARNING: you do not have the command "povray" installed, which vapory depends on!')
    print('WARNING: please install "povray" for your OS and add it to your PATH before continuing.')
    print('')
    time.sleep(1)
  vapory = utils.import_maybe_installing_with_pip('vapory') # POV-ray powered graphics engine!
  
  # Cheap "import"; for all keys in vapory.__dict__ not beginning with '_', add it to locals()
  for key, value in vapory.__dict__.items():
    if key.startswith('_'):
      continue
    globals()[key] = value

  # Got our dependencies, now describe the icon scene!

  scene = Scene(  Camera('location',  [0.0, 0.5, -4.0],
                         'direction', [0,0,1.5],
                         'look_at',  [0, 0, 0],
                         #'aperture', 0.4,
                         'blur_samples', 100), # increase for high quality render

                  objects = [

                      Background("color", [0.85, 0.75, 0.75]),

                      LightSource([0, 0, 0],
                                    'color',[0.9, 0.9, 0.9],
                                    'translate', [-5, 5, -5]),

                      LightSource ([0, 0, 0],
                                      'color', [0.15, 0.15, 0.25],
                                      'translate', [6, -6, -6]),


                      #Box([-0.5, -0.5, -0.5], [0.5, 0.5, 0.5],
                      #     Texture( Pigment( 'color', [0.1,0.1,0.9]),
                      #              Finish('specular', 0.6),
                      #              Normal('agate', 0.25, 'scale', 0.5)),
                      #    'rotate', [45, 46, 47]),

                      Cylinder([-0.5, -0.5, -0.5], [0.5, 0.5, 0.5], 0.4,
                          Texture( Pigment( 'color', [0.1,0.1,0.9]),
                                   Finish('specular', 0.6),
                                   Normal('agate', 0.25, 'scale', 0.5)),
                         'rotate', [-45, -45, 45]),

                      #Cylinder([-0.5, -0.5, -0.5], [0.5, 0.5, 0.5], 0.5,
                      #  Finish('ambient', 0.1, 'diffuse', 0.6),
                      #  Pigment('color', [0.1,0.1,0.9]),
                      #  'rotate', [45, 46, 47] ),

                 ]
  )


  # Render it!
  for w, h in icon_sizes:
    icon_png = next( icon_pngs([(w, h)]) )
    scene.render(icon_png, width=w, height=h, antialiasing=0.001, output_alpha=True)

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

  print('verify output = {}'.format([x for x in icnsutil.IcnsFile.verify(icon_icns)]))

  # Just for jeff to inspect stuff
  if '/j/' in os.environ.get('HOME', ''):
    largest_icon = [x for x in icon_pngs([(w, h)])][-1]
    subprocess.run(['feh', largest_icon ], check=False)

  



