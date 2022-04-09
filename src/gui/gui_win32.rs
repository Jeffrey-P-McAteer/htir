
use crate::config::Args;

use winsafe::prelude::*;
use winsafe::{gui, POINT, SIZE, WinResult};

pub fn open_gui(args: &Args) -> Result<(), Box<dyn std::error::Error>> {
  if !args.debug {
    util::conditional_hide_console_if_double_clicked_on_windows();
  }
  let my = MyWindow::new();
  my.wnd.run_main(None)?
}

