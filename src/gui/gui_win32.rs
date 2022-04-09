
use crate::config::Args;

pub fn open_gui(args: &Args) {
  if !args.debug {
    util::conditional_hide_console_if_double_clicked_on_windows();
  }
  std::unimplemented!()
}

