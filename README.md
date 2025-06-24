# Seb-CamControl
## 🌐 Web Camera Control Application

Seb-CamControl is a modern web application built with Python and Flask that enables full control of USB and integrated cameras.

---

## 📁 Project Structure

```text
Seb-CamControl/
│
├── app.py                 # Main Flask app script
│
├── templates/
│   └── index.html         # UI template
│
├── captures/              # Auto-created folder for captures
│
└── requirements.txt       # Dependency file
```

---

## 🧠 Structure Explanation

### `app.py` – Application Core

- Handles all Flask routes  
- Detects and controls connected cameras  
- Processes video frames  
- Implements logic for capture (photo, video, timelapse)  
- Manages system resources and prevents memory leaks  
- Includes `--port` argument for manual port selection  

---

### `templates/index.html` – Full UI

- Modern styles using Tailwind CSS  
- Integrated CSS with advanced effects  
- Full JavaScript for backend interaction  
- Responsive design for camera control  
- Filter previews with representative icons  

---

### `captures/` – Capture Directory

- Created automatically when app starts  
- Stores all photos, videos, timelapses  
- Path can be changed from web UI  

---

### `requirements.txt` – Dependencies

```text
flask
opencv-python
numpy
```

---

## ⚙️ Key Technical Features

### Robust Resource Management

- Thread-safe access with locks  
- Proper cleanup on shutdown  
- Error recovery with last valid frame  
- Compatibility check for camera properties  

---

### Advanced Filter System

- Original  
- Grayscale  
- Sepia  
- Red  
- Green  
- Blue  
- IR (simulated with color map)  
- UV (simulated with HSV adjustment)  

---

### Performance Optimizations

- Stream quality reduced to 85%  
- Smart frame resizing  
- Event-based updates (no polling)  
- Separate threads for long captures (video, timelapse)  

---

### Enhanced User Experience

- Visual status indicators  
- Popup notifications  
- Subtle action animations  
- Filter preview with icons  
- Dark theme with proper contrast  

---

## ▶️ How to Run

### Install dependencies:
```bash
pip install -r requirements.txt
```

### Run the app with automatic port:
```bash
python app.py
```

### Or specify a port manually:
```bash
python app.py --port 5005
```

### Access in the browser:
```text
http://localhost:[port]
```

---

## 🧩 Compatibility & Deployment

This minimalist yet complete structure ensures smooth operation on **Windows, macOS, and Linux**, with proper system resource handling.

The unified single-file HTML interface simplifies deployment while maintaining high levels of functionality and design.

---

# Seb-CamControl
## 🌐 Aplicación Web de Control de Cámaras

Seb-CamControl es una aplicación web moderna construida con Python y Flask que permite el control completo de cámaras USB e integradas.

---

## 📁 Estructura del Proyecto

```text
Seb-CamControl/
│
├── app.py                 # Script principal de la aplicación Flask
│
├── templates/
│   └── index.html         # Plantilla HTML con la interfaz completa
│
├── captures/              # Carpeta para almacenar fotos/videos (se crea automáticamente)
│
└── requirements.txt       # Archivo de dependencias
```

---

## 🧠 Explicación de la Estructura

### `app.py` – El Corazón de la Aplicación

- Maneja todas las rutas de Flask  
- Gestiona la detección y control de cámaras  
- Procesa los frames de video  
- Implementa la lógica de captura (fotos, videos, timelapse)  
- Administra los recursos del sistema y evita fugas de memoria  
- Incluye argumento `--port` para especificar el puerto manualmente  

---

### `templates/index.html` – Interfaz de Usuario Completa

- HTML con estilos modernos usando Tailwind CSS  
- CSS integrado con efectos visuales avanzados  
- JavaScript completo para interactuar con el backend  
- Diseño responsive optimizado para control de cámara  
- Previsualizaciones de filtros con íconos representativos  

---

### `captures/` – Directorio de Capturas

- Se crea automáticamente al iniciar la aplicación  
- Almacena todas las fotos, videos y timelapses  
- La ruta puede cambiarse desde la interfaz web  

---

### `requirements.txt` – Dependencias

```text
flask
opencv-python
numpy
```

---

## ⚙️ Características Técnicas Clave

### Manejo Robusto de Recursos

- Uso de locks para acceso seguro a la cámara en múltiples hilos  
- Limpieza adecuada al cerrar la aplicación  
- Recuperación de errores con el último frame válido  
- Comprobación de compatibilidad de propiedades de cámara  

---

### Sistema de Filtros Avanzado

- Original  
- Escala de grises  
- Sepia  
- Rojo  
- Verde  
- Azul  
- IR (simulado con mapa de colores)  
- UV (simulado con ajuste HSV)  

---

### Optimizaciones de Rendimiento

- Reducción de calidad de transmisión (85%)  
- Redimensionamiento inteligente de frames  
- Actualizaciones por eventos (no por polling)  
- Hilos separados para capturas largas (video, timelapse)  

---

### Experiencia de Usuario Mejorada

- Indicadores visuales de estado  
- Notificaciones emergentes  
- Animaciones sutiles para acciones  
- Previsualización de filtros con íconos  
- Diseño oscuro con contraste adecuado  

---

## ▶️ Instrucciones de Ejecución

### Instalar dependencias:
```bash
pip install -r requirements.txt
```

### Ejecutar la aplicación (con búsqueda automática de puerto):
```bash
python app.py
```

### O especificar el puerto manualmente:
```bash
python app.py --port 5005
```

### Acceder desde el navegador:
```text
http://localhost:[puerto]
```

---

## 🧩 Compatibilidad y Despliegue

Esta estructura minimalista pero completa asegura un funcionamiento óptimo en **Windows, macOS y Linux**, con un manejo adecuado de permisos y recursos del sistema.

La interfaz unificada en un solo archivo HTML simplifica el despliegue, manteniendo un alto nivel de funcionalidad y diseño.

---
