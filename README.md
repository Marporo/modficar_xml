# Modificador XML - (Versión Local Definitiva)

Este repositorio (rama `main`) alberga la versión estable, definitiva y de escritorio (con GUI) del Modificador Automático de XML. Esta versión evolucionó fuertemente desde su concepción básica hasta convertirse en una herramienta de procesamiento masivo.

> **NOTA DE ARQUITECTURA:** Si buscas la versión Web (Flask), debes cambiar a la rama `feat/web-version`.

---

## 🚀 Capacidades y Funciones Principales

A través del archivo `main_app.py` (Controlador de Interfaz) y `xml_modifier.py` (Núcleo Lógico), la aplicación ofrece:

### 1. Sistema Moderno de Pestañas
La Interfaz (Tkinter y UI\_Theme moderno) se divide en tres áreas clave:
- **Modificar XML:** Procesamiento de datos.
- **Historial:** Carga, lectura y trazabilidad de todos los cambios de sesión.
- **Ayuda:** Documentación embebida que funciona sin conexión, explicando detalladamente aspectos complejos como el uso de Expresiones Regulares.

### 2. Procesamiento Masivo (Bulk Editing)
Esta versión elimina el cuello de botella de "un archivo a la vez". Gracias al rediseño del controlador, el usuario puede seleccionar un *Directorio Entero*. El núcleo iterará automáticamente, cambiando la etiqueta en múltiples documentos simultáneamente y reportando resultados parciales apoyado en una barra de progreso que lee las actualizaciones.

### 3. Motor de Búsqueda Avanzado (Regex)
Soporte completo para el motor `re` (Expresiones Regulares). Permite buscar atributos y textos no de forma estática, sino encontrando patrones variables (ignorando mayúsculas, hallando prefijos/sufijos). 

### 4. Trazabilidad
Todos los cambios se registran en una grilla interactiva que permite rastrear: `Fecha | Archivo | Etiqueta Cambiada | Valores (X -> Y)`.  Asimismo, se soporta la exportación a archivos `.json` para auditoría externa.

---

## 📦 Compilación e Instalación

El proyecto está preparado para no depender de la consola. El código base contiene un archivo `modificador_xml.spec` preparado para la plataforma de instalación de PyInstaller.

Para exportar esta aplicación como un archivo nativo ejecutable (.exe o .app) sin requerir que los usuarios tengan Python en sus computadoras:

```bash
pip install pyinstaller
pyinstaller modificador_xml.spec
```
Esto utilizará los iconos `propelimg.ico` o `xmlimg.ico` localizados en la raíz para construirte un programa completo en una carpeta independiente.
