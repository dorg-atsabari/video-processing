


import av

input_file_path = 'https://cdn-vl.replay.peech.ai/videos/ee8f42ab-fcde-495b-b914-daad9e4bc435/74e5e861-55f7-4c68-b5c8-a8a027a051e8'
output_file_path = './output_audio.m4a'

# Input
input_container = av.open(input_file_path)
input_audio_stream = input_container.streams.audio[0]

# Output
output_container = av.open(output_file_path, 'w')
output_audio_stream = output_container.add_stream(input_audio_stream.codec.name, rate=input_audio_stream.rate)
output_audio_stream.bit_rate = input_audio_stream.bit_rate

desired_start_time = 100
desired_end_time = 150

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