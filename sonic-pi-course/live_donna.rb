# Welcome to Sonic Pi
use_bpm 125

notes = [:c2, :c2, :c3, :c3, :g2, :g2, :as2, :as2]


use_synth :tb303

16.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 0)
end

4.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 2)
end

8.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 4)
end

2.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 0)
end

2.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 2)
end

2.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 4)
end

2.times do
  play_pattern_timed(notes, [0.25], attack: 0, release: 0.125, pitch: 6)
end


