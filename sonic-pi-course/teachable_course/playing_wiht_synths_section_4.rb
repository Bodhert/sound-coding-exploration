use_synth :blade

vibratos = [2,4,6,8,10,12]
vibratos.each do |vibrato|
  play (chord :e, :minor)[vibrato], sustain: vibrato, vibrato_rate: vibrato
  sleep 4
end