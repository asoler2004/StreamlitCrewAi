# 📖 Creador de Historias Visuales con CrewAI

Una aplicación completa desarrollada con CrewAI y Streamlit para crear contenido visual atractivo para redes sociales (Facebook, LinkedIn, Instagram, Twitter) con almacenamiento local y remoto.

## 🚀 Características Principales

### 🤖 Agentes Especializados
- **Agente de Interacción**: Gestiona la comunicación con el usuario
- **Agente de Visión**: Analiza imágenes usando BLIP para generar descripciones detalladas
- **Agentes de Plataforma**: Especializados en crear contenido para cada red social
  - Facebook: Contenido engaging con hooks atractivos
  - LinkedIn: Contenido profesional y de networking
  - Instagram: Captions visuales optimizados
  - Twitter/X: Contenido conciso e impactante
- **Agente de Almacenamiento**: Gestiona el guardado local y remoto

### 📱 Plataformas Soportadas
- **Facebook**: Posts optimizados para engagement
- **LinkedIn**: Contenido profesional y thought leadership
- **Instagram**: Captions que complementan imágenes
- **Twitter/X**: Tweets concisos y threads

### 💾 Opciones de Almacenamiento
- **Local**: JSON, Markdown, HTML, PDF
- **Remoto**: Base de datos Supabase con storage de imágenes
- **Híbrido**: Combinación de ambos

### 🎨 Personalización
- **Tonos**: Profesional, Divertido, Inspiracional, Educativo, Casual, Formal
- **Especificaciones**: Texto libre para requisitos específicos
- **Análisis Visual**: Descripción automática de imágenes

## 🛠️ Instalación

### Prerrequisitos
- Python 3.12+
- uv (recomendado) o pip

### Pasos de Instalación

1. **Clonar el repositorio**
```bash
git clone <tu-repositorio>
cd streamlitcrewai
```

2. **Instalar dependencias**
```bash
# Con uv (recomendado)
uv sync

# O con pip
pip install -e .
```

3. **Configurar variables de entorno**
Crea un archivo `.env` en la raíz del proyecto:
```env
# Clave API de Gemini
GEMINI_API_KEY=tu_clave_de_gemini

# Configuración de Supabase
SUPABASE_URL=tu_url_de_supabase
SUPABASE_KEY=tu_clave_publica_de_supabase
SUPABASE_SECRET_KEY=tu_clave_secreta_de_supabase
SUPABASE_SERVICE_ROLE_KEY=tu_clave_de_servicio

# AgentOps (opcional, para monitoreo)
AGENTOPS_API_KEY=tu_clave_de_agentops
CREWAI_TRACING_ENABLED=true
```

4. **Configurar base de datos Supabase**
Ejecuta el script SQL en `setup_database.sql` en tu panel de Supabase.

## 🚀 Uso

### Ejecutar la aplicación
```bash
streamlit run main.py
```

### Flujo de Trabajo

1. **Seleccionar Imagen**: Sube una imagen desde tu dispositivo
2. **Configurar Historia**: 
   - Selecciona la plataforma de destino
   - Elige el tono deseado
   - Añade especificaciones adicionales (opcional)
3. **Generar Contenido**: El sistema analiza la imagen y crea contenido optimizado
4. **Revisar y Aprobar**: Revisa el contenido generado
5. **Almacenar**: Guarda en formato local y/o remoto

### Ver Historias Archivadas
- **Locales**: Navega por historias guardadas en tu dispositivo
- **Remotas**: Accede a historias almacenadas en Supabase
- **Usar como Plantilla**: Reutiliza historias existentes

## 📁 Estructura del Proyecto

```
streamlitcrewai/
├── main.py                 # Aplicación principal de Streamlit
├── crew/                   # Módulos de CrewAI
│   ├── agents.py          # Definición de agentes
│   ├── tasks.py           # Definición de tareas
│   └── story_crew.py      # Orquestador principal
├── Models/                 # Configuración de modelos
│   └── gemini.py          # Configuración de Gemini
├── Tools/                  # Herramientas personalizadas
│   └── blip_caption_tool.py # Herramienta de análisis de imágenes
├── utils/                  # Utilidades
│   ├── config.py          # Gestión de configuración
│   ├── supabase_client.py # Cliente de Supabase
│   └── file_manager.py    # Gestión de archivos locales
├── stories/               # Directorio de historias locales
├── setup_database.sql     # Script de configuración de BD
├── .env                   # Variables de entorno
└── pyproject.toml         # Configuración del proyecto
```

## 🔧 Configuración Avanzada

### Personalizar Agentes
Los agentes están definidos en `crew/agents.py`. Puedes modificar:
- Roles y objetivos
- Backstories para cambiar el comportamiento
- Herramientas disponibles

### Añadir Nuevas Plataformas
1. Crear nuevo agente en `agents.py`
2. Añadir tarea correspondiente en `tasks.py`
3. Integrar en el flujo de `story_crew.py`

### Modificar Formatos de Salida
Los formatos de exportación se gestionan en `utils/file_manager.py`:
- JSON: Estructura de datos completa
- Markdown: Formato legible
- HTML: Versión web estilizada
- PDF: Documento profesional

## 🔍 Solución de Problemas

### Error de Variables de Entorno
- Verifica que el archivo `.env` esté en la raíz del proyecto
- Asegúrate de que todas las claves API sean válidas
- Reinicia la aplicación después de cambiar variables

### Problemas con Supabase
- Verifica la configuración de RLS (Row Level Security)
- Asegúrate de que el bucket `story-images` exista
- Comprueba los permisos de las tablas

### Errores de Modelo
- Verifica que la clave de Gemini sea válida
- Comprueba la conectividad a internet
- Revisa los logs de CrewAI para detalles

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 🙏 Agradecimientos

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Framework de agentes AI
- [Streamlit](https://streamlit.io/) - Framework de aplicaciones web
- [Supabase](https://supabase.com/) - Backend como servicio
- [BLIP](https://github.com/salesforce/BLIP) - Modelo de análisis de imágenes
- [Google Gemini](https://ai.google.dev/) - Modelo de lenguaje

## 📞 Soporte

Si tienes preguntas o necesitas ayuda:
1. Revisa la documentación
2. Busca en los issues existentes
3. Crea un nuevo issue con detalles del problema

---

**¡Crea contenido visual impactante con el poder de la IA! 🚀**