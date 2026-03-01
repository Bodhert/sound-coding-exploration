# important note on standard composition:
# make things durate 1,2,4,8,16,32,64...(power of two)
# or the inverse halving  1, 0.5, 0.25
# in pitch +- 12, 24,32 -> octaves


## another rule of thumb for composition, if I want things to feel finished
## end on the starting note

base_note = 44


##| live_loop :met do
##|   play 60
##|   sleep 1
##| end



## INTRO

with_fx :reverb, room: 0.5 do
  sample :arovane_beat_a, compress: 1, beat_stretch: 16
  puts sample_duration :arovane_beat_a
end

in_thread do
  with_fx :whammy, deltime: 0.01 do
    4.times do
      sample :ambi_haunted_hum, amp: 1, beat_stretch: 4, amp: 0.5
      sleep 4
    end
  end
end


use_synth :dark_ambience
play 55, sustain: 16, env_curve: 4
play 55 - 12.5, sustain: 16 , env_curve: 2
sleep 16

##| Bridge
with_fx :distortion, distort: 0.8 do
  use_synth :dsaw
  play 20, sustain: 5, attack: 4 , decay: 5
end
sleep 4

# second part

3.times do
  4.times do
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note + 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note + 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play base_note + 32, cuttoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
  
  4.times do
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note - 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note - 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play 2, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
end


# second section
with_fx :distortion, distort: 0.6 do
  use_synth :dsaw
  play 20, release: 16
end

4.times do
  sample :loop_3d_printer, beat_stretch: 1
  4.times do
    sample :bd_haus, amp: 5
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note - 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note - 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play 2, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
  4.times do
    sample :bd_haus, amp: 5
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note + 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note + 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play base_note + 32, cuttoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
end

with_fx :slicer, distort: 0.6  do
  use_synth :dtri
  play 20, release: 32
end

4.times do
  sample :loop_3d_printer, beat_stretch: 1, rate: -1
  4.times do
    sample :bd_haus, amp: 5
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note - 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note - 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play 2, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
  4.times do
    sample :bd_haus, amp: 5
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note + 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note + 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play base_note + 32, cuttoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
end

# final part
use_synth :bnoise
play 55, env_curve: 2, release: 16

4.times do
  sample :loop_3d_printer, beat_stretch: 1, rate: -1
  4.times do
    sample :bd_haus, amp: 5
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note - 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note - 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play 2, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
  4.times do
    sample :bd_haus, amp: 5
    play base_note,  release: 0.1, amp: 2
    sleep 0.125
    play base_note + 12, cutoff: 0.1, release: 0.1,  amp: 2
    sleep 0.125
    play base_note + 24, cutoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
    play base_note + 32, cuttoff: 0.1, release: 0.1, amp: 2
    sleep 0.125
  end
end
