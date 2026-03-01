#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import codecs
# Python 2 Unicode fix - safe printing
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # Wrap stdout/stderr for safe printing
    class SafePrint:
        def __init__(self, stream):
            self.stream = stream
        def write(self, data):
            try:
                if isinstance(data, unicode):
                    data = data.encode('utf-8', 'replace')
                elif isinstance(data, str):
                    try:
                        # Try to decode and re-encode safely
                        data = data.decode('utf-8').encode('utf-8', 'replace')
                    except:
                        data = data.encode('ascii', 'replace')
                self.stream.write(data)
            except Exception as e:
                try:
                    self.stream.write(str(data).encode('ascii', 'replace'))
                except:
                    pass
        def flush(self):
            try:
                self.stream.flush()
            except:
                pass
        def __getattr__(self, name):
            return getattr(self.stream, name)
    sys.stdout = SafePrint(sys.stdout)
    sys.stderr = SafePrint(sys.stderr)
import sys
import cv2
import numpy as np
import tempfile
import traceback
import base64
from os.path import splitext, basename, isfile, isdir, join
from os import makedirs
try:
    from flask import Flask, render_template, request, jsonify, send_from_directory, Response, stream_with_context
    from werkzeug.utils import secure_filename
except ImportError:
    print("Flask bulunamadı. Yüklemek için: pip install flask")
    sys.exit(1)

import threading
import time
import json

# Import project modules (not needed directly, but kept for compatibility)

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size (for videos)
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()

# Global state for real-time frame updates
frame_updates = {}
frame_updates_lock = threading.Lock()

# No need to load models here - scripts will load them


def process_image(input_image):
    """Main processing function using project scripts"""
    try:
        # Create temporary directories
        temp_input_dir = tempfile.mkdtemp()
        temp_output_dir = tempfile.mkdtemp()
        
        # Save input image with a standard name
        input_path = os.path.join(temp_input_dir, 'input.jpg')
        cv2.imwrite(input_path, input_image)
        
        # Step 1: Run vehicle-detection.py
        # Python 2 kullan (normal işlemler için)
        import subprocess
        # python komutu artık Python 2'ye işaret ediyor
        vehicle_cmd = ['python', 'vehicle-detection.py', temp_input_dir, temp_output_dir]
        process = subprocess.Popen(vehicle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
        stdout_veh, stderr_veh = process.communicate()
        if process.returncode != 0:
            error_msg = stderr_veh if stderr_veh else "Bilinmeyen hata"
            # Python 2/3 compatibility
            if isinstance(error_msg, bytes):
                error_msg = error_msg.decode('utf-8', errors='ignore')
            print("Vehicle detection error (return code {}): {}".format(process.returncode, error_msg[:500]))
            return input_image, "Araç tespiti hatası: {}".format(error_msg[:200]), [], 0, 0
        
        # Check if any cars were found
        car_files = [f for f in os.listdir(temp_output_dir) if f.endswith('_cars.txt')]
        if not car_files:
            # No vehicles found
            return input_image, "Araç bulunamadı", [], 0, 0
        
        # Step 2: Run license-plate-detection.py
        lp_model_path = 'data/lp-detector/wpod-net_update1.h5'
        lp_cmd = ['python', 'license-plate-detection.py', temp_output_dir, lp_model_path]
        process = subprocess.Popen(lp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
        stdout_lp, stderr_lp = process.communicate()
        if process.returncode != 0:
            error_msg = stderr_lp if stderr_lp else "Bilinmeyen hata"
            if isinstance(error_msg, bytes):
                error_msg = error_msg.decode('utf-8', errors='ignore')
            print("License plate detection error: {}".format(error_msg[:500]))
        
        # Step 3: Run license-plate-ocr.py
        ocr_cmd = ['python', 'license-plate-ocr.py', temp_output_dir]
        process = subprocess.Popen(ocr_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
        stdout_ocr, stderr_ocr = process.communicate()
        if process.returncode != 0:
            error_msg = stderr_ocr if stderr_ocr else "Bilinmeyen hata"
            if isinstance(error_msg, bytes):
                error_msg = error_msg.decode('utf-8', errors='ignore')
            print("OCR error: {}".format(error_msg[:500]))
        
        # Step 4: Run gen-outputs.py to create final output
        gen_cmd = ['python', 'gen-outputs.py', temp_input_dir, temp_output_dir]
        process = subprocess.Popen(gen_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            error_msg = stderr if stderr else "Bilinmeyen hata"
            if isinstance(error_msg, bytes):
                error_msg = error_msg.decode('utf-8', errors='ignore')
            print("Gen outputs error: {}".format(error_msg[:500]))
            return input_image, "Sonuç oluşturma hatası: {}".format(error_msg[:200]), [], 0, 0
        
        # Read the output image
        output_image_path = os.path.join(temp_output_dir, 'input_output.png')
        if not os.path.exists(output_image_path):
            # Try alternative naming - find any _output.png file
            for f in os.listdir(temp_output_dir):
                if f.endswith('_output.png'):
                    output_image_path = os.path.join(temp_output_dir, f)
                    break
        
        if not os.path.exists(output_image_path):
            return input_image, "Çıktı görüntüsü bulunamadı", [], 0, 0
        
        output_image = cv2.imread(output_image_path)
        
        # Parse results from gen-outputs.py output
        results = []
        # Python 2/3 compatibility
        stdout_str = stdout
        if isinstance(stdout, bytes):
            stdout_str = stdout.decode('utf-8', errors='ignore')
        result_lines = stdout_str.strip().split('\n')
        for line in result_lines:
            if line and ',' in line:
                parts = line.split(',')
                if len(parts) > 1:
                    for plate in parts[1:]:
                        if plate.strip():
                            results.append(plate.strip())
        
        # Format results
        if results:
            result_text = "\n".join(["Araç {}: {}".format(i+1, plate) for i, plate in enumerate(results)])
        else:
            result_text = "Araç bulundu ancak plaka tespit edilemedi"
        
        # Count vehicles and plates
        vehicle_count = len([f for f in os.listdir(temp_output_dir) if f.endswith('_cars.txt')])
        plate_count = len(results)
        
        # Clean up temp directories
        import shutil
        shutil.rmtree(temp_input_dir)
        shutil.rmtree(temp_output_dir)
        
        return output_image, result_text, results, vehicle_count, plate_count
        
    except Exception as e:
        error_msg = "Hata oluştu: {}\n{}".format(str(e), traceback.format_exc())
        print(error_msg)
        return input_image, error_msg, [], 0, 0


def process_video(video_path, frame_skip=None, max_frames_to_process=60, session_id=None):
    """
    Process video frame by frame for license plate detection
    frame_skip: Process every Nth frame to speed up processing (auto-calculated if None)
    max_frames_to_process: Maximum number of frames to process (to limit processing time)
    session_id: Session ID for real-time updates
    Returns: output_video_path, all_detected_plates, total_frames_processed, total_vehicles, total_plates
    """
    try:
        import shutil
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return None, "Video açılamadı", [], 0, 0, 0
        
        # Get video properties (Python 2/3 compatible using numeric IDs)
        # Property IDs: FPS=5, WIDTH=3, HEIGHT=4, FRAME_COUNT=7
        fps = int(cap.get(5)) or 30  # CV_CAP_PROP_FPS
        width = int(cap.get(3))  # CV_CAP_PROP_FRAME_WIDTH
        height = int(cap.get(4))  # CV_CAP_PROP_FRAME_HEIGHT
        total_frames = int(cap.get(7))  # CV_CAP_PROP_FRAME_COUNT
        
        if fps == 0:
            fps = 30  # Default FPS
        
        # Auto-calculate frame_skip based on video length (optimized for speed - FASTER)
        if frame_skip is None:
            # For long videos (>1000 frames), use larger skip for faster processing
            if total_frames > 1000:
                # Calculate skip to process approximately max_frames_to_process frames
                frame_skip = max(1, total_frames // max_frames_to_process)
            elif total_frames > 500:
                frame_skip = 15  # Faster for medium videos (was 10)
            elif total_frames > 200:
                frame_skip = 8  # Faster for shorter videos
            else:
                frame_skip = 5  # Default for very short videos
        
        print("Video işleme ayarları: {} frame, {} fps, frame_skip={}, yaklaşık {} frame işlenecek".format(
            total_frames, fps, frame_skip, min(max_frames_to_process, total_frames // frame_skip)))
        
        # Get fourcc (Python 2/3 compatible)
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        except:
            try:
                fourcc = cv2.cv.CV_FOURCC(*'mp4v')
            except:
                fourcc = -1  # Use default codec
        
        # Create output video path
        output_video_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output_video.mp4')
        
        # Video writer
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
        
        if not out.isOpened():
            cap.release()
            return None, "Video writer açılamadı", [], 0, 0, 0
        
        # Temporary directories for frame processing (not used but kept for cleanup)
        temp_frames_dir = tempfile.mkdtemp()
        temp_output_dir = tempfile.mkdtemp()
        
        all_plates = []
        frame_count = 0
        processed_frames = 0
        total_vehicles = 0
        total_plates = 0
        frames_processed_count = 0  # Track how many frames we've actually processed
        
                # Initialize session for real-time updates
        if session_id:
            with frame_updates_lock:
                if session_id in frame_updates:
                    frame_updates[session_id]['total_frames'] = total_frames
                else:
                    frame_updates[session_id] = {
                        'frames': [],
                        'total_frames': total_frames,
                        'processed': 0,
                        'status': 'processing'
                    }
        
        print("Video işleniyor: {} frame, {} fps, frame_skip={}".format(total_frames, fps, frame_skip))
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Stop if we've processed enough frames (early exit for speed)
            if frames_processed_count >= max_frames_to_process:
                # Just copy remaining frames without processing (much faster)
                out.write(frame)
                frame_count += 1
                # Update progress less frequently for remaining frames
                if frame_count % 50 == 0:
                    if session_id:
                        with frame_updates_lock:
                            if session_id in frame_updates:
                                frame_updates[session_id]['processed'] = frames_processed_count
                continue
            
            # Process every Nth frame (faster processing for real-time)
            if frame_count % frame_skip == 0:
                # Process this frame directly without saving to disk first
                temp_input_dir = tempfile.mkdtemp()
                temp_frame_output_dir = tempfile.mkdtemp()
                
                try:
                    # Save frame directly to input dir
                    frame_input_path = os.path.join(temp_input_dir, 'input.jpg')
                    cv2.imwrite(frame_input_path, frame)
                    
                    # Run vehicle detection
                    import subprocess
                    vehicle_cmd = ['python', 'vehicle-detection.py', temp_input_dir, temp_frame_output_dir]
                    process = subprocess.Popen(vehicle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                    stdout_veh, stderr_veh = process.communicate()
                    
                    if process.returncode == 0:
                        # Check if cars were found
                        car_files = [f for f in os.listdir(temp_frame_output_dir) if f.endswith('_cars.txt')]
                        
                        if car_files:
                            # Run license plate detection
                            lp_model_path = 'data/lp-detector/wpod-net_update1.h5'
                            lp_cmd = ['python', 'license-plate-detection.py', temp_frame_output_dir, lp_model_path]
                            subprocess.Popen(lp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR).communicate()
                            
                            # Run OCR
                            ocr_cmd = ['python', 'license-plate-ocr.py', temp_frame_output_dir]
                            subprocess.Popen(ocr_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR).communicate()
                            
                            # Generate output
                            gen_cmd = ['python', 'gen-outputs.py', temp_input_dir, temp_frame_output_dir]
                            process = subprocess.Popen(gen_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                            stdout, stderr = process.communicate()
                            
                            if process.returncode == 0:
                                # Read processed frame
                                output_frame_path = os.path.join(temp_frame_output_dir, 'input_output.png')
                                if os.path.exists(output_frame_path):
                                    processed_frame = cv2.imread(output_frame_path)
                                    if processed_frame is not None:
                                        # Resize to original dimensions if needed
                                        if processed_frame.shape[:2] != (height, width):
                                            processed_frame = cv2.resize(processed_frame, (width, height))
                                        frame = processed_frame
                                        
                                        # Parse plates from output
                                        frame_plates = []
                                        stdout_str = stdout
                                        if isinstance(stdout, bytes):
                                            stdout_str = stdout.decode('utf-8', errors='ignore')
                                        result_lines = stdout_str.strip().split('\n')
                                        for line in result_lines:
                                            if line and ',' in line:
                                                parts = line.split(',')
                                                if len(parts) > 1:
                                                    for plate in parts[1:]:
                                                        plate_str = plate.strip()
                                                        if plate_str:
                                                            frame_plates.append(plate_str)
                                                            if plate_str not in all_plates:
                                                                all_plates.append(plate_str)
                                                                total_plates += 1
                                        
                                        total_vehicles += len(car_files)
                                        processed_frames += 1
                                        frames_processed_count += 1
                                        
                                        # Send real-time update if session_id exists (send even if no plates for debugging)
                                        if session_id:
                                            # Convert frame to base64 for transmission
                                            _, buffer = cv2.imencode('.jpg', processed_frame)
                                            frame_base64 = base64.b64encode(buffer).decode('utf-8')
                                            
                                            with frame_updates_lock:
                                                if session_id in frame_updates:
                                                    frame_updates[session_id]['frames'].append({
                                                        'frame_number': frame_count,
                                                        'image': 'data:image/jpeg;base64,' + frame_base64,
                                                        'plates': frame_plates if frame_plates else [],
                                                        'vehicle_count': len(car_files),
                                                        'timestamp': time.time()
                                                    })
                                                    frame_updates[session_id]['processed'] = frames_processed_count
                                                    
                                                    # Also update all_plates in session for final summary
                                                    if 'all_plates' not in frame_updates[session_id]:
                                                        frame_updates[session_id]['all_plates'] = []
                                                    for plate in frame_plates:
                                                        if plate not in frame_updates[session_id]['all_plates']:
                                                            frame_updates[session_id]['all_plates'].append(plate)
                
                except Exception as e:
                    print("Frame {} işleme hatası: {}".format(frame_count, str(e)))
                finally:
                    # Clean up temp directories for this frame
                    try:
                        shutil.rmtree(temp_input_dir)
                        shutil.rmtree(temp_frame_output_dir)
                    except:
                        pass
            
            # Write frame to output video
            out.write(frame)
            frame_count += 1
            
            # Progress update less frequently for speed (every 200 frames or every 3 seconds)
            if frame_count % 200 == 0 or (frame_count % (fps * 3) == 0):
                progress_pct = (frame_count * 100.0 / total_frames) if total_frames > 0 else 0
                print("İlerleme: {}/{} frame ({:.1f}%), İşlenen: {} frame".format(
                    frame_count, total_frames, progress_pct, frames_processed_count))
                # Update session less frequently for better performance
                if session_id and frame_count % 200 == 0:
                    with frame_updates_lock:
                        if session_id in frame_updates:
                            frame_updates[session_id]['processed'] = frames_processed_count
        
        cap.release()
        out.release()
        
        # Mark session as completed and ensure all_plates is saved
        if session_id:
            with frame_updates_lock:
                if session_id in frame_updates:
                    # Ensure all_plates is saved from the collected plates
                    if 'all_plates' not in frame_updates[session_id] or not frame_updates[session_id]['all_plates']:
                        frame_updates[session_id]['all_plates'] = all_plates
                        print("All_plates saved to session at completion: {}".format(all_plates))
                    frame_updates[session_id]['status'] = 'completed'
                    frame_updates[session_id]['plates'] = all_plates  # Also save to plates for compatibility
                    frame_updates[session_id]['plate_count'] = len(all_plates)
        
        # Verify output video was created
        if not os.path.exists(output_video_path) or os.path.getsize(output_video_path) == 0:
            # Clean up
            try:
                shutil.rmtree(temp_frames_dir)
                shutil.rmtree(temp_output_dir)
            except:
                pass
            if session_id:
                with frame_updates_lock:
                    if session_id in frame_updates:
                        frame_updates[session_id]['status'] = 'error'
            return None, "Video oluşturulamadı", [], 0, 0, 0
        
        # Clean up
        try:
            shutil.rmtree(temp_frames_dir)
            shutil.rmtree(temp_output_dir)
        except:
            pass
        
        print("Video işleme tamamlandı: {} frame işlendi, {} plaka bulundu".format(processed_frames, len(all_plates)))
        return output_video_path, "Video işlendi: {} frame işlendi, {} plaka bulundu".format(processed_frames, len(all_plates)), all_plates, processed_frames, total_vehicles, total_plates
        
    except Exception as e:
        error_msg = "Video işleme hatası: {}\n{}".format(str(e), traceback.format_exc())
        print(error_msg)
        return None, error_msg, [], 0, 0, 0


@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        error_msg = "Template hatası: {}. Lütfen templates/index.html dosyasının mevcut olduğundan emin olun.".format(str(e))
        print(error_msg)
        traceback.print_exc()
        return error_msg, 500


@app.route('/test')
def test():
    """Test endpoint to check if server is running"""
    return jsonify({'status': 'OK', 'message': 'Server is running!'})


@app.route('/favicon.ico')
def favicon():
    """Handle favicon requests"""
    return '', 204  # No content


@app.route('/.well-known/<path:path>')
def well_known(path):
    """Handle .well-known requests (Chrome DevTools, etc.)"""
    return '', 204  # No content


def process_live_stream(stream_url, session_id=None, frame_skip=30):
    """
    Process live M3U8/HLS stream for license plate detection
    Uses faster processing (every Nth frame) for real-time performance
    Uses optimized mobese-fast scripts for much faster detection
    frame_skip=30 means process every 30th frame (very fast for real-time)
    """
    try:
        import shutil
        
        # Open stream
        cap = cv2.VideoCapture(stream_url)
        if not cap.isOpened():
            return None, "Canlı akış açılamadı", [], 0, 0, 0
        
        # Get stream properties
        fps = int(cap.get(5)) or 25
        width = int(cap.get(3))
        height = int(cap.get(4))
        
        if fps == 0:
            fps = 25
        
        # Initialize session
        if session_id:
            with frame_updates_lock:
                if session_id not in frame_updates:
                    frame_updates[session_id] = {
                        'frames': [],
                        'original_frames': [],  # For original stream display
                        'all_plates': [],
                        'status': 'streaming',
                        'vehicle_count': 0,
                        'plate_count': 0,
                        'processed_frames': 0
                    }
        
        all_plates = []
        frame_count = 0
        processed_frames = 0
        total_vehicles = 0
        total_plates = 0
        
        print("MOBESE canlı akış işleniyor: {} fps, frame_skip={} (ÇOK HIZLI MOD)".format(fps, frame_skip))
        
        # Process stream frames
        while True:
            # Check if stream should be stopped
            with frame_updates_lock:
                if session_id and session_id in frame_updates:
                    if frame_updates[session_id].get('status') == 'stopped':
                        print("Mobese akış durduruldu")
                        break
            
            ret, frame = cap.read()
            if not ret:
                print("Frame okunamadı, yeniden bağlanılıyor...")
                # Try to reconnect
                time.sleep(1)
                cap.release()
                cap = cv2.VideoCapture(stream_url)
                continue
            
            # Send original frame to frontend (for original stream display) - every 3 frames for smooth playback
            if session_id and frame_count % 3 == 0:
                try:
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    
                    with frame_updates_lock:
                        if session_id in frame_updates:
                            frame_updates[session_id]['original_frames'] = frame_updates[session_id].get('original_frames', [])
                            frame_updates[session_id]['original_frames'].append({
                                'frame_number': frame_count,
                                'image': 'data:image/jpeg;base64,' + frame_base64,
                                'timestamp': time.time()
                            })
                            # Keep only last 3 original frames (for smooth playback)
                            if len(frame_updates[session_id]['original_frames']) > 3:
                                frame_updates[session_id]['original_frames'].pop(0)
                except Exception as e:
                    print("Original frame gönderme hatası: {}".format(str(e)))
            
            # Process every Nth frame for speed
            if frame_count % frame_skip == 0:
                print("Frame {} işleniyor...".format(frame_count))
                temp_input_dir = tempfile.mkdtemp()
                temp_frame_output_dir = tempfile.mkdtemp()
                
                try:
                    # Save frame
                    frame_input_path = os.path.join(temp_input_dir, 'input.jpg')
                    cv2.imwrite(frame_input_path, frame)
                    
                    # Run MOBESE YOLOv8 ile araç tespiti (Python 3 + Ultralytics)
                    # Önce YOLOv8'i dene, yoksa Darknet'e fallback
                    import subprocess
                    
                    # Python 3 ile YOLOv8 araç tespitini dene
                    python3_available = False
                    python3_cmd = None
                    
                    # Conda ortamındaki Python 3'ü kontrol et (Python 2 uyumlu)
                    conda_prefix = os.environ.get('CONDA_PREFIX', '')
                    if conda_prefix:
                        conda_python3 = os.path.join(conda_prefix, 'bin', 'python3')
                        if os.path.exists(conda_python3):
                            try:
                                # Python 2 uyumlu: subprocess.Popen kullan
                                proc = subprocess.Popen([conda_python3, '--version'], 
                                                      stdout=subprocess.PIPE, 
                                                      stderr=subprocess.PIPE)
                                stdout, stderr = proc.communicate()
                                if proc.returncode == 0:
                                    # Ultralytics kontrolü - YOLOv8 için gerekli
                                    test_proc = subprocess.Popen([conda_python3, '-c', 'from ultralytics import YOLO; import cv2'], 
                                                               stdout=subprocess.PIPE, 
                                                               stderr=subprocess.PIPE)
                                    test_stdout, test_stderr = test_proc.communicate()
                                    if test_proc.returncode == 0:
                                        python3_available = True
                                        python3_cmd = conda_python3
                                        print("Frame {} - Conda Python 3 + Ultralytics + OpenCV hazir!".format(frame_count))
                                    else:
                                        print("Frame {} - Conda Python 3 var ama Ultralytics yuklu degil".format(frame_count))
                            except Exception as e:
                                print("Frame {} - Conda Python 3 kontrolu hatasi: {}".format(frame_count, str(e)))
                    
                    # Conda Python 3 yoksa sistem Python 3'ü dene
                    if not python3_available:
                        try:
                            # Python 2 uyumlu: subprocess.Popen kullan
                            proc = subprocess.Popen(['python3', '--version'], 
                                                  stdout=subprocess.PIPE, 
                                                  stderr=subprocess.PIPE)
                            stdout, stderr = proc.communicate()
                            if proc.returncode == 0:
                                # Ultralytics kontrolü - YOLOv8 için gerekli
                                test_proc = subprocess.Popen(['python3', '-c', 'from ultralytics import YOLO; import cv2'], 
                                                           stdout=subprocess.PIPE, 
                                                           stderr=subprocess.PIPE)
                                test_stdout, test_stderr = test_proc.communicate()
                                if test_proc.returncode == 0:
                                    python3_available = True
                                    python3_cmd = 'python3'
                                    # Python 2/3 uyumlu decode
                                    if isinstance(stdout, bytes):
                                        version_str = stdout.decode('utf-8', errors='ignore').strip()
                                    else:
                                        version_str = str(stdout).strip()
                                    print("Frame {} - Sistem Python 3 + Ultralytics + OpenCV hazir!".format(frame_count))
                                else:
                                    print("Frame {} - Sistem Python 3 var ama Ultralytics yuklu degil".format(frame_count))
                        except Exception as e:
                            print("Frame {} - Python 3 kontrolu hatasi: {}".format(frame_count, str(e)))
                    
                    if python3_available and python3_cmd:
                        # YOLOv8 ile araç tespiti (Python 3) - ÖNCELİKLE YOLOv8 KULLAN
                        print("Frame {} - YOLOv8 ile arac tespiti deneniyor...".format(frame_count))
                        vehicle_cmd = [python3_cmd, 'mobese-vehicle-yolov8-detection.py', temp_input_dir, temp_frame_output_dir]
                        process = subprocess.Popen(vehicle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                        stdout_veh, stderr_veh = process.communicate()
                        
                        # Debug: Print YOLOv8 output (TAM ÇIKTI)
                        if stdout_veh:
                            stdout_str = stdout_veh
                            if isinstance(stdout_veh, bytes):
                                stdout_str = stdout_veh.decode('utf-8', errors='ignore')
                            # Tüm çıktıyı göster
                            print("Frame {} - YOLOv8 stdout: {}".format(frame_count, stdout_str[:500]))
                        
                        if stderr_veh:
                            stderr_str = stderr_veh
                            if isinstance(stderr_veh, bytes):
                                stderr_str = stderr_veh.decode('utf-8', errors='ignore')
                            print("Frame {} - YOLOv8 stderr: {}".format(frame_count, stderr_str[:500]))
                        
                        # Eğer YOLOv8 başarısız olursa tekrar dene veya Darknet'e fallback
                        if process.returncode != 0:
                            if stderr_veh:
                                stderr_str = stderr_veh
                                if isinstance(stderr_veh, bytes):
                                    stderr_str = stderr_veh.decode('utf-8', errors='ignore')
                                try:
                                    safe_str = stderr_str[:500].encode('ascii', 'replace').decode('ascii')
                                    print("Frame {} - YOLOv8 HATASI (tam): {}".format(frame_count, safe_str))
                                except:
                                    print("Frame {} - YOLOv8 hatasi (encoding error)".format(frame_count))
                            
                            # YOLOv8 başarısız - Darknet'e fallback (ama önce hatayı göster)
                            print("Frame {} - YOLOv8 arac tespiti basarisiz (returncode={})".format(frame_count, process.returncode))
                            
                            # Ultralytics veya cv2 eksik olabilir - kullanıcıya bilgi ver
                            if stderr_veh:
                                stderr_str = stderr_veh
                                if isinstance(stderr_veh, bytes):
                                    stderr_str = stderr_veh.decode('utf-8', errors='ignore')
                                if 'ultralytics' in stderr_str.lower() or 'ModuleNotFoundError' in stderr_str:
                                    print("Frame {} - UYARI: Ultralytics yuklu degil! YOLOv8 calismiyor.".format(frame_count))
                                    print("Frame {} - Cozum: python3 -m pip install --user ultralytics opencv-python".format(frame_count))
                            
                            print("Frame {} - Darknet kullaniliyor (fallback)...".format(frame_count))
                            vehicle_cmd = ['python', 'mobese-detection.py', temp_input_dir, temp_frame_output_dir]
                            process = subprocess.Popen(vehicle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                            stdout_veh, stderr_veh = process.communicate()
                    else:
                        # Python 3 yoksa direkt Darknet kullan
                        print("Frame {} - Python 3 bulunamadı, Darknet kullanılıyor...".format(frame_count))
                        vehicle_cmd = ['python', 'mobese-detection.py', temp_input_dir, temp_frame_output_dir]
                        process = subprocess.Popen(vehicle_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                        stdout_veh, stderr_veh = process.communicate()
                    
                    # Debug: Print vehicle detection output (Python 2/3 uyumlu)
                    if stdout_veh:
                        # Python 2/3 uyumlu decode
                        if isinstance(stdout_veh, bytes):
                            stdout_str = stdout_veh.decode('utf-8', errors='ignore')
                        else:
                            stdout_str = str(stdout_veh)
                        
                        # Print ALL Darknet output for debugging
                        print("Frame {} - Darknet çıktısı: {}".format(frame_count, stdout_str.strip()[:500]))
                    
                    if stderr_veh:
                        # Python 2/3 uyumlu decode
                        if isinstance(stderr_veh, bytes):
                            stderr_str = stderr_veh.decode('utf-8', errors='ignore')
                        else:
                            stderr_str = str(stderr_veh)
                        # Only print if it's an actual error, not layer info
                        if stderr_str.strip() and 'error' in stderr_str.lower():
                            print("Frame {} - Vehicle detection error: {}".format(frame_count, stderr_str[:200]))
                    
                    if process.returncode == 0:
                        car_files = [f for f in os.listdir(temp_frame_output_dir) if f.endswith('_cars.txt')]
                        print("Frame {} - Araç dosyaları: {}".format(frame_count, len(car_files)))
                        
                        if car_files:
                            # Run MOBESE özel model ile plaka tespiti
                            # YOLOv8 best.pt Python 3 gerektirir, bu yüzden önce Python 3 ile dene
                            # Eğer Python 3 yoksa veya ultralytics yoksa, WPOD-NET kullanılacak
                            
                            # Python 3 ile YOLOv8'i dene
                            # Önce conda ortamındaki Python 3'ü dene, sonra sistem Python 3'ü
                            python3_available = False
                            python3_cmd = None
                            
                            # Conda ortamındaki Python 3'ü kontrol et (Python 2 uyumlu)
                            conda_prefix = os.environ.get('CONDA_PREFIX', '')
                            if conda_prefix:
                                conda_python3 = os.path.join(conda_prefix, 'bin', 'python3')
                                if os.path.exists(conda_python3):
                                    try:
                                        # Python 2 uyumlu: subprocess.Popen kullan
                                        proc = subprocess.Popen([conda_python3, '--version'], 
                                                              stdout=subprocess.PIPE, 
                                                              stderr=subprocess.PIPE)
                                        stdout, stderr = proc.communicate()
                                        if proc.returncode == 0:
                                            python3_available = True
                                            python3_cmd = conda_python3
                                    except:
                                        pass
                            
                            # Conda Python 3 yoksa sistem Python 3'ü dene
                            if not python3_available:
                                try:
                                    # Python 2 uyumlu: subprocess.Popen kullan
                                    proc = subprocess.Popen(['python3', '--version'], 
                                                          stdout=subprocess.PIPE, 
                                                          stderr=subprocess.PIPE)
                                    stdout, stderr = proc.communicate()
                                    if proc.returncode == 0:
                                        python3_available = True
                                        python3_cmd = 'python3'
                                except:
                                    pass
                            
                            if python3_available and python3_cmd:
                                # Python 3 ile YOLOv8 script'ini çalıştır (best.pt modeli)
                                print("Frame {} - best.pt (YOLOv8) ile plaka tespiti deneniyor...".format(frame_count))
                                lp_cmd = [python3_cmd, 'mobese-lp-yolov8-detection.py', temp_frame_output_dir]
                                process_lp = subprocess.Popen(lp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                                stdout_lp, stderr_lp = process_lp.communicate()
                                
                                # Debug: Print YOLOv8 output (Python 2/3 uyumlu)
                                if stdout_lp:
                                    # Python 2/3 uyumlu decode
                                    if isinstance(stdout_lp, bytes):
                                        stdout_str = stdout_lp.decode('utf-8', errors='ignore')
                                    else:
                                        stdout_str = str(stdout_lp)
                                    try:
                                        if 'best.pt' in stdout_str or 'YOLOv8' in stdout_str:
                                            print("Frame {} - best.pt kullanildi!".format(frame_count))
                                    except:
                                        pass  # Skip if encoding issues
                                
                                # Eğer YOLOv8 başarısız olursa WPOD-NET'e fallback
                                if process_lp.returncode != 0:
                                    print("Frame {} - YOLOv8 plaka tespiti basarisiz (ultralytics yuklu degil olabilir), WPOD-NET kullaniliyor...".format(frame_count))
                                    lp_cmd = ['python', 'mobese-lp-detection.py', temp_frame_output_dir]
                                    subprocess.Popen(lp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR).communicate()
                            else:
                                # Python 3 yoksa direkt WPOD-NET kullan
                                print("Python 3 bulunamadı, WPOD-NET kullanılıyor...")
                                lp_cmd = ['python', 'mobese-lp-detection.py', temp_frame_output_dir]
                                subprocess.Popen(lp_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR).communicate()
                            
                            # Run OCR (same, but can be optimized too)
                            ocr_cmd = ['python', 'license-plate-ocr.py', temp_frame_output_dir]
                            subprocess.Popen(ocr_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR).communicate()
                            
                            # Generate output
                            gen_cmd = ['python', 'gen-outputs.py', temp_input_dir, temp_frame_output_dir]
                            process = subprocess.Popen(gen_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=BASE_DIR)
                            stdout, stderr = process.communicate()
                            
                            if process.returncode == 0:
                                output_frame_path = os.path.join(temp_frame_output_dir, 'input_output.png')
                                if os.path.exists(output_frame_path):
                                    processed_frame = cv2.imread(output_frame_path)
                                    if processed_frame is not None:
                                        if processed_frame.shape[:2] != (height, width):
                                            processed_frame = cv2.resize(processed_frame, (width, height))
                                        
                                        # Parse plates
                                        frame_plates = []
                                        stdout_str = stdout
                                        if isinstance(stdout, bytes):
                                            stdout_str = stdout.decode('utf-8', errors='ignore')
                                        result_lines = stdout_str.strip().split('\n')
                                        for line in result_lines:
                                            if line and ',' in line:
                                                parts = line.split(',')
                                                if len(parts) > 1:
                                                    for plate in parts[1:]:
                                                        plate_str = plate.strip()
                                                        if plate_str:
                                                            frame_plates.append(plate_str)
                                                            if plate_str not in all_plates:
                                                                all_plates.append(plate_str)
                                                                total_plates += 1
                                        
                                        total_vehicles += len(car_files)
                                        processed_frames += 1
                                        
                                        # Send real-time update
                                        if session_id:
                                            _, buffer = cv2.imencode('.jpg', processed_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                                            frame_base64 = base64.b64encode(buffer).decode('utf-8')
                                            
                                            with frame_updates_lock:
                                                if session_id in frame_updates:
                                                    frame_updates[session_id]['frames'].append({
                                                        'frame_number': frame_count,
                                                        'image': 'data:image/jpeg;base64,' + frame_base64,
                                                        'plates': frame_plates if frame_plates else [],
                                                        'vehicle_count': len(car_files),
                                                        'timestamp': time.time()
                                                    })
                                                    frame_updates[session_id]['processed'] = processed_frames
                                                    frame_updates[session_id]['vehicle_count'] = total_vehicles
                                                    
                                                    # Update all_plates
                                                    if 'all_plates' not in frame_updates[session_id]:
                                                        frame_updates[session_id]['all_plates'] = []
                                                    for plate in frame_plates:
                                                        if plate not in frame_updates[session_id]['all_plates']:
                                                            frame_updates[session_id]['all_plates'].append(plate)
                                                    frame_updates[session_id]['plate_count'] = len(frame_updates[session_id]['all_plates'])
                                                    
                                                    print("Frame {} işlendi ve gönderildi - Plakalar: {}, Araçlar: {}".format(
                                                        frame_count, len(frame_plates), len(car_files)))
                        else:
                            # Araç bulunamadı ama yine de orijinal frame'i gönder
                            print("Frame {} - Araç bulunamadı, orijinal frame gönderiliyor".format(frame_count))
                            if session_id:
                                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                                
                                with frame_updates_lock:
                                    if session_id in frame_updates:
                                        frame_updates[session_id]['frames'].append({
                                            'frame_number': frame_count,
                                            'image': 'data:image/jpeg;base64,' + frame_base64,
                                            'plates': [],
                                            'vehicle_count': 0,
                                            'timestamp': time.time()
                                        })
                                        print("Frame {} - Orijinal frame gönderildi (araç yok)".format(frame_count))
                    else:
                        print("Frame {} - Araç tespiti hatası (returncode: {})".format(frame_count, process.returncode))
                        # Hata olsa bile orijinal frame'i gönder
                        if session_id:
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            frame_base64 = base64.b64encode(buffer).decode('utf-8')
                            
                            with frame_updates_lock:
                                if session_id in frame_updates:
                                    frame_updates[session_id]['frames'].append({
                                        'frame_number': frame_count,
                                        'image': 'data:image/jpeg;base64,' + frame_base64,
                                        'plates': [],
                                        'vehicle_count': 0,
                                        'timestamp': time.time()
                                    })
                                    print("Frame {} - Hata durumunda orijinal frame gönderildi".format(frame_count))
                
                except Exception as e:
                    print("Frame {} işleme hatası: {}".format(frame_count, str(e)))
                    import traceback
                    traceback.print_exc()
                    # Hata olsa bile orijinal frame'i gönder
                    if session_id:
                        try:
                            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                            frame_base64 = base64.b64encode(buffer).decode('utf-8')
                            
                            with frame_updates_lock:
                                if session_id in frame_updates:
                                    frame_updates[session_id]['frames'].append({
                                        'frame_number': frame_count,
                                        'image': 'data:image/jpeg;base64,' + frame_base64,
                                        'plates': [],
                                        'vehicle_count': 0,
                                        'timestamp': time.time()
                                    })
                        except:
                            pass
                finally:
                    try:
                        shutil.rmtree(temp_input_dir)
                        shutil.rmtree(temp_frame_output_dir)
                    except:
                        pass
            
            frame_count += 1
            
            # No delay for mobese - process as fast as possible
            # time.sleep(0.01)  # Removed for maximum speed
        
        cap.release()
        return None, "Akış sonlandı", all_plates, processed_frames, total_vehicles, total_plates
        
    except Exception as e:
        error_msg = "Canlı akış hatası: {}\n{}".format(str(e), traceback.format_exc())
        print(error_msg)
        return None, error_msg, [], 0, 0, 0


@app.route('/start_stream', methods=['POST'])
def start_stream():
    """Start processing live M3U8 stream"""
    try:
        data = request.get_json()
        stream_url = data.get('url', '')
        
        if not stream_url:
            return jsonify({'error': 'Stream URL gerekli'}), 400
        
        # Generate session ID
        import uuid
        session_id = str(uuid.uuid4())
        
        # Initialize session
        with frame_updates_lock:
            frame_updates[session_id] = {
                'frames': [],
                'all_plates': [],
                'status': 'streaming',
                'stream_url': stream_url,
                'vehicle_count': 0,
                'plate_count': 0,
                'processed_frames': 0
            }
        
        # Start stream processing in background
        def process_stream_background():
            process_live_stream(stream_url, session_id=session_id, frame_skip=30)  # Çok hızlı işleme (her 30. frame)
        
        thread = threading.Thread(target=process_stream_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'status': 'streaming',
            'message': 'Canlı akış işleme başlatıldı'
        })
    
    except Exception as e:
        return jsonify({'error': 'Akış başlatma hatası: {}'.format(str(e))}), 500


@app.route('/stop_stream/<session_id>', methods=['POST'])
def stop_stream(session_id):
    """Stop processing live stream"""
    try:
        with frame_updates_lock:
            if session_id in frame_updates:
                frame_updates[session_id]['status'] = 'stopped'
                return jsonify({'success': True, 'message': 'Akış durduruldu'})
            return jsonify({'error': 'Session bulunamadı'}), 404
    except Exception as e:
        return jsonify({'error': 'Hata: {}'.format(str(e))}), 500


@app.route('/stream/<session_id>')
def stream_updates(session_id):
    """Server-Sent Events endpoint for real-time frame updates"""
    def generate():
        last_count = 0
        last_original_count = 0
        while True:
            with frame_updates_lock:
                if session_id in frame_updates:
                    data = frame_updates[session_id]
                    
                    # Send original frames (for original stream display)
                    if 'original_frames' in data and len(data['original_frames']) > last_original_count:
                        new_original_frames = data['original_frames'][last_original_count:]
                        for orig_frame in new_original_frames:
                            orig_frame['status'] = 'original_frame'
                            yield 'data: ' + json.dumps(orig_frame) + '\n\n'
                        last_original_count = len(data['original_frames'])
                    
                    # Send new processed frames
                    if len(data['frames']) > last_count:
                        new_frames = data['frames'][last_count:]
                        for frame_data in new_frames:
                            frame_data['status'] = 'frame'
                            yield 'data: ' + json.dumps(frame_data) + '\n\n'
                        last_count = len(data['frames'])
                    
                    # Check if completed
                    if data['status'] == 'completed':
                        # Get plates from session - prioritize all_plates, then plates, then empty list
                        session_plates = data.get('all_plates', [])
                        if not session_plates:
                            session_plates = data.get('plates', [])
                        
                        # Send final video if available
                        final_data = {
                            'status': 'completed',
                            'vehicle_count': data.get('vehicle_count', 0),
                            'plate_count': len(session_plates) if session_plates else data.get('plate_count', 0),
                            'processed_frames': data.get('processed_frames', 0),
                            'plates': session_plates,  # Use collected plates
                            'results': data.get('results', '')
                        }
                        
                        # Debug: Print final plates
                        print("SSE Final plates sending: {}".format(session_plates))
                        
                        # Try to read and encode final video
                        output_path = data.get('output_path')
                        if output_path and os.path.exists(output_path):
                            try:
                                output_size = os.path.getsize(output_path)
                                if output_size < 50 * 1024 * 1024:  # Less than 50MB
                                    with open(output_path, 'rb') as f:
                                        video_data = f.read()
                                    video_base64 = base64.b64encode(video_data).decode('utf-8')
                                    final_data['video'] = 'data:video/mp4;base64,' + video_base64
                            except Exception as e:
                                print("Final video encoding error: {}".format(str(e)))
                        
                        yield 'data: ' + json.dumps(final_data) + '\n\n'
                        break
                    elif data['status'] == 'error':
                        yield 'data: ' + json.dumps({'status': 'error', 'message': 'Video işleme hatası'}) + '\n\n'
                        break
                else:
                    # Session not found, wait a bit
                    time.sleep(0.5)
                    continue
            
            time.sleep(0.1)  # Small delay to prevent busy waiting
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Dosya bulunamadı'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi'}), 400
        
        if file:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Check if it's a video file
            file_ext = os.path.splitext(filename)[1].lower()
            video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
            
            if file_ext in video_extensions:
                # Check file size (max 100MB)
                file_size = os.path.getsize(filepath)
                if file_size > 100 * 1024 * 1024:
                    os.remove(filepath)
                    return jsonify({'error': 'Video dosyası çok büyük (Max: 100MB)'}), 400
                
                # Generate session ID for real-time updates
                import uuid
                session_id = str(uuid.uuid4())
                
                # Store filepath in session for later cleanup (if not already exists)
                with frame_updates_lock:
                    if session_id not in frame_updates:
                        frame_updates[session_id] = {
                            'frames': [],
                            'total_frames': 0,
                            'processed': 0,
                            'status': 'processing',
                            'filepath': filepath,
                            'output_path': None,
                            'results': None,
                                'plates': None,
                                'all_plates': [],  # Track all unique plates from frames
                                'vehicle_count': 0,
                                'plate_count': 0,
                                'processed_frames': 0
                        }
                    else:
                        frame_updates[session_id]['filepath'] = filepath
                
                # Start video processing in background thread
                def process_in_background():
                    try:
                        output_video_path, result_text, results, processed_frames, vehicle_count, plate_count = process_video(
                            filepath, frame_skip=None, max_frames_to_process=60, session_id=session_id)  # Faster: 60 frames instead of 100
                        
                        # Use all_plates from session if available, otherwise use results
                        final_plates = results if results else []
                        with frame_updates_lock:
                            if session_id in frame_updates and 'all_plates' in frame_updates[session_id]:
                                final_plates = frame_updates[session_id]['all_plates']
                                if not final_plates and results:
                                    final_plates = results
                        
                        print("Video işleme tamamlandı - Plakalar: {}, Araçlar: {}, İşlenen frame: {}".format(
                            len(final_plates), vehicle_count, processed_frames))
                        
                        with frame_updates_lock:
                            if session_id in frame_updates:
                                frame_updates[session_id]['output_path'] = output_video_path
                                frame_updates[session_id]['results'] = result_text
                                frame_updates[session_id]['plates'] = final_plates
                                frame_updates[session_id]['vehicle_count'] = vehicle_count
                                frame_updates[session_id]['plate_count'] = len(final_plates) if final_plates else plate_count
                                frame_updates[session_id]['processed_frames'] = processed_frames
                                frame_updates[session_id]['status'] = 'completed' if output_video_path else 'error'
                                
                                # Debug: Print session data
                                print("Session data saved - Plates: {}, Count: {}, All_plates: {}, All_plates_count: {}".format(
                                    frame_updates[session_id]['plates'], 
                                    len(frame_updates[session_id]['plates']),
                                    frame_updates[session_id].get('all_plates', []),
                                    len(frame_updates[session_id].get('all_plates', []))))
                                
                                # Ensure all_plates is set if not already
                                if 'all_plates' not in frame_updates[session_id] or not frame_updates[session_id]['all_plates']:
                                    frame_updates[session_id]['all_plates'] = final_plates
                                    print("All_plates set from final_plates: {}".format(final_plates))
                    except Exception as e:
                        print("Video işleme hatası: {}".format(str(e)))
                        import traceback
                        traceback.print_exc()
                        with frame_updates_lock:
                            if session_id in frame_updates:
                                frame_updates[session_id]['status'] = 'error'
                
                thread = threading.Thread(target=process_in_background)
                thread.daemon = True
                thread.start()
                
                # Return immediately with session ID
                return jsonify({
                    'success': True,
                    'type': 'video',
                    'session_id': session_id,
                    'status': 'processing',
                    'message': 'Video işleme başlatıldı'
                })
            else:
                # Process image
                input_image = cv2.imread(filepath)
                if input_image is None:
                    os.remove(filepath)
                    return jsonify({'error': 'Geçersiz görüntü dosyası'}), 400
                
                # Process image
                output_image, result_text, results, vehicle_count, plate_count = process_image(input_image)
                
                # Convert output image to base64
                _, buffer = cv2.imencode('.jpg', output_image)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                # Clean up uploaded file
                os.remove(filepath)
                
                return jsonify({
                    'success': True,
                    'type': 'image',
                    'image': 'data:image/jpeg;base64,' + img_base64,
                    'results': result_text,
                    'plates': results,
                    'vehicle_count': vehicle_count,
                    'plate_count': plate_count
                })
    
    except Exception as e:
        return jsonify({'error': 'İşlem hatası: {}'.format(str(e))}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    if not os.path.exists(TEMPLATES_DIR):
        os.makedirs(TEMPLATES_DIR)
        print("Templates klasörü oluşturuldu: {}".format(TEMPLATES_DIR))
    
    # Check if template exists
    template_path = os.path.join(TEMPLATES_DIR, 'index.html')
    if not os.path.exists(template_path):
        print("HATA: templates/index.html dosyası bulunamadı!")
        print("Lütfen templates/index.html dosyasının mevcut olduğundan emin olun.")
        sys.exit(1)
    
    # Check if required scripts exist
    required_scripts = [
        'vehicle-detection.py',
        'license-plate-detection.py',
        'license-plate-ocr.py',
        'gen-outputs.py'
    ]
    
    missing_scripts = []
    for script in required_scripts:
        if not os.path.exists(script):
            missing_scripts.append(script)
    
    if missing_scripts:
        print("HATA: Gerekli script'ler bulunamadı:")
        for script in missing_scripts:
            print("  - {}".format(script))
        sys.exit(1)
    
    print("\n" + "="*50)
    print("  ALPR - Otomatik Plaka Tanıma Sistemi")
    print("  Web Arayüzü Başlatılıyor...")
    print("="*50 + "\n")
    print("Proje script'leri kullanılıyor:")
    print("  - vehicle-detection.py")
    print("  - license-plate-detection.py")
    print("  - license-plate-ocr.py")
    print("  - gen-outputs.py")
    
    # Try to find an available port
    import socket
    
    def find_free_port(start_port=5000, max_attempts=10):
        for port in range(start_port, start_port + max_attempts):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('0.0.0.0', port))
                sock.close()
                return port
            except socket.error:
                continue
        return None
    
    port = find_free_port(5000)
    if port is None:
        print("HATA: 5000-5009 arası portlar kullanımda!")
        print("Lütfen port 5000'i kullanan process'i kapatın:")
        print("  lsof -ti:5000 | xargs kill -9")
        sys.exit(1)
    
    if port != 5000:
        print("UYARI: Port 5000 kullanımda, port {} kullanılıyor.".format(port))
    
    print("\nWeb sunucusu başlatılıyor...")
    print("Tarayıcınızda http://localhost:{} adresini açın.\n".format(port))
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except Exception as e:
        print("Sunucu başlatılamadı: {}".format(str(e)))
        traceback.print_exc()
        sys.exit(1)

