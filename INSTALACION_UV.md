# 🚀 Guía de Instalación con UV

Esta guía te ayudará a instalar y configurar el proyecto usando **uv**, el gestor de paquetes moderno y rápido para Python.

## 📋 Prerrequisitos

### 1. Instalar UV
Si no tienes uv instalado, puedes instalarlo de varias formas:

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### Con pip (si ya tienes Python)
```bash
pip install uv
```

### 2. Verificar instalación
```bash
uv --version
```

## 🔧 Instalación del Proyecto

### 1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd streamlitcrewai
```

### 2. Sincronizar dependencias
```bash
uv sync
```

Este comando:
- ✅ Crea un entorno virtual automáticamente
- ✅ Instala todas las dependencias del `pyproject.toml`
- ✅ Genera el archivo `uv.lock` para reproducibilidad
- ✅ Configura el proyecto en modo desarrollo

### 3. Verificar instalación
```bash
uv run python test_system.py
```

## 🚀 Ejecutar la Aplicación

### Opción 1: Con uv run (Recomendado)
```bash
uv run streamlit run main.py
```

### Opción 2: Activar entorno y ejecutar
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Luego ejecutar
streamlit run main.py
```

### Opción 3: Script de inicio
```bash
uv run python run.py
```

## 🔄 Gestión de Dependencias

### Agregar nueva dependencia
```bash
uv add nombre-del-paquete
```

### Agregar dependencia de desarrollo
```bash
uv add --dev nombre-del-paquete
```

### Actualizar dependencias
```bash
uv sync --upgrade
```

### Remover dependencia
```bash
uv remove nombre-del-paquete
```

## 🛠️ Comandos Útiles

### Ver dependencias instaladas
```bash
uv pip list
```

### Información del entorno
```bash
uv info
```

### Limpiar cache
```bash
uv cache clean
```

### Exportar requirements (si necesario)
```bash
uv pip freeze > requirements.txt
```

## 🔍 Solución de Problemas

### Error: "uv: command not found"
**Solución**: Reinstala uv o agrega al PATH
```bash
# Verificar instalación
which uv  # macOS/Linux
where uv  # Windows
```

### Error: "No module named 'xxx'"
**Solución**: Sincronizar dependencias
```bash
uv sync
```

### Error: "Permission denied"
**Solución**: Ejecutar con permisos o usar --user
```bash
uv sync --user
```

### Entorno virtual corrupto
**Solución**: Recrear entorno
```bash
rm -rf .venv  # Eliminar entorno
uv sync       # Recrear
```

## 🎯 Ventajas de UV

- ⚡ **Velocidad**: 10-100x más rápido que pip
- 🔒 **Reproducibilidad**: Lock files automáticos
- 🎯 **Simplicidad**: Un solo comando para todo
- 🔄 **Compatibilidad**: Funciona con pip y pyproject.toml
- 🛡️ **Seguridad**: Verificación de integridad automática

## 📚 Recursos Adicionales

- [Documentación oficial de uv](https://docs.astral.sh/uv/)
- [Guía de migración desde pip](https://docs.astral.sh/uv/pip/)
- [Comparación de rendimiento](https://astral.sh/blog/uv)

---

**¡Disfruta de la velocidad y simplicidad de uv! 🚀**