background {
  color
  <0.75,0.75,0.85> 
}
light_source {
  <0,0,0>
  color
  <0.9,0.9,0.9>
  translate
  <0,5,5.0> 
}
light_source {
  <0,0,0>
  color
  <0.15,0.15,0.25>
  translate
  <1,6,4.0> 
}
cylinder {
  <0.0,-0.6,0.0>
  <0.0,0.6,0.0>
  0.6
  texture {
    pigment {
      color
      <0.1,0.1,0.9> 
    }
    finish {
      specular
      0.6 
    }
    normal {
      marble
      0.25
      scale
      0.5 
    } 
  }
  rotate
  <0,0,0> 
}
camera {
  location
  <0.0,1.4,4.0>
  direction
  <0,0,1.5>
  look_at
  <0,0.3,0>
  blur_samples
  50
  right
  <1.0,0,0>
  right
  <1.0,0,0> 
}
global_settings{
  
}