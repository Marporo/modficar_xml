# XML Modifier Pro 🚀

**XML Modifier Pro** es una herramienta de escritorio potente y moderna diseñada para el procesamiento masivo de archivos XML. Construida con **Python 3** y **PyQt6**, ofrece una interfaz nativa inspirada en las guías de diseño de Apple, combinando estética premium con un motor de procesamiento robusto y asincrónico.

---

## ✨ Características Principales

-  **Interfaz Nativa (macOS Style)**: Diseño limpio, profesional y optimizado para una experiencia de usuario fluida.
- 🔍 **Filtrado Inteligente**: Buscador en tiempo real integrado en los selectores de etiquetas y valores.
- 🧠 **Modo Regex**: Soporte completo para expresiones regulares en búsquedas y reemplazos.
- ⚡ **Procesamiento Asincrónico**: Los cambios masivos se ejecutan en hilos separados para evitar bloqueos de la aplicación.
- 📁 **Modo Lote (Batch)**: Procese archivos individuales o carpetas completas con miles de archivos .xml en segundos.
- 📝 **Función [TODOS]**: Sobreescritura total de etiquetas simplificada.
- 📑 **Historial y Vista Previa**: Valide sus cambios antes de aplicarlos y mantenga un registro de todas las operaciones realizadas.

## 🛠️ Requisitos Técnicos

- **Python**: 3.9 o superior.
- **Dependencias**: Listadas en `requirements.txt` (PyQt6).
- **Sistema Operativo**: Optimizado para macOS (compatible con Windows y Linux).

## 🚀 Instalación Rápida

1. Clone el repositorio:
   ```bash
   git clone https://github.com/usuario/modificar_xml_repo.git
   cd modificar_xml_repo
   ```

2. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Lance la aplicación:
   ```bash
   python src/main.py
   ```

## 🏗️ Estructura del Proyecto

- `/src/core`: Lógica de negocio y motor de procesamiento XML.
- `/src/ui`: Interfaz gráfica, sistema de estilos y gestión de eventos.
- `/resources`: Iconografía vectorial (SVG) y assets.

Para más detalles sobre el diseño técnico, consulte el archivo [ARCHITECTURE.md](./ARCHITECTURE.md).

## 📦 Compilación (Crear .app para macOS)

Si desea generar un ejecutable independiente, utilice **PyInstaller**:

```bash
pyinstaller xml_modifier_pro.spec
```

---
*Desarrollado con enfoque en la eficiencia y la precisión técnica.*
