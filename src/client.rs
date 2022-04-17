
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
        cli_main(&url, &args);
      }
      else {
        gui_main(&args);
      }
    }

  });

  Ok(())
}

fn cli_main(url: &str, _args: &Args) {
  println!("Hello async cli_main runtime! url={:?}", url);
}

fn gui_main(args: &Args) {
  println!("Hello async gui_main runtime!");
  if let Err(e) = gui::gui::open_gui(args) {
    println!("Error running gui: {:?}", e);
  }
}


