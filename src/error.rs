

pub struct MeiliError {
    pub message: String,
}

impl MeiliError {
  pub fn new<I: Into<String>>(message: I) -> MeiliError {
    MeiliError {
      message: message.into()
    }
  }
  pub fn new_boxed<I: Into<String>>(message: I) -> Box<MeiliError> {
    Box::new(MeiliError::new(message))
  }
}

impl std::error::Error for MeiliError {
  fn source(&self) -> Option<&(dyn std::error::Error + 'static)> { None }
}

impl std::fmt::Display for MeiliError {
  fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
    write!(f, "{}", self.message)
  }
}

// A unique format for dubugging output
impl std::fmt::Debug for MeiliError {
  fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
    write!(
      f,
      "MeiliError {{ message: {} }}",
      self.message
    )
  }
}



