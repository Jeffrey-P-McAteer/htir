
use crate::config::Args;

use cacao::macos::{App, AppDelegate, menu::Menu, menu::MenuItem};
use cacao::macos::window::Window;

pub fn open_gui(_args: &Args) -> Result<(), Box<dyn std::error::Error>> {
  App::new("com.hello.world", BasicApp::default()).run();
  Ok(())
}



#[derive(Default)]
struct BasicApp {
    window: Window
}

impl AppDelegate for BasicApp {
    fn did_finish_launching(&self) {
        println!("BasicApp.did_finish_launching()");
        self.window.set_minimum_content_size(400., 400.);
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
    fn dock_menu(&self) -> Option<Menu> {
      println!("BasicApp.dock_menu()");

      let m = Menu::new("HTIR", vec![
        MenuItem::New("Hello World Menu Item").action(|| {
          println!("Hello World Menu Item clicked!");
        }),
        MenuItem::EnterFullScreen,
        MenuItem::CloseWindow,
        MenuItem::Quit,
      ]);

      return m;
    }
}

