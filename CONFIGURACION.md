# 🔧 Guía de Configuración

Esta guía te ayudará a configurar correctamente el Creador de Historias Visuales.

## 📋 Prerrequisitos

### 1. Python 3.12+
Verifica tu versión de Python:
```bash
python --version
```

Si no tienes Python instalado, descárgalo desde [python.org](https://python.org).

### 2. Gestor de Paquetes
Recomendamos **uv** para gestión de dependencias:
```bash
# Instalar uv
pip install uv
```

## 🔑 Configuración de APIs

### 1. Google Gemini API
1. Ve a [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nueva clave API
3. Copia la clave para usar en `.env`

### 2. Supabase
1. Crea una cuenta en [Supabase](https://supabase.com)
2. Crea un nuevo proyecto
3. Ve a Settings > API
4. Copia las siguientes claves:
   - `URL`
   - `anon/public key`
   - `service_role key`

### 3. AgentOps (Opcional)
1. Crea una cuenta en [AgentOps](https://agentops.ai)
2. Obtén tu API key del dashboard
3. Úsala para monitoreo de agentes

## 📄 Archivo .env

Crea un archivo `.env` en la raíz del proyecto:

```env
# ===== CONFIGURACIÓN OBLIGATORIA =====

# Google Gemini API
GEMINI_API_KEY=AIzaSy...tu_clave_aqui

# Supabase Configuration
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SECRET_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ===== CONFIGURACIÓN OPCIONAL =====

# AgentOps (para monitoreo)
AGENTOPS_API_KEY=tu_clave_agentops
CREWAI_TRACING_ENABLED=true
```

## 🗄️ Configuración de Base de Datos

### 1. Ejecutar Script SQL
1. Ve a tu proyecto de Supabase
2. Abre el SQL Editor
3. Copia y pega el contenido de `setup_database.sql`
4. Ejecuta el script

### 2. Verificar Configuración
El script creará:
- Tabla `stories` para historias
- Tabla `story_versions` para versionado
- Bucket `story-images` para imágenes
- Políticas de seguridad (RLS)

## 🚀 Instalación de Dependencias

### Opción 1: Con uv (Recomendado)
```bash
uv sync
```

### Opción 2: Instalación en modo desarrollo
```bash
uv pip install -e .
```

### Opción 3: Solo instalar dependencias
```bash
uv pip install streamlit crewai python-dotenv supabase transformers torch torchvision Pillow reportlab markdown agentops
```

## ✅ Verificación del Sistema

Ejecuta el script de pruebas:
```bash
python test_system.py
```

Este script verificará:
- ✅ Variables de entorno
- ✅ Dependencias instaladas
- ✅ Configuración del modelo
- ✅ Herramientas de análisis
- ✅ Conexión a Supabase
- ✅ Sistema de archivos

## 🚀 Ejecutar la Aplicación

### Opción 1: Script de inicio
```bash
python run.py
```

### Opción 2: Streamlit directo
```bash
streamlit run main.py
```

### Opción 3: Windows (Batch)
```bash
run.bat
```

## 🔍 Solución de Problemas Comunes

### Error: "ModuleNotFoundError"
**Problema**: Dependencias no instaladas
**Solución**: 
```bash
uv sync
# o
uv pip install -e .
```

### Error: "Invalid API Key"
**Problema**: Clave API incorrecta o expirada
**Solución**: 
1. Verifica que la clave esté correcta en `.env`
2. Regenera la clave en el servicio correspondiente

### Error: "Connection refused" (Supabase)
**Problema**: Configuración de Supabase incorrecta
**Solución**:
1. Verifica URL y claves en `.env`
2. Asegúrate de que el proyecto esté activo
3. Verifica que las tablas existan

### Error: "Permission denied" (Supabase)
**Problema**: Políticas RLS mal configuradas
**Solución**:
1. Ejecuta nuevamente `setup_database.sql`
2. Verifica que las políticas estén activas
3. Usa `service_role_key` para operaciones administrativas

### Error: "Model download failed"
**Problema**: Primera ejecución de BLIP
**Solución**:
1. Asegúrate de tener conexión a internet
2. Espera a que se descargue el modelo (puede tardar)
3. Verifica espacio en disco (>2GB)

### Error: "Port already in use"
**Problema**: Puerto 8501 ocupado
**Solución**:
```bash
streamlit run main.py --server.port 8502
```

## 📊 Configuración Avanzada

### Cambiar Modelo de IA
Edita `Models/gemini.py`:
```python
gemini_llm = LLM(
    model="gemini-2.0-flash",  # Cambia el modelo
    api_key=gemini_api_key,
    temperature=0.7  # Ajusta creatividad
)
```

### Personalizar Agentes
Edita `crew/agents.py` para modificar:
- Roles y objetivos
- Backstories (personalidad)
- Herramientas disponibles

### Añadir Nuevas Plataformas
1. Crea nuevo agente en `agents.py`
2. Añade tarea en `tasks.py`
3. Integra en `story_crew.py`

## 🔒 Seguridad

### Variables de Entorno
- ❌ Nunca subas `.env` a repositorios públicos
- ✅ Usa `.env.example` para plantillas
- ✅ Rota claves API regularmente

### Supabase
- ✅ Usa Row Level Security (RLS)
- ✅ Limita permisos por usuario
- ✅ Monitorea uso de API

### Archivos Locales
- ✅ Limita tamaño de uploads (200MB)
- ✅ Valida tipos de archivo
- ✅ Limpia archivos temporales

## 📞 Obtener Ayuda

Si tienes problemas:

1. **Revisa esta guía** completa
2. **Ejecuta** `python test_system.py`
3. **Consulta** los logs de error
4. **Busca** en issues del repositorio
5. **Crea** un nuevo issue con detalles

---

**¡Listo para crear contenido increíble! 🎉**