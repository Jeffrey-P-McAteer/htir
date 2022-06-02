
use tokio::runtime::{Builder};
use clap::Parser;


use meili::*;
use meili::config::Args;

fn main() -> Result<(), Box<dyn std::error::Error>> {
  let args = Args::parse();

  let rt = Builder::new_current_thread()
    .build()?;

  rt.block_on(async {
    let _ = config::read_config::<&str>(None);

    if args.open_gui {
      gui_main(&args);
    }
    else {
      // If url is provided go CLI mode, otherwise go GUI mode (supports windows double-click fn)
      if let Some(ref url) = args.url {
        cli_main(&url, &args).await;
      }
      else {
        gui_main(&args).await;
      }
    }

  });

  Ok(())
}

async fn cli_main(url: &str, _args: &Args) {
  println!("Hello async cli_main runtime! url={:?}", url);

  visit_openpgp_cards();
  visit_pcsc_cards();
  visit_fido_keys();



}


fn visit_fido_keys() {
  use authenticator;
  use sha2::{Digest, Sha256};

  println!("=== visit_fido_keys ===");

  let mut manager = authenticator::authenticatorservice::AuthenticatorService::new().expect("The auth service should initialize safely");

  manager.add_u2f_usb_hid_platform_transports();

  println!("Asking a security key to register now...");
  let challenge_str = format!(
      "{}{}",
      r#"{"challenge": "1vQ9mxionq0ngCnjD-wTsv1zUSrGRtFqG2xP09SbZ70","#,
      r#" "version": "U2F_V2", "appId": "http://demo.yubico.com"}"#
  );
  let mut challenge = Sha256::default();
  challenge.input(challenge_str.as_bytes());
  let chall_bytes = challenge.result().to_vec();

  let mut application = Sha256::default();
  application.input(b"http://demo.yubico.com");
  let app_bytes = application.result().to_vec();

  let flags = authenticator::RegisterFlags::empty();

  let timeout_ms = 32000;

  let (status_tx, status_rx) = std::sync::mpsc::channel::<authenticator::StatusUpdate>();
  std::thread::spawn(move || loop {
      match status_rx.recv() {
          Ok(authenticator::StatusUpdate::DeviceAvailable { dev_info }) => {
              // println!("STATUS: device available: {}", dev_info)
          }
          Ok(authenticator::StatusUpdate::DeviceUnavailable { dev_info }) => {
              // println!("STATUS: device unavailable: {}", dev_info)
          }
          Ok(authenticator::StatusUpdate::Success { dev_info }) => {
              // println!("STATUS: success using device: {}", dev_info);
          }
          Err(RecvError) => {
              // println!("STATUS: end");
              return;
          }
      }
  });

  let (register_tx, register_rx) = std::sync::mpsc::channel();
  let callback = authenticator::statecallback::StateCallback::new(Box::new(move |rv| {
      register_tx.send(rv).unwrap();
  }));

  manager
      .register(
          flags,
          timeout_ms,
          chall_bytes.clone(),
          app_bytes.clone(),
          vec![],
          status_tx.clone(),
          callback,
      )
      .expect("Couldn't register");

  let register_result = register_rx
      .recv()
      .expect("Problem receiving, unable to continue");
  let (register_data, device_info) = register_result.expect("Registration failed");

  println!("Device info: {}", &device_info);

}

fn visit_openpgp_cards() {
  //use openpgp_card::OpenPgp;
  //use openpgp_card_pcsc::PcscBackend;
  use openpgp_card::CardBackend;
  println!("=== visit_openpgp_cards ===");

  for mode in [Some(pcsc::ShareMode::Exclusive), Some(pcsc::ShareMode::Shared), None, /* Some(pcsc::ShareMode::Direct) */ ] {
    println!("Querying for pcsc cards in mode={:?}", mode);
    match openpgp_card_pcsc::PcscBackend::cards(mode) {
      Ok(cards) => {
        println!("Got {} cards:", cards.len());
        for mut c in cards {
          match c.transaction() {
            Ok(mut t) => {
              match t.application_related_data() {
                Ok(ard) => {
                  if let Ok(app_data) = ard.application_id() {
                    println!("manufacturer_name = {:?}", app_data.manufacturer_name() );
                    println!("ident = {:?}", app_data.ident() );
                  }
                }
                Err(e) => {
                  println!("ard e={:?}", e);
                }
              }
            }
            Err(e) => {
              println!("transaction e={:?}", e);
            }
          }
        }
      }
      Err(e) => {
        println!("Got error reading PCSC cards: {:?}", e);
      }
    }
  }
}

fn visit_pcsc_cards() {
  use pcsc;
  
  println!("=== visit_pcsc_cards ===");

  let ctx = match pcsc::Context::establish(pcsc::Scope::User) {
        Ok(ctx) => ctx,
        Err(err) => {
            eprintln!("Failed to establish pcsc context: {}", err);
            return;
        }
    };

    // List available readers.
    let mut readers_buf = [0; 4096];
    let mut readers = match ctx.list_readers(&mut readers_buf) {
        Ok(readers) => readers,
        Err(err) => {
            eprintln!("Failed to list pcsc readers: {}", err);
            return;
        }
    };

    for reader in readers {
      match ctx.connect(reader, pcsc::ShareMode::Shared, pcsc::Protocols::ANY) {
          Ok(card) => {
            println!("got a card!");
            if let Ok(status) = card.status2_owned() {
              println!("card atr = {:?}", status.atr() );
              println!("card atr string = {:?}", String::from_utf8_lossy( status.atr() ) );
            }
          },
          Err(pcsc::Error::NoSmartcard) => {
              println!("A smartcard is not present in the reader.");
              return;
          }
          Err(err) => {
              eprintln!("Failed to connect to card: {}", err);
              return;
          }
      }
    }
}


async fn gui_main(args: &Args) {
  println!("Hello async gui_main runtime!");
  if let Err(e) = gui::gui::open_gui(args) {
    println!("Error running gui: {:?}", e);
  }
}


