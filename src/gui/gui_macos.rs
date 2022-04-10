
use crate::config::Args;

use std::io::Write;

use cacao::macos::{App, AppDelegate, menu::Menu, menu::MenuItem};
use cacao::macos::window::Window;

pub fn open_gui(_args: &Args) -> Result<(), Box<dyn std::error::Error>> {
  let app = App::new("com.hello.world", BasicApp::default());
  
  App::set_menu(vec![
    Menu::new("HTIR", vec![
      MenuItem::new("Hello World Menu Item").action(|| {
        println!("Hello World Menu Item clicked!");
        if let Err(error) = std::io::stdout().flush() {
            println!("std::io::stdout().flush() error={:?}", error);
        }
      }),
      MenuItem::EnterFullScreen,
      MenuItem::CloseWindow,
      MenuItem::Quit,
    ]),
    Menu::new("Edit", vec![
      MenuItem::new("Edit Menu Item").action(|| {
        println!("Edit Menu Item clicked!");
        if let Err(error) = std::io::stdout().flush() {
            println!("std::io::stdout().flush() error={:?}", error);
        }
      }),
    ]),
  ]);

  app.run();

  Ok(())
}



#[derive(Default)]
struct BasicApp {
    window: Window
}

impl AppDelegate for BasicApp {
    fn did_finish_launching(&self) {
        println!("BasicApp.did_finish_launching()");
        self.window.set_minimum_content_size(400.0, 300.0);
        self.window.set_title("Hello World!");
        self.window.show();
    }
    fn will_terminate(&self) {
      println!("BasicApp.will_terminate()");
    }
    fn should_terminate_after_last_window_closed(&self) -> bool {
      println!("BasicApp.should_terminate_after_last_window_closed()");
      return true;
    }
    /*fn dock_menu(&self) -> Option<Menu> {
      println!("BasicApp.dock_menu()");

      let m = Menu::new("HTIR", vec![
        MenuItem::new("Hello World Menu Item").action(|| {
          println!("Hello World Menu Item clicked!");
          if let Err(error) = std::io::stdout().flush() {
              println!("std::io::stdout().flush() error={:?}", error);
          }
        }),
        MenuItem::EnterFullScreen,
        MenuItem::CloseWindow,
        MenuItem::Quit,
      ]);

      return Some(m);
    }*/
}

