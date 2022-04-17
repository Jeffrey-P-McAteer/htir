
/**
 * All per-OS GUI implementations use the meili lib to perform operations
 * and declare the same public API, this module merely renames them so
 * client code does not have to care what the backend GUI target is.
 * OS-specific things may be wrapped in `Option<>` types, and all `Result<>` types will
 * use `dyn std::error::Error` to avoid callers having to care about implementation details.
 */

// Use win32 graphics if windows & native UI enabled

#[cfg(all(target_os = "windows", not(feature = "force_gtk_ui")))]
pub mod gui_win32;
#[cfg(all(target_os = "windows", not(feature = "force_gtk_ui")))]
pub use gui_win32 as gui;

// Use cocoa graphics if macos & native UI enabled

#[cfg(all(target_os = "macos", not(feature = "force_gtk_ui")))]
pub mod gui_macos;
#[cfg(all(target_os = "macos", not(feature = "force_gtk_ui")))]
pub use gui_macos as gui;

// Use GTK windows if feature=native_ui not specified OR we are compiling for a unix variant.

#[cfg(any(target_os = "linux", target_os = "freebsd", target_os = "openbsd", target_os = "netbsd", feature = "force_gtk_ui"))]
pub mod gui_unix_gtk;
#[cfg(any(target_os = "linux", target_os = "freebsd", target_os = "openbsd", target_os = "netbsd", feature = "force_gtk_ui"))]
pub use gui_unix_gtk as gui;

