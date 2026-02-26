import av
from fractions import Fraction
import cv2
from face_detector import FaceDetector

# Configuration
trim_start_time = 30
trim_end_time = 50
duration = trim_end_time - trim_start_time

# Analysis mode - analyze face detections to determine optimal min_size
analyze_mode = True  # Set to True to run analysis first, False to process normally
face_min_size = 120  # Minimum face size in pixels (can be auto-determined in analyze_mode)

crop_width = 600
smoothing_factor = 0.1  # Lower = smoother (0.0-1.0), higher = more responsive
dead_zone_threshold = 30  # Pixels - ignore movements smaller than this to prevent micro-jitter
large_movement_threshold = 80  # Pixels - if movement exceeds this, snap immediately (no sliding)

# Detection failure handling
hold_on_missing_detection = True  # Whether to hold position when detection fails
max_hold_frames = None  # Maximum frames to hold (None = hold indefinitely)

input_file_path = 'https://cdn-vl.replay.peech.ai/videos/ee8f42ab-fcde-495b-b914-daad9e4bc435/74e5e861-55f7-4c68-b5c8-a8a027a051e8'
output_file_path = './output_combined.mp4'

# Initialize face detector
face_detector_instance = FaceDetector()


def analyze_face_detections(input_file, start_time, end_time, sample_rate=1):
    """
    Analyze face detections in the video to determine optimal min_size.
    
    Args:
        input_file: Path to input video
        start_time: Start time in seconds
        end_time: End time in seconds
        sample_rate: Analyze every Nth frame (1 = every frame, 2 = every other frame, etc.)
    
    Returns:
        Suggested min_size value
    """
    import statistics
    
    print("\n" + "="*60)
    print("FACE DETECTION ANALYSIS MODE")
    print("="*60)
    print(f"Analyzing video from {start_time}s to {end_time}s...")
    print("This will help determine the optimal min_size to filter false positives.\n")
    
    container = av.open(input_file)
    video_stream = container.streams.video[0]
    
    # Seek to start
    seek_time = int(start_time / video_stream.time_base)
    container.seek(seek_time, stream=video_stream)
    
    # Collect statistics
    all_widths = []
    all_heights = []
    all_aspect_ratios = []
    frames_with_faces = 0
    frames_without_faces = 0
    total_frames_analyzed = 0
    frame_count = 0
    
    # Detect faces without min_size filter to see everything
    for packet in container.demux(video_stream):
        for frame in packet.decode():
            current_time = float(frame.pts * frame.time_base)
            
            if current_time < start_time:
                continue
            
            if current_time >= end_time:
                break
            
            # Sample frames
            frame_count += 1
            if frame_count % sample_rate != 0:
                continue
            
            total_frames_analyzed += 1
            
            # Show progress
            progress = ((current_time - start_time) / (end_time - start_time)) * 100
            print(f"Analyzing: {progress:.1f}%", end='\r', flush=True)
            
            frame_img = frame.to_ndarray(format='bgr24')
            frame_height, frame_width = frame_img.shape[:2]
            
            # Detect all faces (with very low min_size to catch everything)
            faces = face_detector_instance.detect_faces(frame_img, min_confidence=0.5, min_size=20)
            
            if faces:
                frames_with_faces += 1
                for (x, y, w, h) in faces:
                    all_widths.append(w)
                    all_heights.append(h)
                    aspect_ratio = w / h if h > 0 else 0
                    all_aspect_ratios.append(aspect_ratio)
            else:
                frames_without_faces += 1
    
    container.close()
    
    # Analyze statistics
    print("\n\n" + "="*60)
    print("ANALYSIS RESULTS")
    print("="*60)
    
    if not all_widths:
        print("WARNING: No faces detected in the analyzed segment!")
        print("Suggested min_size: 80 (default)")
        return 80
    
    # Sort for percentile calculations
    all_widths.sort()
    all_heights.sort()
    
    # Calculate statistics
    detection_rate = (frames_with_faces / total_frames_analyzed * 100) if total_frames_analyzed > 0 else 0
    
    print(f"\nFrames analyzed: {total_frames_analyzed}")
    print(f"Frames with faces: {frames_with_faces} ({detection_rate:.1f}%)")
    print(f"Frames without faces: {frames_without_faces}")
    print(f"Total face detections: {len(all_widths)}")
    
    print(f"\n--- Face Width Statistics ---")
    print(f"Min:      {min(all_widths)} px")
    print(f"Max:      {max(all_widths)} px")
    print(f"Median:   {statistics.median(all_widths):.0f} px")
    print(f"Mean:     {statistics.mean(all_widths):.0f} px")
    
    # Percentiles
    p5 = all_widths[int(len(all_widths) * 0.05)]
    p10 = all_widths[int(len(all_widths) * 0.10)]
    p25 = all_widths[int(len(all_widths) * 0.25)]
    
    print(f"\n--- Percentiles (Width) ---")
    print(f"5th:  {p5} px  (95% of detections are larger)")
    print(f"10th: {p10} px  (90% of detections are larger)")
    print(f"25th: {p25} px  (75% of detections are larger)")
    
    print(f"\n--- Face Height Statistics ---")
    print(f"Min:      {min(all_heights)} px")
    print(f"Max:      {max(all_heights)} px")
    print(f"Median:   {statistics.median(all_heights):.0f} px")
    
    # Suggest min_size based on analysis
    # Use 10th percentile to filter out smallest 10% (likely false positives)
    # But ensure it's not too aggressive
    suggested_min_size = max(p10, 80)  # At least 80px
    
    print(f"\n{'='*60}")
    print(f"RECOMMENDATION")
    print(f"{'='*60}")
    print(f"\nSuggested min_size: {suggested_min_size} px")
    print(f"  - Filters out smallest 10% of detections (likely false positives)")
    print(f"  - Keeps {100 - 10:.0f}% of detected faces")
    print(f"  - Balance between accuracy and false positive reduction")
    
    if p5 < 50:
        print(f"\nWARNING: Many very small detections found (< 50px)")
        print(f"         These are likely false positives (hands, etc.)")
        print(f"         Consider using min_size >= {max(p10, 100)}")
    
    print(f"\n{'='*60}\n")
    
    return int(suggested_min_size)


def update_crop_position(frame_img, smoothed_crop_x, crop_width, frame_width, 
                         last_known_crop_x=None, consecutive_misses=0):
    """
    Detect face and update smoothed crop position with adaptive smoothing.
    
    Args:
        frame_img: Image frame
        smoothed_crop_x: Current smoothed crop position
        crop_width: Width of crop
        frame_width: Width of frame
        last_known_crop_x: Last known good crop position (for holding on detection failure)
        consecutive_misses: Number of consecutive frames without detection
    
    Returns:
        Tuple of (smoothed_crop_x, last_known_crop_x, consecutive_misses)
    """
    frame_height, frame_width_img = frame_img.shape[:2]
    
    # Use face detector to get first face
    face = face_detector_instance.get_first_face(frame_img, min_confidence=0.5, min_size=face_min_size)
    
    if face is not None:
        (x, y, w, h) = face
        
        # Debug: Check if detection is outside frame bounds
        if x < 0 or y < 0 or x + w > frame_width_img or y + h > frame_height:
            print(f"Warning: Face detection outside bounds - x:{x}, y:{y}, w:{w}, h:{h}, frame:{frame_width_img}x{frame_height}")
        
        # Calculate center of face
        face_center_x = x + w // 2
        desired_crop_x = max(0, min(face_center_x - crop_width // 2, frame_width_img - crop_width))
        
        # Reset consecutive misses counter
        consecutive_misses = 0
        
        # Apply adaptive exponential smoothing with dead zone
        if smoothed_crop_x is None:
            smoothed_crop_x = desired_crop_x
        else:
            movement_distance = abs(desired_crop_x - smoothed_crop_x)
            
            if movement_distance < dead_zone_threshold:
                # Dead zone: apply very light smoothing to dampen micro-jitter
                # Use much lower smoothing factor to barely move
                very_light_smoothing = 0.05
                smoothed_crop_x = very_light_smoothing * desired_crop_x + (1 - very_light_smoothing) * smoothed_crop_x
            elif movement_distance >= large_movement_threshold:
                # Large movement: snap immediately (no sliding animation)
                smoothed_crop_x = desired_crop_x
            else:
                # Medium movement: use smooth tracking
                smoothed_crop_x = smoothing_factor * desired_crop_x + (1 - smoothing_factor) * smoothed_crop_x
        
        # Update last known good position AFTER smoothing (hold at actual smoothed position)
        last_known_crop_x = smoothed_crop_x
        
        # Draw face detection overlay using actual detected coordinates
        # Clamp rectangle coordinates only to prevent OpenCV errors (but show actual detection)
        x1 = max(0, min(x, frame_width_img - 1))
        y1 = max(0, min(y, frame_height - 1))
        x2 = max(0, min(x + w, frame_width_img - 1))
        y2 = max(0, min(y + h, frame_height - 1))
        cv2.rectangle(frame_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Draw text showing ACTUAL detected values (not clamped)
        # Position text within frame bounds but display actual values
        text_y = max(20, min(y - 5, frame_height - 10))  # Ensure text is visible
        text_x1 = max(5, min(x, frame_width_img - 150))  # X label position
        text_x2 = max(5, min(x + w, frame_width_img - 150))  # Y label position
        text_x3 = max(5, min(x + (w//2//2), frame_width_img - 150))  # W label position
        text_x4 = max(5, min(x - 150, frame_width_img - 150))  # H label position
        text_y2 = max(20, min(y - 50, frame_height - 10))  # W label Y position
        text_y3 = max(20, min(y + (h//2), frame_height - 10))  # H label Y position
        
        # Display actual detected values (x, y, w, h) - not clamped
        cv2.putText(frame_img, f"X:{x}", (text_x1, text_y), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
        cv2.putText(frame_img, f"Y:{y}", (text_x2, text_y), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
        cv2.putText(frame_img, f"W:{w}", (text_x3, text_y2), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
        cv2.putText(frame_img, f"H:{h}", (text_x4, text_y3), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 255, 255), 2, cv2.LINE_4)
    else:
        # No face detected - use last known good position if available
        if hold_on_missing_detection and last_known_crop_x is not None:
            # Check if we should still hold (max_hold_frames check)
            if max_hold_frames is None or consecutive_misses < max_hold_frames:
                # Hold position at last known good location
                smoothed_crop_x = last_known_crop_x
                consecutive_misses += 1
            # If max_hold_frames exceeded, let smoothed_crop_x remain unchanged
        # If no last known position or hold disabled, keep current smoothed_crop_x unchanged
    
    return smoothed_crop_x, last_known_crop_x, consecutive_misses


def crop_frame(frame_img, smoothed_crop_x, crop_width, frame_width, frame_height):
    """Crop the frame based on smoothed crop position."""
    # Calculate crop position
    crop_x = int(smoothed_crop_x) if smoothed_crop_x is not None else 0
    crop_x = max(0, min(crop_x, frame_width - crop_width))
    crop_y = 0
    crop_height = frame_height
    
    # Crop the frame
    actual_crop_width = min(crop_width, frame_width - crop_x)
    actual_crop_height = min(crop_height, frame_height - crop_y)
    frame_img = frame_img[crop_y:crop_y + actual_crop_height, crop_x:crop_x + actual_crop_width]
    
    # Resize if crop is smaller than desired (edge case)
    if frame_img.shape[0] != crop_height or frame_img.shape[1] != crop_width:
        frame_img = cv2.resize(frame_img, (crop_width, crop_height))
    
    return frame_img


def process_video_frame(frame, smoothed_crop_x, crop_width, trim_start_time, trim_end_time, duration,
                        last_known_crop_x=None, consecutive_misses=0):
    """
    Process a single video frame: detect face, update crop, and return cropped frame.
    
    Returns:
        Tuple of (new_frame, smoothed_crop_x, is_done, last_known_crop_x, consecutive_misses)
    """
    current_time = float(frame.pts * frame.time_base)
    
    if current_time < trim_start_time:
        return None, smoothed_crop_x, False, last_known_crop_x, consecutive_misses
    
    if current_time >= trim_end_time:
        return None, smoothed_crop_x, True, last_known_crop_x, consecutive_misses
    
    # Show progress
    if duration > 0:
        progress = ((current_time - trim_start_time) / duration) * 100
        if 0 <= progress <= 100:
            print(f"{progress:.1f}%", end='\r', flush=True)
    
    frame_img = frame.to_ndarray(format='bgr24')
    frame_height, frame_width = frame_img.shape[:2]
    
    # Update crop position based on face detection
    smoothed_crop_x, last_known_crop_x, consecutive_misses = update_crop_position(
        frame_img, smoothed_crop_x, crop_width, frame_width, 
        last_known_crop_x, consecutive_misses
    )
    
    # Crop the frame
    frame_img = crop_frame(frame_img, smoothed_crop_x, crop_width, frame_width, frame_height)
    
    new_frame = av.VideoFrame.from_ndarray(frame_img, format='bgr24')
    return new_frame, smoothed_crop_x, False, last_known_crop_x, consecutive_misses


def process_audio_packet(packet, trim_start_time, trim_end_time, output_audio_stream, output_container):
    """Process audio packet and write to output."""
    if packet.pts is None:
        return
    
    time_sec = packet.pts * packet.stream.time_base
    if trim_start_time <= time_sec <= trim_end_time:
        for frame in packet.decode():
            time_base = frame.time_base
            if frame.pts is not None:
                frame.pts = int(frame.pts - trim_start_time / time_base)
                frame.dts = int(frame.dts - trim_start_time / time_base) if frame.dts is not None else None
            
            for packet_out in output_audio_stream.encode(frame):
                output_container.mux(packet_out)

# Run analysis mode if enabled
if analyze_mode:
    suggested_min_size = analyze_face_detections(input_file_path, trim_start_time, trim_end_time, sample_rate=2)
    
    # Ask user if they want to use the suggested value
    print(f"Current face_min_size: {face_min_size}")
    print(f"Suggested face_min_size: {suggested_min_size}")
    
    user_input = input("\nUse suggested min_size? (y/n, or enter custom value): ").strip().lower()
    
    if user_input == 'y' or user_input == 'yes':
        face_min_size = suggested_min_size
        print(f"✓ Using suggested min_size: {face_min_size}")
    elif user_input.isdigit():
        face_min_size = int(user_input)
        print(f"✓ Using custom min_size: {face_min_size}")
    else:
        print(f"✓ Keeping current min_size: {face_min_size}")
    
    # Ask if they want to continue processing
    continue_processing = input("\nContinue with video processing? (y/n): ").strip().lower()
    
    if continue_processing != 'y' and continue_processing != 'yes':
        print("\nAnalysis complete. Exiting without processing video.")
        print(f"To process with the suggested min_size, set face_min_size={face_min_size} and analyze_mode=False")
        exit(0)
    
    print("\n" + "="*60)
    print("STARTING VIDEO PROCESSING")
    print("="*60)
    print(f"Using face_min_size: {face_min_size}\n")

# Setup containers and streams
input_container = av.open(input_file_path)
output_container = av.open(output_file_path, 'w')

input_video_stream = input_container.streams.video[0]
input_audio_stream = input_container.streams.audio[0]

# Output Video Stream
output_video_stream = output_container.add_stream(input_video_stream.codec.name, rate=Fraction(input_video_stream.average_rate))
output_video_stream.width = crop_width
output_video_stream.height = input_video_stream.height
output_video_stream.pix_fmt = input_video_stream.pix_fmt

# Output Audio Stream
output_audio_stream = output_container.add_stream(input_audio_stream.codec.name, rate=input_audio_stream.rate)

# Seek to start time
seek_time = int(trim_start_time / input_video_stream.time_base)
input_container.seek(seek_time, stream=input_video_stream)

# Main processing loop
done = False
smoothed_crop_x = None
last_known_crop_x = None  # Track last known good crop position
consecutive_misses = 0  # Track consecutive frames without detection

for packet in input_container.demux(input_video_stream, input_audio_stream):
    if done:
        break
    
    if packet.stream.type == 'video':
        for frame in packet.decode():
            new_frame, smoothed_crop_x, is_done, last_known_crop_x, consecutive_misses = process_video_frame(
                frame, smoothed_crop_x, crop_width, trim_start_time, trim_end_time, duration,
                last_known_crop_x, consecutive_misses
            )
            
            if is_done:
                done = True
                break
            
            if new_frame is not None:
                for encoded_packet in output_video_stream.encode(new_frame):
                    output_container.mux(encoded_packet)
    
    elif packet.stream.type == 'audio':
        if not done:
            process_audio_packet(packet, trim_start_time, trim_end_time, output_audio_stream, output_container)

# Flush Video
for encoded_packet in output_video_stream.encode():
    output_container.mux(encoded_packet)

# Flush Audio
for encoded_packet in output_audio_stream.encode():
    output_container.mux(encoded_packet)