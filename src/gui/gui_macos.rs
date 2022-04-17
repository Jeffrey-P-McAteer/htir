
use crate::config::Args;

use cacao::macos::{
  App, AppDelegate,
  window::Window, window::WindowDelegate, window::WindowConfig, window::WindowStyle, window::WindowToolbarStyle,
  menu::Menu, menu::MenuItem,
  toolbar::Toolbar, toolbar::ToolbarDelegate, toolbar::ToolbarDisplayMode, toolbar::ToolbarItem, toolbar::ItemIdentifier
};
use cacao::button::Button;

pub fn open_gui(_args: &Args) -> Result<(), Box<dyn std::error::Error>> {
  let app = App::new("com.hello.world", BasicApp::default());
  
  App::set_menu(vec![
    Menu::new("Meili", vec![
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



#[derive(Debug)]
struct BasicApp {
    pub window: Window<BasicWindow>,
}

#[derive(Debug)]
struct BasicWindow {
  pub toolbar: Toolbar<BasicToolbar>,
  //pub content: WebView<WebViewInstance>, // TODO?
}

impl Default for BasicApp {
  fn default() -> Self {
      BasicApp {
        window: Window::with({
          let mut config = WindowConfig::default();
          config.set_styles(&[
            WindowStyle::UnifiedTitleAndToolbar,
            WindowStyle::Titled,
            WindowStyle::Closable,
            WindowStyle::Miniaturizable,
            WindowStyle::Resizable,
            // WindowStyle::FullSizeContentView, // someday
          ]);
          config.toolbar_style = WindowToolbarStyle::UnifiedCompact; // Big toolbars \o/
          config
        }, BasicWindow::default() ),
      }
    }
}

impl Default for BasicWindow {
  fn default() -> Self {
    BasicWindow {
      toolbar: Toolbar::new("Meili-Toolbar", BasicToolbar::default()),
    }
  }
}

impl WindowDelegate for BasicWindow {
    const NAME: &'static str = "Meili-Client-WindowDelegate";

    fn did_load(&mut self, window: Window) {
        window.set_minimum_content_size(400.0, 300.0);
        window.set_title("Meili Client");
        window.set_movable_by_background(true);
        window.set_titlebar_appears_transparent(false);
        window.set_toolbar(&self.toolbar);

    }
}

impl AppDelegate for BasicApp {
    fn did_finish_launching(&self) {
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

      let m = Menu::new("Meili", vec![
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
  const NAME: &'static str = "MeiliClientToolbar";

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
