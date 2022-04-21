
use crate::*;

#[test]
fn config_memory() {
    let mut c = config::Config::default();

    c.enrich_server();
    c.enrich_client();

    let socket = c.get_tcp_listen_socket();

}


#[test]
fn config_empty_file() {
    let mut c = config::read_config(Some("/dev/null")); // TODO make test work on windorks as well
    

}


