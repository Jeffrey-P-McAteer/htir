
/**
 * All per-OS GUI implementations use the htir lib to perform operations
 * and declare the same public API, this module merely renames them so
 * client code does not have to care what the backend GUI target is.
 * OS-specific things may be wrapped in `Option<>` types, and all `Result<>` types will
 * use `dyn std::error::Error` to avoid callers having to care about implementation details.
 */

#[cfg(target_os = "windows")]
pub mod gui_win32;
#[cfg(target_os = "windows")]
pub use gui_win32 as gui;

#[cfg(target_os = "macos")]
pub mod gui_macos;
#[cfg(target_os = "macos")]
pub use gui_macos as gui;

#[cfg(any(target_os = "linux", target_os = "freebsd", target_os = "openbsd", target_os = "netbsd"))]
pub mod gui_unix_gtk;
#[cfg(any(target_os = "linux", target_os = "freebsd", target_os = "openbsd", target_os = "netbsd"))]
pub use gui_unix_gtk as gui;

