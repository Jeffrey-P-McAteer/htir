
use std::path::{Path, PathBuf};
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};

use clap::Parser;


#[derive(Debug, Copy, Clone)]
pub struct Config {
  pub server_listen_ip: IpAddr,
  pub server_listen_port: u16,

  pub server_ssl_cert: (),
  pub server_ssl_pkey: (),


}

impl Default for Config {
  fn default() -> Config {
    Config {
      //server_listen_ip: IpAddr::V4( Ipv4Addr::new(0, 0, 0, 0) ),
      server_listen_ip: IpAddr::V6( Ipv6Addr::new(0, 0, 0, 0, 0, 0, 0, 0) ), // Pretty much all OSes give us 0.0.0.0 ipv4 as well when ::/0 is specified.
      server_listen_port: 4430,
      server_ssl_cert: (),
      server_ssl_pkey: (),
    }
  }
}

pub fn read_config<'a, P: Into<PathBuf>>(override_config_file: Option<P>) -> Config {
  if let Some(override_config_file) = override_config_file {
    match read_config_from_file( override_config_file.into().as_path() ) {
      Ok(c) => return c,
      Err(e) => {
        eprintln!("read_config read_config_from_file e={:?}", e);
        return Config::default();
      }
    }
  }
  return Config::default()
}

pub fn read_config_from_file(_file: &Path) -> Result<Config, Box<dyn std::error::Error>> {
  std::unimplemented!()
}




//////// Client-supporting config

#[derive(Parser, Debug, Default)]
#[clap(author, version, about, long_about = None)]
pub struct Args {
  #[clap(short, long)]
  pub open_gui: bool,

  #[clap(short, long)]
  pub debug: bool,

  pub url: Option<String>,

}


