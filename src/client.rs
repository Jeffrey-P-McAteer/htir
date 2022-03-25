
use tokio::runtime::{Runtime, Builder};

use htir::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let rt = Builder::new_current_thread()
      .build()?;

    rt.block_on(async {
      
      println!("Hello async client runtime!");

    });

    Ok(())
}
