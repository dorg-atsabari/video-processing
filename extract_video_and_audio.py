
import av
from fractions import Fraction

trim_start_time = 30
trim_end_time = 45

input_file_path = './video-sources/84dYijIpWjQ.mp4'
output_video_file_path = './output_video.mp4'
output_audio_file_path = './output_audio.m4a'

input_container = av.open(input_file_path)
output_video_container = av.open(output_video_file_path, 'w')
output_audio_container = av.open(output_audio_file_path, 'w')

input_video_stream = input_container.streams.video[0]
input_audio_stream = input_container.streams.audio[0]

output_video_stream = output_video_container.add_stream(input_video_stream.codec.name, rate=Fraction(input_video_stream.average_rate))
output_video_stream.width = input_video_stream.width
output_video_stream.height = input_video_stream.height
output_video_stream.pix_fmt = input_video_stream.pix_fmt

output_audio_stream = output_audio_container.add_stream(input_audio_stream.codec.name, rate=input_audio_stream.rate)

input_container.seek(int(trim_start_time / input_video_stream.time_base), stream=input_video_stream)

print('Extracting video...')

for frame in input_container.decode(video=0):
    current_time = float(frame.pts * frame.time_base)
    print(current_time, end='\r', flush=True)

    if current_time < trim_start_time:
        continue

    if current_time >= trim_end_time:
        break

    frame_img = frame.to_ndarray(format='bgr24')
    
    new_frame = av.VideoFrame.from_ndarray(frame_img, format='bgr24')

    for packet in output_video_stream.encode(new_frame):
        output_video_container.mux(packet)

# Flushing
for packet in output_video_stream.encode():
        output_video_container.mux(packet)

print('Done')

input_container.seek(int(trim_start_time / input_audio_stream.time_base), stream=input_audio_stream)

print('Extracting audio file...')

for frame in input_container.decode(audio=0):
    current_time = float(frame.pts * frame.time_base)
    print(current_time, end='\r', flush=True)

    if current_time >= trim_end_time:
        break

    for packet in output_audio_stream.encode(frame):
        output_audio_container.mux(packet)

for packet in output_audio_stream.encode():
        output_audio_container.mux(packet)

print('Done')


print('Done')