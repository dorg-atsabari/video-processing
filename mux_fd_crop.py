import av
from fractions import Fraction
import cv2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

trim_start_time = 510
trim_end_time = 525
duration = trim_end_time - trim_start_time

crop_width = 700
smoothing_factor = 0.15  # Lower = smoother (0.0-1.0), higher = more responsive

input_file_path = 'https://cdn-vl.replay.peech.ai/videos/ee8f42ab-fcde-495b-b914-daad9e4bc435/74e5e861-55f7-4c68-b5c8-a8a027a051e8'
output_file_path = './output_combined.mp4'

input_container = av.open(input_file_path)
output_container = av.open(output_file_path, 'w')
# Input Streams
input_video_stream = input_container.streams.video[0]
input_audio_stream = input_container.streams.audio[0]
# Output Video Stream
output_video_stream = output_container.add_stream(input_video_stream.codec.name, rate=Fraction(input_video_stream.average_rate))
output_video_stream.width = crop_width
output_video_stream.height = input_video_stream.height  # Use original video height
output_video_stream.pix_fmt = input_video_stream.pix_fmt
# Output Audio Stream
output_audio_stream = output_container.add_stream(input_audio_stream.codec.name, rate=input_audio_stream.rate)


seek_time = int(trim_start_time / input_video_stream.time_base)
input_container.seek(seek_time, stream=input_video_stream)

done: bool = False
smoothed_crop_x = None  # Track smoothed crop position

for packet in input_container.demux(input_video_stream, input_audio_stream):

    if done == True:
         break

    # Video
    if packet.stream.type == 'video':
        for frame in packet.decode():
            current_time = float(frame.pts * frame.time_base)
            progress = ((current_time - trim_start_time) / duration) * 100
            if 0 < progress < 100:
                print(f"{progress:.1f}%", end='\r', flush=True)
            
            if current_time < trim_start_time:
                continue

            if current_time >= trim_end_time:
                done = True
                break

            frame_img = frame.to_ndarray(format='bgr24')
            frame_height, frame_width = frame_img.shape[:2]

            # Face detection
            gray = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            # Calculate crop region centered on face (horizontally), full height
            crop_y = 0
            crop_height = frame_height  # Use full original height
            
            if len(faces) > 0:
                (x, y, w, h) = faces[0]
                if w > 100:
                    # Calculate center of face
                    face_center_x = x + w // 2
                    
                    # Calculate desired crop position centered on face horizontally
                    desired_crop_x = max(0, min(face_center_x - crop_width // 2, frame_width - crop_width))
                    
                    # Apply exponential smoothing to reduce jitter
                    if smoothed_crop_x is None:
                        smoothed_crop_x = desired_crop_x
                    else:
                        smoothed_crop_x = smoothing_factor * desired_crop_x + (1 - smoothing_factor) * smoothed_crop_x
                    
                    # Draw face detection overlay
                    cv2.rectangle(frame_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame_img, f"X:{x}", (x, y-5), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
                    cv2.putText(frame_img, f"Y:{y}", (x+w, y-5), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
                    cv2.putText(frame_img, f"W:{w}", (x + (w//2//2), y - 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
                    cv2.putText(frame_img, f"H:{h}", (x - 150, y + (h//2)), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
            
            # Use smoothed crop position (or default to 0 if no face detected yet)
            crop_x = int(smoothed_crop_x) if smoothed_crop_x is not None else 0
            # Ensure crop_x stays within frame bounds
            crop_x = max(0, min(crop_x, frame_width - crop_width))
            
            # Crop the frame (ensure crop doesn't exceed frame dimensions)
            actual_crop_width = min(crop_width, frame_width - crop_x)
            actual_crop_height = min(crop_height, frame_height - crop_y)
            frame_img = frame_img[crop_y:crop_y + actual_crop_height, crop_x:crop_x + actual_crop_width]
            
            # Resize if crop is smaller than desired (edge case)
            if frame_img.shape[0] != crop_height or frame_img.shape[1] != crop_width:
                frame_img = cv2.resize(frame_img, (crop_width, crop_height))

            new_frame = av.VideoFrame.from_ndarray(frame_img, format='bgr24')

            for encoded_packet in output_video_stream.encode(new_frame):
                output_container.mux(encoded_packet)
    
    ###########

    # Audio
    elif packet.stream.type == 'audio':
        if done:
            continue

        time_sec = packet.pts * packet.stream.time_base if packet.pts is not None else None
        if time_sec is not None and trim_start_time <= time_sec <= trim_end_time:
            for frame in packet.decode():
                time_base = frame.time_base
                if frame.pts is not None:
                    frame.pts = int(frame.pts - trim_start_time / time_base)
                    frame.dts = int(frame.dts - trim_start_time / time_base) if frame.dts is not None else None

                for packet_out in output_audio_stream.encode(frame):
                    output_container.mux(packet_out)

# Flush Video
for encoded_packet in output_video_stream.encode():
    output_container.mux(encoded_packet)

# Flush Audio
for encoded_packet in output_audio_stream.encode():
    output_container.mux(encoded_packet)