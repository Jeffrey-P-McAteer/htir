
use crate::*;

#[test]
fn gen_config() {
    let mut c = config::Config::default();

    c.enrich_server();
    c.enrich_client();

    let socket = c.get_tcp_listen_socket();
    


}



