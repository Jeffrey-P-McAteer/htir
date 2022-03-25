
use htir::*;

#[tokio::main(flavor = "multi_thread", worker_threads = 10)]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    
    println!("Hello, server!");

    Ok(())
}
