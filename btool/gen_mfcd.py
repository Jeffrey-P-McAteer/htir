

import os
import sys
import subprocess
import tempfile
import shutil
import urllib.request
import zipfile
import io

def get_ditaa_cmd():
  if shutil.which('ditaa'):
    return [ shutil.which('ditaa') ]

  if shutil.which('java'):
    temp_ditaa_jar = os.path.abspath(os.path.join(
      tempfile.gettempdir(), 'ditaa.jar'
    ))

    if not os.path.exists(temp_ditaa_jar):
      # Download a copy; we'll un-zip in-memory for deployment simplicity
      get_url = 'https://downloads.sourceforge.net/project/ditaa/ditaa/0.9/ditaa0_9.zip'
      response = urllib.request.urlopen(get_url)
      
      while len( response.headers.get('Location', '') ) > 1:
        new_url = response.headers.get('Location', '')
        print('Redirecting {} to {}'.format(get_url, new_url))
        get_url = new_url
        response = urllib.request.urlopen(get_url)

      # We have a response object w/o Location redirect header

      print('Downloading {} to {}'.format(get_url, temp_ditaa_jar))

      zipfile_data = response.read()
      zipfile_data = io.BytesIO(zipfile_data)
      with zipfile.ZipFile(zipfile_data) as zf:
        with zf.open('ditaa0_9.jar', 'r') as ditaa_jar:
          with open(temp_ditaa_jar, 'wb') as fd:
            fd.write( ditaa_jar.read() )

    return [ shutil.which('java'), '-jar', temp_ditaa_jar ]


  raise Exception('Cannot find java or ditaa commands!')


def main(args=sys.argv):

  ditaa_source = os.path.join('meili_mfcd.ditaa')
  mfcd_out = os.path.join('target', 'mfcd.png')

  os.makedirs(os.path.dirname(mfcd_out), exist_ok=True)

  cmd = get_ditaa_cmd() + ['--overwrite', '--round-corners', '--scale', '2.0', ditaa_source, mfcd_out]
  print('> {}'.format(' '.join(cmd)))
  subprocess.run(cmd, check=True)

  if os.path.exists(mfcd_out):
    print('Generated {}'.format(mfcd_out))
    
    if shutil.which('feh'):
      subprocess.Popen(['feh', mfcd_out], start_new_session=True)







if __name__ == '__main__':
  main()