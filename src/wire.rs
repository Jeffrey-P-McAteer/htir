
use crate::*;

// WireMessage wraps all other messages; we use `flags` to
// determine how inner should be decoded.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WireMessageHeader<'a> {
  pub msg_flags: u64,
  #[serde(with = "serde_bytes")]
  pub inner: &'a [u8],
}

impl WireMessageHeader {
  pub fn get_msg_num(&self) -> u8 {
    return (self.msg_flags % 256) as u8;
  }
}

#[derive(Debug, Clone)]
pub enum WireMessage {

}

impl WireMessage {
  pub fn from_bytes(bytes: &[u8]) -> Result<WireMessage, Box<dyn std::error::Error>> {
    // First decode header
    let header = serde_bare::from_slice::<WireMessageHeader>(bytes)?;
    match header.get_msg_num() {
      0 => {
        std::unimplemented!()
      }
      unk => {
        return Err(error::MeiliError::new_boxed(""));
      }
    }
  }
  pub fn add_header(&self) -> WireMessageHeader {
    std::unimplemented!()
  }
}



// All Meili messages begin with a u64's worth of flags, and WireMessageZero exists so we can
// use the flags to allow backwards-compatible breaking message changes.
// We parse as WireMessageZero first, read the flags, then re-parse as whatever completely different
// message format the client has specified.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WireMessageZero {
  pub flags: u64,
}

// Clients send this to servers to request SQL query/insert/update actions.
#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WireMessageOne {
  pub flags: u64,

  pub sn: String,  // Server Name
  pub db: String,  // Database Name
  pub sql: String, // SQL payload

}


#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WireMessageTwo {
  pub flags: u64,
  pub num_rows: u64,
}

#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct WireMessageThree {
  pub flags: u64,
  pub columns: Vec<String>,
}

