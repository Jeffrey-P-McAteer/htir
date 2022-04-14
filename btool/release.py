
import os
import sys
import shutil
import subprocess

# Our libraries

import btool

def main(args=sys.argv):
  btool.main(args)

  linux_release_files = [
    ( os.path.abspath(os.path.join('target', 'x86_64-unknown-linux-gnu', 'release', 'client')), 'linux-x86_64-client'),
    ( os.path.abspath(os.path.join('target', 'x86_64-unknown-linux-gnu', 'release', 'server')), 'linux-x86_64-server'),
    # Todo aarch64 names
  ]

  windows_release_files = [
    ( os.path.abspath(os.path.join('target', 'x86_64-pc-windows-gnu', 'release', 'client.exe')), 'windows-x86_64-client.exe'),
    ( os.path.abspath(os.path.join('target', 'x86_64-pc-windows-gnu', 'release', 'server.exe')), 'windows-x86_64-server.exe' ),
    # Todo aarch64 names
  ]

  macos_release_files = [
    ( os.path.abspath(os.path.join('target', 'HTIR.dmg')), 'macos-HTIR.dmg'),
    ( os.path.abspath(os.path.join('target', 'x86_64-apple-darwin', 'release', 'client')), 'macos-x86_64-client'),
    ( os.path.abspath(os.path.join('target', 'x86_64-apple-darwin', 'release', 'server')), 'macos-x86_64-server'),
    # Todo aarch64 names
  ]

  asset_staging_dir = os.path.abspath( os.path.join('target', 'release_stage') )
  os.makedirs(asset_staging_dir, exist_ok=True)
  for f in os.listdir(asset_staging_dir):
    os.remove(os.path.join(asset_staging_dir, f))

  assets_to_upload = []
  for file_path, release_name in linux_release_files + windows_release_files + macos_release_files:
    if os.path.exists(file_path):
      release_asset_path = os.path.join(asset_staging_dir, release_name)
      shutil.copy(
        file_path, release_asset_path
      )
      assets_to_upload.append(release_asset_path)

  github_access_token = os.environ.get('GITHUB_ACCESS_TOKEN', '')
  if len(github_access_token) < 1:
    raise Exception('Cannot upload release, GITHUB_ACCESS_TOKEN={}'.format(github_access_token))

  github_username = os.environ.get('GITHUB_USERNAME', '')
  if len(github_username) < 1:
    raise Exception('Cannot upload release, GITHUB_USERNAME={}'.format(github_username))

  github_binary_upload = utils.import_maybe_installing_with_pip('github_binary_upload', pkg_name='github-binary-upload')
  toml = utils.import_maybe_installing_with_pip('toml')
  cargo_toml = toml.load('Cargo.toml')
  release_version = cargo_toml.get('package', {}).get('version', '0.0.0')

  print('Releasing version {}'.format(release_version))
  for f in assets_to_upload:
    print('> {}'.format(os.path.basename(f)))

  github_binary_upload.publish_release_from_tag(
    'htir', None, assets_to_upload, 'https://api.github.com', github_username, github_access_token, False
  )

  

if __name__ == '__main__':
  main()

