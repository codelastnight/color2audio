import mido 
msg = mido.Message('note_on', note=60)

ports = mido.get_output_names()

outport = mido.open_output(ports[1])
outport.send(msg)