
// Used for a multi-pass render which creates alpha from BG difference, keeping shadows!
#ifndef (SL_r)
  #declare SL_r = 1 ;
#end
#ifndef (SL_g)
  #declare SL_g = 1 ;
#end
#ifndef (SL_b)
  #declare SL_b = 1 ;
#end

#declare SceneLight = rgb<SL_r,SL_g,SL_b> ;

// Coordinate system: [left-right (x), up-down (y), near-far (z)]

global_settings {
  //assumed_gamma 1
  max_trace_level 15
}

background { color SceneLight }
box {
  <4,-0.6,2>, <-4,-0.61,-2>
  pigment {
      color SceneLight
  }
}

light_source { // Primary scene soft light just offset from center
  <0.5,6,3>
  color rgb<1.9,1.9,1.9> // lowest we can go w/o creating obnoxious 2d shadow
  area_light
  <2,0,0> <0,0,2>
  4,4 // numbers in directions
  adaptive 0  // 0,1,2,3...
  jitter // random softening
}


cylinder {
  <0.0,-0.6,0.0>
  <0.0,0.9,0.0>
  0.8
  texture {
    pigment {
      color
      <0.1,0.1,0.9> 
    }
    finish {
      specular
      0.6 
    }
    /*normal {
      marble
      0.25
      scale
      0.5 
    }*/
  }
  rotate
  <0,0,0> 
}

camera {
  perspective
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

