


import av

input_file_path = './video-sources/84dYijIpWjQ.mp4'
output_file_path = './output_audio.m4a'

# Input
input_container = av.open(input_file_path)
input_audio_stream = input_container.streams.audio[0]

# Output
output_container = av.open(output_file_path, 'w')
output_audio_stream = output_container.add_stream(input_audio_stream.codec.name, rate=input_audio_stream.rate)

desired_start_time = 100
desired_end_time = 106

for frame in input_container.decode(audio=0):
    current_time = float(frame.pts * input_audio_stream.time_base)
    
    if current_time > desired_end_time:
        break

    if current_time < desired_start_time:
        continue
    
    for packet in output_audio_stream.encode(frame):
        output_container.mux(packet)

for packet in output_audio_stream.encode(None):
    output_container.mux(packet)

input_container.close()
output_container.close()

print('Done')