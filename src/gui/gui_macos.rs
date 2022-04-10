
use crate::config::Args;

use std::io::Write;

use cacao::macos::{
  App, AppDelegate,
  window::Window,
  menu::Menu, menu::MenuItem,
  toolbar::Toolbar, toolbar::ToolbarDelegate, toolbar::ToolbarDisplayMode, toolbar::ToolbarItem, toolbar::ItemIdentifier
};

pub fn open_gui(_args: &Args) -> Result<(), Box<dyn std::error::Error>> {
  let app = App::new("com.hello.world", BasicApp::default());
  
  App::set_menu(vec![
    Menu::new("HTIR", vec![
      MenuItem::new("Hello World Menu Item").action(|| {
        println!("Hello World Menu Item clicked!");
        
      }),
      MenuItem::EnterFullScreen,
      MenuItem::CloseWindow,
      MenuItem::Quit,
    ]),
    Menu::new("Edit", vec![
      MenuItem::new("Edit Menu Item").action(|| {
        println!("Edit Menu Item clicked!");
        
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
        self.window.set_minimum_content_size(400.0, 300.0);
        self.window.set_title("HTIR Client");
        self.window.set_movable_by_background(true);
        self.window.set_titlebar_appears_transparent(false);
        self.window.set_toolbar(BasicToolbar::default());

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
        }),
        MenuItem::EnterFullScreen,
        MenuItem::CloseWindow,
        MenuItem::Quit,
      ]);

      return Some(m);
    }*/
}


#[derive(Debug)]
pub struct BasicToolbar(ToolbarItem);

impl Default for BasicToolbar {
    fn default() -> Self {
        BasicToolbar({
            let mut item = ToolbarItem::new("AddTodoButton");
            item.set_title("Add Todo");
            item.set_button(Button::new("+ New"));
            
            item.set_action(|| {
              println!("AddTodoButton clicked!");
                //dispatch_ui(Message::OpenNewTodoSheet);
            });

            item
        })
    }
}

impl ToolbarDelegate for BasicToolbar {
  const NAME: &'static str = "HTIRClientToolbar";

  fn did_load(&mut self, toolbar: Toolbar) {
      toolbar.set_display_mode(ToolbarDisplayMode::IconOnly);
  }

  fn allowed_item_identifiers(&self) -> Vec<ItemIdentifier> {
      vec![ItemIdentifier::Custom("AddTodoButton")]
  }

  fn default_item_identifiers(&self) -> Vec<ItemIdentifier> {
      vec![ItemIdentifier::Custom("AddTodoButton")]
  }

  // We only have one item, so we don't care about the identifier.
  fn item_for(&self, _identifier: &str) -> &ToolbarItem {
      &self.0
  }
}
