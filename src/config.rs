
use std::path::{Path, PathBuf};
use std::net::{IpAddr, Ipv4Addr, Ipv6Addr};
//use std::str::FromStr;
//use std::any::{Any, TypeId};

use tokio_rustls::rustls::{Certificate, PrivateKey};

use clap;

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct Config {
  pub server_listen_ip: IpAddr, // TCP + UDP
  pub server_listen_port: u16, // TCP + UDP + Multicast groups
  pub server_multicast_groups: Vec<IpAddr>, // Multiple groups to allow v4 and v6 comms elegantly

  pub server_ssl_cert_file: Option<PathBuf>,
  pub server_ssl_key_file: Option<PathBuf>,

  // Everything below is set from the above using Config::enrich

  #[serde(skip)]
  pub server_ssl_certs: Vec<Certificate>,

  #[serde(skip)]
  pub server_ssl_pkey: Option<PrivateKey>,


}

impl Default for Config {
  fn default() -> Config {
    Config {
      //server_listen_ip: IpAddr::V4( Ipv4Addr::new(0, 0, 0, 0) ),
      server_listen_ip: IpAddr::V6( Ipv6Addr::new(0, 0, 0, 0, 0, 0, 0, 0) ), // Pretty much all OSes give us 0.0.0.0 ipv4 as well when ::/0 is specified.
      server_listen_port: 4430,
      server_multicast_groups: vec![ IpAddr::V6( Ipv6Addr::new(0, 0, 0, 0, 0, 0, 0, 0) ), ],
      server_ssl_cert_file: None,
      server_ssl_key_file: None,
      server_ssl_certs: vec![],
      server_ssl_pkey: None,
    }
  }
}

impl Config {
  // Responsible for using config values to generate the lower config fields which
  // may not make sense to "parse" because they rely on multiple upper fields agreeing on something.
  pub fn enrich(&mut self) -> Result<(), Box<dyn std::error::Error>> {
    
    Ok(())
  }

  // Accessors which use base data to construct richer types
  pub fn get_listen_socket(&self) -> std::net::SocketAddr {
    std::net::SocketAddr::new(self.server_listen_ip, self.server_listen_port)
  }

}

pub fn read_config<'a, P: Into<PathBuf>>(override_config_file: Option<P>) -> Config {
  if let Some(override_config_file) = override_config_file {
    let config_file_path = override_config_file.into();
    let config_file_path = config_file_path.as_path();
    match read_config_from_file( config_file_path ) {
      Ok(c) => return c,
      Err(e) => {
        eprintln!("Error reading config from {}: {:?}", config_file_path.display(), e);
        return Config::default();
      }
    }
  }
  return Config::default()
}

pub fn read_config_from_file(file: &Path) -> Result<Config, Box<dyn std::error::Error>> {  
  let file_contents = std::fs::read_to_string(file)?;
  Ok( toml::from_str(&file_contents)? )
}

/*
fn try_key_val_into<T: FromStr + Any + 'static, U: AsRef<str>>(
  obj: &libucl::Object,
  key: U) -> Result<Option<T>, <T as FromStr>::Err >
  where <T as FromStr>::Err: std::error::Error
{
  let key = key.as_ref();
  if key.contains(".") {
    let obj = obj.fetch_path(key);
    if let Some(obj) = obj {
      // We have a value, go into parsing mode!
      if TypeId::of::<T>() == TypeId::of::<u16>() || TypeId::of::<T>() == TypeId::of::<i16>() ||
         TypeId::of::<T>() == TypeId::of::<u32>() || TypeId::of::<T>() == TypeId::of::<i32>() ||
         TypeId::of::<T>() == TypeId::of::<u64>() || TypeId::of::<T>() == TypeId::of::<i64>() ||
         TypeId::of::<T>() == TypeId::of::<usize>() || TypeId::of::<T>() == TypeId::of::<isize>()
      {
        if let Some(obj_int) = obj.as_int() { // try as i64
          //... turn it back into a string so we rely on the FromStr::parse::<T> for &str -> T
          let obj_s = format!("{}", obj_int);
          match obj_s.parse::<T>() {
            Ok(val) => {
              return Ok(Some( val ));
            }
            Err(e) => {
              return Err(e);
            }
          }
        }
      }
      else {
        if let Some(obj_s) = obj.as_string() { // try as a string
          match obj_s.parse::<T>() {
            Ok(val) => {
              return Ok(Some( val ));
            }
            Err(e) => {
              return Err(e);
            }
          }
        }
      }
    }
  }
  else {
    let obj = obj.fetch(key);
    if let Some(obj) = obj {
      // We have a value, go into parsing mode!
      if TypeId::of::<T>() == TypeId::of::<u16>() || TypeId::of::<T>() == TypeId::of::<i16>() ||
         TypeId::of::<T>() == TypeId::of::<u32>() || TypeId::of::<T>() == TypeId::of::<i32>() ||
         TypeId::of::<T>() == TypeId::of::<u64>() || TypeId::of::<T>() == TypeId::of::<i64>() ||
         TypeId::of::<T>() == TypeId::of::<usize>() || TypeId::of::<T>() == TypeId::of::<isize>()
      {
        if let Some(obj_int) = obj.as_int() { // try as i64
          //... turn it back into a string so we rely on the FromStr::parse::<T> for &str -> T
          let obj_s = format!("{}", obj_int);
          match obj_s.parse::<T>() {
            Ok(val) => {
              return Ok(Some( val ));
            }
            Err(e) => {
              return Err(e);
            }
          }
        }
      }
      else {
        if let Some(obj_s) = obj.as_string() { // try as a string
          match obj_s.parse::<T>() {
            Ok(val) => {
              return Ok(Some( val ));
            }
            Err(e) => {
              return Err(e);
            }
          }
        }
      }
    }
  }
  return Ok(None);
}
*/


//////// Client-supporting config

#[derive(clap::Parser, Debug, Default)]
#[clap(author, version, about, long_about = None)]
pub struct Args {
  #[clap(short, long)]
  pub open_gui: bool,

  #[clap(short, long)]
  pub debug: bool,

  pub url: Option<String>,

}


