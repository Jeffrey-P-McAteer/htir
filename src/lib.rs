



pub mod config {
  use std::path::{Path, PathBuf};

  #[derive(Default, Debug, Copy, Clone)]
  pub struct Config {
    pub some_option: f64,

  }

  pub fn read_config<'a, P: Into<PathBuf>>(override_config_file: Option<P>) -> Result<Config, Box<dyn std::error::Error>> {
    if let Some(override_config_file) = override_config_file {
      return read_config_from_file( override_config_file.into().as_path() );
    }
    Ok(Config::default())
  }

  pub fn read_config_from_file(_file: &Path) -> Result<Config, Box<dyn std::error::Error>> {
    std::unimplemented!()
  }

}

