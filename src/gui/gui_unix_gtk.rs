
use crate::config::Args;

use gtk4::prelude::*;
use gtk4::{Application, ApplicationWindow, /*Button*/};
use glib;

pub fn open_gui(_args: &Args) -> Result<(), Box<dyn std::error::Error>> {
  let application = Application::builder()
      .application_id("pw.jmcateer.htir-client")
      .build();

  application.connect_activate(|app| {
      let window = ApplicationWindow::builder()
          .application(app)
          .title("HTIR Client")
          .decorated(true) // TODO use user preference?
          .default_width(400)
          .default_height(300)
          .build();

      let header_bar = gtk4::HeaderBar::new();
      window.set_titlebar(Some(&header_bar));

      let search_button = gtk4::ToggleButton::new();
    search_button.set_icon_name("system-search-symbolic");
    header_bar.pack_end(&search_button);

    let container = gtk4::Box::new(gtk4::Orientation::Vertical, 6);
    window.set_child(Some(&container));

    let search_bar = gtk4::SearchBar::builder()
        .valign(gtk4::Align::Start)
        .key_capture_widget(&window)
        .build();

    container.append(&search_bar);

    search_button
        .bind_property("active", &search_bar, "search-mode-enabled")
        .flags(glib::BindingFlags::SYNC_CREATE | glib::BindingFlags::BIDIRECTIONAL)
        .build();

    let entry = gtk4::SearchEntry::new();
    entry.set_hexpand(true);
    search_bar.set_child(Some(&entry));

    let label = gtk4::Label::builder()
        .label("Type to start search")
        .vexpand(true)
        .halign(gtk4::Align::Center)
        .valign(gtk4::Align::Center)
        .css_classes(vec!["large-title".to_string()])
        .build();

    container.append(&label);

    entry.connect_search_started(glib::clone!(@weak search_button => move |_| {
        search_button.set_active(true);
    }));

    entry.connect_stop_search(glib::clone!(@weak search_button => move |_| {
        search_button.set_active(false);
    }));

    entry.connect_search_changed(glib::clone!(@weak label => move |entry| {
        if entry.text() != "" {
            label.set_text(&entry.text());
        } else {
            label.set_text("Type to start search");
        }
    }));

      
      window.show();
  });

  application.run();
  
  Ok(())
}



