import sys
import subprocess
import pkg_resources
import argparse
import socket
import cv2
import numpy as np
import time
import os
import threading
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, request

# Verificar dependencias
required = {'flask', 'opencv-python', 'numpy'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing = required - installed

if missing:
    print("Faltan dependencias:")
    for dep in missing:
        print(f"- {dep}")
    print("\nInstalar con:")
    print(f"pip install {' '.join(missing)}")
    sys.exit(1)

app = Flask(__name__)

class CameraManager:
    def __init__(self):
        self.cap = None
        self.current_camera = 0
        self.settings = {
            'brightness': 0,      # -100 a 100
            'contrast': 0,        # -100 a 100
            'saturation': 0,      # -100 a 100
            'sharpness': 0,       # -100 a 100
            'exposure': 0,        # -10 a 10
            'resolution': (1280, 720),
            'filter': 'none',
            'overlay_timestamp': False
        }
        self.recording = False
        self.video_writer = None
        self.timelapse_active = False
        self.save_path = "captures"
        self.filename_prefix = "capture_"
        self.create_directory()
        self.frame_lock = threading.Lock()
        self.active = True
        self.last_frame = None
    
    def create_directory(self):
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
    
    def list_cameras(self):
        index = 0
        cameras = []
        max_attempts = 10
        
        while index < max_attempts:
            try:
                cap = cv2.VideoCapture(index)
                if cap.isOpened():
                    _, frame = cap.read()
                    if frame is not None:
                        cameras.append(index)
                    cap.release()
                else:
                    break
            except:
                pass
            index += 1
        
        return cameras

    def select_camera(self, camera_id):
        if self.cap:
            self.release_camera()
        
        try:
            self.cap = cv2.VideoCapture(camera_id)
            if not self.cap.isOpened():
                raise Exception(f"No se pudo abrir la cámara {camera_id}")
            
            # Ajustar resolución máxima soportada
            max_width = 1920
            max_height = 1080
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, max_width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, max_height)
            
            actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Si la resolución solicitada no está disponible, usar la máxima soportada
            self.settings['resolution'] = (actual_width, actual_height)
            
            self.current_camera = camera_id
            return True
        except Exception as e:
            print(f"Error al seleccionar cámara: {e}")
            return False

    def release_camera(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None

    def apply_image_adjustments(self, frame):
        """Aplica manualmente los ajustes de imagen al frame"""
        try:
            # Convertir a float32 para mayor precisión en los cálculos
            frame = frame.astype(np.float32) / 255.0
            
            # Aplicar brillo
            frame += self.settings['brightness'] / 100.0
            
            # Aplicar contraste
            frame = (frame - 0.5) * (1.0 + self.settings['contrast'] / 100.0) + 0.5
            
            # Aplicar saturación (solo si es imagen a color)
            if len(frame.shape) == 3:
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 1] *= 1.0 + self.settings['saturation'] / 100.0
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # Aplicar nitidez
            if self.settings['sharpness'] != 0:
                # Kernel de nitidez
                kernel = np.array([
                    [-1, -1, -1],
                    [-1,  9 + self.settings['sharpness'] / 20.0, -1],
                    [-1, -1, -1]
                ])
                frame = cv2.filter2D(frame, -1, kernel)
            
            # Aplicar exposición
            frame *= 1.0 + self.settings['exposure'] / 10.0
            
            # Asegurar valores dentro del rango [0, 1]
            np.clip(frame, 0, 1, out=frame)
            
            # Convertir de nuevo a uint8
            frame = (frame * 255).astype(np.uint8)
            
            return frame
        except Exception as e:
            print(f"Error aplicando ajustes de imagen: {e}")
            return frame

    def apply_filters(self, frame):
        try:
            # Aplicar filtros de color
            if self.settings['filter'] == 'grayscale':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            elif self.settings['filter'] == 'sepia':
                sepia_kernel = np.array([
                    [0.272, 0.534, 0.131],
                    [0.349, 0.686, 0.168],
                    [0.393, 0.769, 0.189]
                ])
                frame = cv2.transform(frame, sepia_kernel)
                frame = np.clip(frame, 0, 255).astype(np.uint8)
            elif self.settings['filter'] == 'red':
                frame[:, :, 0] = 0  # Canal azul
                frame[:, :, 1] = 0  # Canal verde
            elif self.settings['filter'] == 'green':
                frame[:, :, 0] = 0  # Canal azul
                frame[:, :, 2] = 0  # Canal rojo
            elif self.settings['filter'] == 'blue':
                frame[:, :, 1] = 0  # Canal verde
                frame[:, :, 2] = 0  # Canal rojo
            elif self.settings['filter'] == 'ir':
                # Simulación de infrarrojo
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                frame = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
            elif self.settings['filter'] == 'uv':
                # Simulación de ultravioleta
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                hsv[:, :, 0] = 120  # Cambiar tono a violeta
                hsv[:, :, 1] = 255  # Saturación máxima
                frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            
            # Aplicar ajustes de imagen
            frame = self.apply_image_adjustments(frame)
            
            # Sobrepone timestamp
            if self.settings['overlay_timestamp']:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(
                    frame, timestamp, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1
                )
            
            return frame
        except Exception as e:
            print(f"Error aplicando filtros: {e}")
            return frame

    def generate_frames(self):
        while self.active:
            if not self.cap or not self.cap.isOpened():
                time.sleep(0.1)
                continue
                
            try:
                with self.frame_lock:
                    success, frame = self.cap.read()
                    if not success:
                        # Usar último frame válido si hay problema
                        if self.last_frame is not None:
                            frame = self.last_frame.copy()
                        else:
                            time.sleep(0.1)
                            continue
                    else:
                        self.last_frame = frame.copy()
                    
                    frame = self.apply_filters(frame)
                    
                    # Redimensionar para transmisión
                    max_stream_size = (1280, 720)
                    if frame.shape[1] > max_stream_size[0] or frame.shape[0] > max_stream_size[1]:
                        frame = cv2.resize(frame, max_stream_size)
                    
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if not ret:
                        continue
                        
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.01)
            except Exception as e:
                print(f"Error generando frame: {e}")
                time.sleep(0.1)

    def capture_photo(self, filename):
        if not self.cap or not self.cap.isOpened():
            raise Exception("Cámara no disponible")
        
        try:
            with self.frame_lock:
                success, frame = self.cap.read()
                if not success:
                    raise Exception("Error al capturar foto")
                
                frame = self.apply_filters(frame)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                full_path = os.path.join(
                    self.save_path,
                    f"{self.filename_prefix}{filename}_{timestamp}.jpg"
                )
                cv2.imwrite(full_path, frame)
                return full_path
        except Exception as e:
            raise Exception(f"Error capturando foto: {e}")

    def start_video(self, filename):
        if self.recording:
            return "La grabación ya está en progreso"
        
        try:
            resolution = self.settings['resolution']
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            full_path = os.path.join(
                self.save_path,
                f"{self.filename_prefix}{filename}_{timestamp}.avi"
            )
            
            self.video_writer = cv2.VideoWriter(
                full_path, 
                fourcc, 
                20.0, 
                resolution
            )
            if not self.video_writer.isOpened():
                return f"Error al crear el archivo de video: {full_path}"
            
            self.recording = True
            
            # Hilo para captura de video
            def video_capture_thread():
                while self.recording and self.cap and self.cap.isOpened():
                    try:
                        with self.frame_lock:
                            success, frame = self.cap.read()
                            if success:
                                frame = self.apply_filters(frame)
                                self.video_writer.write(frame)
                    except:
                        pass
                    time.sleep(0.05)
            
            threading.Thread(target=video_capture_thread, daemon=True).start()
            return full_path
        except Exception as e:
            return f"Error iniciando video: {e}"

    def stop_video(self):
        if not self.recording:
            return "No hay grabación en curso"
        
        try:
            self.recording = False
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None
            return "Grabación detenida"
        except Exception as e:
            return f"Error deteniendo video: {e}"

    def start_timelapse(self, filename, interval, duration):
        if self.timelapse_active:
            return "Timelapse ya en progreso"
        
        try:
            self.timelapse_active = True
            
            def timelapse_thread():
                start_time = time.time()
                frame_count = 0
                
                while time.time() - start_time < duration and self.timelapse_active:
                    try:
                        with self.frame_lock:
                            success, frame = self.cap.read()
                            if success:
                                frame = self.apply_filters(frame)
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                frame_path = os.path.join(
                                    self.save_path,
                                    f"{self.filename_prefix}{filename}_{timestamp}_{frame_count}.jpg"
                                )
                                cv2.imwrite(frame_path, frame)
                                frame_count += 1
                    except Exception as e:
                        print(f"Error en timelapse: {e}")
                    
                    time.sleep(interval)
                
                self.timelapse_active = False
            
            threading.Thread(target=timelapse_thread, daemon=True).start()
            return f"Timelapse iniciado: {duration} segundos con intervalo {interval}s"
        except Exception as e:
            return f"Error iniciando timelapse: {e}"
    
    def cleanup(self):
        self.active = False
        self.stop_video()
        self.timelapse_active = False
        self.release_camera()

# Crear instancia de CameraManager
cam_manager = CameraManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cameras')
def get_cameras():
    cameras = cam_manager.list_cameras()
    return jsonify([{"id": idx, "name": f"Cámara {idx}"} for idx in cameras])

@app.route('/select_camera', methods=['POST'])
def select_camera():
    data = request.json
    camera_id = int(data['camera_id'])
    try:
        success = cam_manager.select_camera(camera_id)
        return jsonify(success=success)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    try:
        if 'resolution' in data and isinstance(data['resolution'], str):
            res_values = data['resolution'].split(',')
            data['resolution'] = (int(res_values[0]), int(res_values[1]))
        
        # Convertir valores numéricos
        if 'brightness' in data: data['brightness'] = int(data['brightness'])
        if 'contrast' in data: data['contrast'] = int(data['contrast'])
        if 'saturation' in data: data['saturation'] = int(data['saturation'])
        if 'sharpness' in data: data['sharpness'] = int(data['sharpness'])
        if 'exposure' in data: data['exposure'] = float(data['exposure'])
        
        cam_manager.settings.update(data)
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

@app.route('/video_feed')
def video_feed():
    return Response(
        cam_manager.generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    capture_type = data['type']
    filename = data.get('filename', 'capture')
    
    try:
        if capture_type == 'photo':
            result = cam_manager.capture_photo(filename)
            return jsonify(success=True, message=f"Foto guardada: {result}")
        elif capture_type == 'video':
            action = data['action']
            if action == 'start':
                result = cam_manager.start_video(filename)
                return jsonify(success=True, message=f"Grabación iniciada: {result}")
            else:
                result = cam_manager.stop_video()
                return jsonify(success=True, message=result)
        elif capture_type == 'timelapse':
            interval = int(data['interval'])
            duration = int(data['duration'])
            result = cam_manager.start_timelapse(filename, interval, duration)
            return jsonify(success=True, message=result)
        else:
            return jsonify(success=False, error="Tipo de captura inválido"), 400
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500

@app.route('/set_save_path', methods=['POST'])
def set_save_path():
    data = request.json
    path = data.get('path', 'captures')
    try:
        if not os.path.exists(path):
            os.makedirs(path)
        cam_manager.save_path = path
        return jsonify(success=True, message=f"Carpeta destino actualizada: {path}")
    except Exception as e:
        return jsonify(success=False, error=str(e)), 400

def find_available_port(start_port, max_tries=10):
    port = start_port
    for _ in range(max_tries):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', port))
            return port
        except OSError:
            port += 1
    return None

def cleanup_resources():
    cam_manager.cleanup()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Control de Cámaras Web')
    parser.add_argument('--port', type=int, default=5000, 
                       help='Puerto inicial (por defecto: 5000)')
    args = parser.parse_args()

    port = find_available_port(args.port)
    if port is None:
        print(f"No se pudo encontrar un puerto disponible en el rango {args.port}-{args.port+10}")
        sys.exit(1)

    print(f"Iniciando servidor en el puerto {port}")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    finally:
        cleanup_resources()