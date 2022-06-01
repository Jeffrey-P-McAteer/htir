
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

  // Test access to OpenPGP credentials.
  // This should cover a ton of useful identity management systems.

  //use openpgp_card::OpenPgp;
  //use openpgp_card_pcsc::PcscBackend;
  use openpgp_card::CardBackend;

  for mode in [Some(pcsc::ShareMode::Exclusive), Some(pcsc::ShareMode::Shared), None, Some(pcsc::ShareMode::Direct)] {
    println!("Querying for cards in mode={:?}", mode);
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

async fn gui_main(args: &Args) {
  println!("Hello async gui_main runtime!");
  if let Err(e) = gui::gui::open_gui(args) {
    println!("Error running gui: {:?}", e);
  }
}


