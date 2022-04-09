
use tokio::runtime::{Builder};
use clap::Parser;

use htir::*;

#[derive(Parser, Debug, Default)]
#[clap(author, version, about, long_about = None)]
pub struct Args {
  #[clap(short, long)]
  pub open_gui: bool,

  #[clap(short, long)]
  pub debug: bool,

  pub url: Option<String>,

}


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
  if !args.debug {
    util::conditional_hide_console_if_double_clicked_on_windows();
  }
  println!("Hello async gui_main runtime!");



}


