
use tokio::runtime::{Runtime, Builder};

use htir::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let rt = Builder::new_multi_thread()
        //.worker_threads(4) // defaults to HW concurrency numbers reported by the OS / hardware
        .thread_stack_size(3 * 1024 * 1024)
        .enable_all()
        .build()?;

    rt.block_on(async {
      
      println!("Hello async server runtime!");

    });

    Ok(())
}
