# CamControl
## Aplicación Web de Control de Cámaras

La estructura del proyecto para esta nueva versión optimizada es la siguiente:

```text
CamControl/
│
├── app.py                 # Script principal de la aplicación Flask
│
├── templates/
│   └── index.html          # Plantilla HTML con interfaz completa
│
├── captures/               # Carpeta para almacenar fotos/videos (se crea automáticamente)
│
└── requirements.txt        # Archivo de dependencias
```

## Explicación de la estructura:

### app.py - El corazón de la aplicación:
Maneja todas las rutas de Flask
Gestiona la detección y control de cámaras
Procesa los frames de video
Implementa la lógica de captura (fotos, videos, timelapse)
Administra los recursos y evita fugas de memoria
Incluye argumentos para especificar el puerto (--port)

### templates/index.html - Interfaz de usuario completa:
HTML con Tailwind CSS para estilos modernos
CSS integrado con efectos visuales avanzados
JavaScript completo para interactuar con el backend
Diseño responsive y optimizado para control de cámara
Previsualizaciones de filtros con iconos representativos

### captures/ - Directorio de capturas:
Se crea automáticamente al iniciar la aplicación
Almacena todas las fotos, videos y timelapses
La ruta puede cambiarse desde la interfaz web

### requirements.txt - Dependencias:
```text
flask
opencv-python
numpy
```

## Características técnicas clave:

Manejo robusto de recursos:
Uso de locks para acceso seguro a la cámara en múltiples hilos
Limpieza adecuada al cerrar la aplicación
Recuperación de errores con último frame válido
Comprobación de compatibilidad de propiedades de cámara
Sistema de filtros avanzado:
Original
Escala de grises
Sepia
Rojo
Verde
Azul
IR (simulado con mapa de colores)
UV (simulado con ajuste HSV)
Optimizaciones de rendimiento:
Reducción de calidad de transmisión (85%)
Redimensionamiento inteligente de frames
Actualizaciones por eventos (no por polling)
Hilos separados para capturas largas (video, timelapse)
Experiencia de usuario mejorada:
Indicadores visuales de estado
Notificaciones emergentes
Animaciones sutiles para acciones
Previsualización de filtros con iconos
Diseño oscuro con contraste adecuado

## Instrucciones de ejecución:

Instalar dependencias:
```bash
pip install -r requirements.txt
```
Ejecutar la aplicación (con búsqueda automática de puerto):
```bash
python app.py
```
O especificar puerto manualmente:
```bash
python app.py --port 5005
```
Acceder en el navegador:
```text
http://localhost:[puerto]
```
Esta estructura minimalista pero completa asegura un funcionamiento óptimo en Windows, macOS y Linux, con un manejo adecuado de permisos y recursos del sistema. La interfaz unificada en un solo archivo HTML simplifica el despliegue mientras mantiene un alto nivel de funcionalidad y diseño.
