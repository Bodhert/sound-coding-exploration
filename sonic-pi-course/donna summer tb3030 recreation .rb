# Welcome to Sonic Pi
use_bpm 125

notes = [:c2, :c2, :c3, :c3, :g2, :g2, :as2, :as2]


pitch = 0
# debug
live_loop :tb do
  tick
  # #| if look == 0
  ##|   tick_set 48
  ##| end
  
  if look == 16 or look == 32 or look == 40 or look == 50 or look == 52
    pitch += 3
  elsif look == 48
    pitch = 0
  elsif look == 54
    pitch = 0
    tick_set 0
  end
  
  puts look
  
  use_synth :tb303
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: pitch)
end