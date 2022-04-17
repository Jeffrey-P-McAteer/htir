
use std::net::SocketAddr;
use std::path::{Path, PathBuf};
use std::fs::File;
use std::io::BufReader;
use std::sync::Arc;

use tokio::runtime::{Builder};
use tokio::net::{TcpListener, TcpStream};
use tokio::io::{ReadBuf, AsyncWriteExt};

use futures_util::{future, StreamExt, TryStreamExt};
use futures_util::future::poll_fn;

use tokio_rustls::rustls::{Certificate, PrivateKey};
use tokio_rustls::TlsAcceptor;

use meili::*;

fn main() -> Result<(), Box<dyn std::error::Error>> {
  let rt = Builder::new_multi_thread()
    //.worker_threads(4) // defaults to HW concurrency numbers reported by the OS / hardware
    .thread_stack_size(3 * 1024 * 1024)
    .enable_all()
    .build()?;

  rt.block_on(async {
    let c = config::read_config::<&str>(None);
    if let Err(e) = init_server_config(&c).await {
      eprintln!("Error during init_server_config: {}", e);
      return;
    }
    if let Err(e) = server_main(&c).await {
      eprintln!("Error during server_main: {}", e);
    }
  });

  Ok(())
}

async fn init_server_config(config: &config::Config) -> Result<(), Box<dyn std::error::Error>> {

  // All checks passed!
  Ok(())
}

async fn server_main(config: &config::Config) -> Result<(), Box<dyn std::error::Error>> {
  println!("server_main({:?})", config);
  let addr = "127.0.0.1:4430"; // TODO read from config
  
  // TODO encrypt server by default
  // TODO if no SSL connection 301 it to https
  // TODO if TCP is BARE packet prefer that

  let listener = TcpListener::bind(&addr).await?;
  eprintln!("Listening on: {}", addr);
  loop {
    match listener.accept().await {
      Ok((stream, remote_peer_addr)) => {
        tokio::spawn(async move {
          if let Err(e) = handle_connection(stream, remote_peer_addr).await {
            eprintln!("Error during handle_connection() for remote_peer_addr={}: {}", remote_peer_addr, e);
          }
        });
      }
      Err(e) => {
        eprintln!("listener.accept().await loop e={:?}", e);
      }
    }
  }
  Ok(())
}

async fn handle_connection(mut stream: TcpStream, remote_peer_addr: SocketAddr) -> Result<(), Box<dyn std::error::Error>> {
  eprintln!("TCP client connected: {}", remote_peer_addr);

  // Is this a BARE stream or an HTTP stream or an HTTPS stream?
  let mut buf = [0; 16384]; // 16kb buffer should fit most payloads, but we OUGHT to assume it will never hold the full stream.
  let mut buf = ReadBuf::new(&mut buf);
  
  poll_fn(|cx| {
    stream.poll_peek(cx, &mut buf)
  }).await?;

  let peeked_bytes_from_client: &[u8] = buf.filled();

  // Test for unencrypted HTTP GET, http_get_beginning_bytes is "GET "
  let http_get_beginning_bytes: &[u8] = &[0x47, 0x45, 0x54, 0x20];
  let is_unencrypted_http_stream = peeked_bytes_from_client.len() >= http_get_beginning_bytes.len() && (
    http_get_beginning_bytes[0] == peeked_bytes_from_client[0] &&
    http_get_beginning_bytes[1] == peeked_bytes_from_client[1] &&
    http_get_beginning_bytes[2] == peeked_bytes_from_client[2] &&
    http_get_beginning_bytes[3] == peeked_bytes_from_client[3]
  );
  if is_unencrypted_http_stream {
    // Return a 301 redirect to...
    let hostname_from_client = parse_out_host_from_http_get(peeked_bytes_from_client);
    let hostname_from_client = std::str::from_utf8(&hostname_from_client)?;
    let payload = format!(r#"HTTP/1.1 301 Moved Permanently
Location: https://{}
"#, hostname_from_client);
    stream.write(payload.as_bytes()).await?;
    stream.shutdown().await?;
    eprintln!("peeked_bytes_from_client={:?}", peeked_bytes_from_client);
    eprintln!("str::from_utf8(peeked_bytes_from_client)={:?}", std::str::from_utf8(peeked_bytes_from_client)? );
    eprintln!("{} gave unencrypted HTTP GET, we sent a 301 to https://", remote_peer_addr);
    return Ok(());
  }

  eprintln!("peeked_bytes_from_client={:?}", peeked_bytes_from_client);
  eprintln!("str::from_utf8(peeked_bytes_from_client)={:?}", std::str::from_utf8(peeked_bytes_from_client).unwrap_or("<UTF-8 Decode Error>") );

  // Now test if the first 16kb contains a BARE-encoded message we can understand
  // We use ServerTestStruct for now but later will use a better structure to decode.
  match serde_bare::from_slice::<ServerTestStruct>(peeked_bytes_from_client) {
    Ok(server_test_struct) => {
      eprintln!("serde_bare::from_slice server_test_struct={:?}", server_test_struct);
      // TODO
      return Ok(());
    }
    Err(e) => {
      eprintln!("serde_bare::from_slice e={}", e);
    }
  }

  // If we're still here then this MUST be an SSL-encrypted tcp stream,
  // and after decrypting we should check if this is HTTPS or BARE packets

  let certs = load_certs(&PathBuf::from("/j/proj/hackathon-2022-April/ssl/server.crt"))?;
  let mut keys = load_keys(&PathBuf::from("/j/proj/hackathon-2022-April/ssl/server.key"))?;

  let config = rustls::ServerConfig::builder()
      .with_safe_defaults()
      .with_no_client_auth()
      .with_single_cert(certs, keys.remove(0))
      .map_err(|err| std::io::Error::new(std::io::ErrorKind::InvalidInput, err))?;
  
  let acceptor = TlsAcceptor::from(Arc::new(config));

  let mut stream = acceptor.accept(stream).await?;


  // We have a plain-text websocket
  let ws_stream = tokio_tungstenite::accept_async(stream).await?;

  eprintln!("New WebSocket connection: {}", remote_peer_addr);

  let (write, read) = ws_stream.split();

  // We should not forward messages other than text or binary.
  read.try_filter(|msg| future::ready(msg.is_text() || msg.is_binary()))
      .forward(write)
      .await?;

  // End of session w no errors!
  Ok(())
}

fn load_certs(path: &Path) -> std::io::Result<Vec<Certificate>> {
    rustls_pemfile::certs(&mut BufReader::new(File::open(path)?))
        .map_err(|_| std::io::Error::new(std::io::ErrorKind::InvalidInput, "invalid cert"))
        .map(|mut certs| certs.drain(..).map(Certificate).collect())
}

fn load_keys(path: &Path) -> std::io::Result<Vec<PrivateKey>> {
    rustls_pemfile::rsa_private_keys(&mut BufReader::new(File::open(path)?))
        .map_err(|_| std::io::Error::new(std::io::ErrorKind::InvalidInput, "invalid key"))
        .map(|mut keys| keys.drain(..).map(PrivateKey).collect())
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
struct ServerTestStruct {
  pub a: String,
  pub b: u64,

  //#[serde(with = "serde_bytes")]
  //pub b: Vec<u8>,
}


// Yes I _could_ pull in a library, but I want this to be as fast as possible.
// If we get wierd input I don't need a fully-fledged error message, we're fine giving a broken
// redirect to the goofy client.
fn parse_out_host_from_http_get(http_fragment: &[u8]) -> Vec<u8> {
  // "Host: " as [u8]
  let http_host_beginning_bytes: &[u8] = &[0x48, 0x6f, 0x73, 0x74, 0x3a, 0x20];
  // "\r\n" as [u8]
  let http_host_ending_bytes: &[u8] = &[0xd, 0xa];
  let mut host_begin_i = 0;
  let mut host_end_i = 0;
  let mut host_name_copy = vec![];

  for i in 0..(http_fragment.len() - http_host_beginning_bytes.len()) {
    let is_match = 
      http_host_beginning_bytes[0] == http_fragment[i+0] &&
      http_host_beginning_bytes[1] == http_fragment[i+1] &&
      http_host_beginning_bytes[2] == http_fragment[i+2] &&
      http_host_beginning_bytes[3] == http_fragment[i+3] &&
      http_host_beginning_bytes[4] == http_fragment[i+4] &&
      http_host_beginning_bytes[5] == http_fragment[i+5];
    if is_match {
      host_begin_i = i + http_host_beginning_bytes.len();
    }
  }

  for i in host_begin_i..http_fragment.len() {
    let is_match =
      http_host_ending_bytes[0] == http_fragment[i+0] &&
      http_host_ending_bytes[1] == http_fragment[i+1];
    if is_match {
      host_end_i = i;
    }
  }

  if host_begin_i < host_end_i {
    for i in host_begin_i..host_end_i {
      host_name_copy.push( http_fragment[i] );
    }
  }

  return host_name_copy;
}
