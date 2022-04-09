
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


#[derive(Clone)]
pub struct MyWindow {
    wnd:       gui::WindowMain, // responsible for managing the window
    btn_hello: gui::Button,     // a button
}

impl MyWindow {
    pub fn new() -> MyWindow {
        let wnd = gui::WindowMain::new( // instantiate the window manager
            gui::WindowMainOpts {
                title: "My window title".to_owned(),
                size: SIZE::new(300, 150),
                ..Default::default() // leave all other options as default
            },
        );

        let btn_hello = gui::Button::new(
            &wnd, // the window manager is the parent of our button
            gui::ButtonOpts {
                text: "&Click me".to_owned(),
                position: POINT::new(20, 20),
                ..Default::default()
            },
        );

        let new_self = Self { wnd, btn_hello };
        new_self.events(); // attach our events
        new_self
    }

    fn events(&self) {
        self.btn_hello.on().bn_clicked({
            let wnd = self.wnd.clone(); // clone so it can be passed into the closure
            move || {
                wnd.hwnd().SetWindowText("Hello, world!")?;
                Ok(())
            }
        });
    }
}
