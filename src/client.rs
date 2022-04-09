
use tokio::runtime::{Builder};

use htir::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let rt = Builder::new_current_thread()
      .build()?;

    rt.block_on(async {
      let _ = config::read_config::<&str>(None);

      println!("Hello async client runtime!");

    });

    Ok(())
}
