




pub fn conditional_hide_console_if_double_clicked_on_windows() {
    #[cfg(target_os = "windows")]
    {
        // Check if we are run from the console or just launched with explorer.exe
        let mut console_proc_list_buff: Vec<u32> = vec![0; 16];
        let num_procs = unsafe {
            winapi::um::wincon::GetConsoleProcessList(console_proc_list_buff.as_mut_ptr(), 16)
        };
        //eprintln!("num_procs={:?}", num_procs);
        if num_procs == 1 || num_procs == 2 {
            // We were launched from explorer.exe, detatch the console
            unsafe { winapi::um::wincon::FreeConsole() };
        }
        // Otherwise do nothing, we want console messages when run from the console.
    }
}

