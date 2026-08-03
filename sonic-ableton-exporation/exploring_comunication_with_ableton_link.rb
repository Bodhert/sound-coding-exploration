define :midi_signal do |signal, port = "iac_driver_bus_1", channel = 1|
  midi_note_on signal, port: port , channel: channel
end

midi_signal(127) # stop all in ableton
##| midi_signal(16)
live_loop :orchestator do
  link_sync
  bar = 0  + tick + 1
  if bar == 1
    midi_signal(0)
  elsif bar == 2
    midi_signal(8)
  elsif bar == 10
    midi_signal(16)
  end
  puts bar
  sleep 1
end

