
use htir::*;

use pyo3::prelude::*;

#[pyfunction]
fn test01(some_str: String) -> PyResult<String> {
    let c = config::read_config::<&str>(None);
    Ok(format!("Hello Python from HTIR, you said: {}. Our config is {:?}", &some_str, &c))
}

#[pymodule]
fn htir(_py: Python, m: &PyModule) -> PyResult<()> {
  m.add_function(wrap_pyfunction!(test01, m)?)?;
  Ok(())
}



