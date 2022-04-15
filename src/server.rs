
use tokio::runtime::{Builder};
use tokio::net::{TcpListener, TcpStream};

use futures_util::{future, StreamExt, TryStreamExt};

use htir::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
  let rt = Builder::new_multi_thread()
    //.worker_threads(4) // defaults to HW concurrency numbers reported by the OS / hardware
    .thread_stack_size(3 * 1024 * 1024)
    .enable_all()
    .build()?;

  rt.block_on(async {
    let c = config::read_config::<&str>(None);
    server_main(&c).await;
  });

  Ok(())
}

async fn server_main(config: &config::Config) -> Result<(), Box<dyn std::error::Error>> {
  println!("server_main({:?})", config);
  let addr = "127.0.0.1:8080"; // TODO read from config
  
  // TODO encrypt server by default
  // TODO if no SSL connection 301 it to https
  // TODO if TCP is BARE packet prefer that

  let listener = TcpListener::bind(&addr).await?;
  eprintln!("Listening on: {}", addr);
  loop {
    match listener.accept().await {
      Ok((stream, _)) => {
        tokio::spawn(accept_connection(stream));
      }
      Err(e) => {
        eprintln!("listener.accept().await loop e={:?}", e);
      }
    }
  }
  Ok(())
}

async fn accept_connection(stream: TcpStream) {
    let addr = stream.peer_addr().expect("connected streams should have a peer address");
    eprintln!("Peer address: {}", addr);

    let ws_stream = tokio_tungstenite::accept_async(stream)
        .await
        .expect("Error during the websocket handshake occurred");

    eprintln!("New WebSocket connection: {}", addr);

    let (write, read) = ws_stream.split();
    // We should not forward messages other than text or binary.
    read.try_filter(|msg| future::ready(msg.is_text() || msg.is_binary()))
        .forward(write)
        .await
        .expect("Failed to forward messages")
}


