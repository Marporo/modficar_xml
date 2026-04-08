# XML Modifier Pro - Documentación de Arquitectura

Bienvenido al esquema técnico del **Modificador XML**. Este documento detalla la estructura del proyecto y ayuda a los nuevos desarrolladores a entender las decisiones de diseño adoptadas.

## 🎯 Objetivo de la Aplicación
Permitir a los usuarios y sistemas procesar masivamente archivos XML (identificando etiquetas específicas y valores a reemplazar) a través de una interfaz interactiva y segura, sin requerir conocimientos de programación.

---

## 🏗️ Arquitectura General: "Core Compartido" (Separation of Concerns)

Decidimos estructurar este repositorio separando de manera estricta la **lógica profunda del negocio** de la **capa visual**. 

Este proyecto sigue una arquitectura puramente orientada a la web (Web-first), pero reteniendo la capacidad teórica de extenderse gracias al aislamiento de su núcleo.

### Estructura de Directorios

```text
/
├── app.py                 # (Camarero) - Recibe las peticiones de los usuarios.
├── core/                  # (Cocina) - Todo lo que requiere procesamiento matemático y lógico.
│   └── xml_modifier.py    # Motor principal de manipulación XML.
├── templates/             # (Decoración) - Estructuras HTML5 (El esqueleto).
│   └── index.html
└── static/                # (Pintura y Efectos) - Archivos CSS y JavaScript.
    └── css/
        └── style.css
```

---

## 🧠 Explicación de los Componentes (Módulos)

### 1. `core/xml_modifier.py` (Lógica de Negocio)
Este es el "Cerebro" de la aplicación.
- **Función:** Recibe órdenes genéricas (Ej: "Toma esta ruta de archivo, busca la etiqueta X que tenga valor Y, y ponle Z").
- **Independencia Total:** Este archivo no usa bibliotecas web (`Flask`) ni bibliotecas de escritorio (`Tkinter`). Solo sabe leer `.xml` usando `xml.etree.ElementTree`.
- **Ventaja:** Si el día de mañana queremos hacer una aplicación de terminal o un bot de Telegram, el bot simplemente llamará a `xml_modifier.py` y funcionará perfectamente sin modificar ni una coma.

### 2. `app.py` (Controlador / Enrutador)
Este es el puente entre el Internet exterior y el cerebro de la aplicación.
- **Función:** Utiliza `Flask` para abrir un puerto web (usualmente `5001`). Su trabajo es escuchar cuando un navegador intenta conectarse o enviar un formulario por Método `POST`.
- **Flujo:** Toma el archivo subido de forma insegura, lo sanitiza usando `secure_filename`, lo guarda temporalmente y "llama al cocinero" (`core/xml_modifier.py`). Luego envía el archivo resultante como una descarga al usuario (Response).

### 3. `templates/` y `static/` (El Frente)
Toda la interfaz visual de la aplicación.
- **Frontend Moderno:** Hemos implementado diseño líquido ("Glassmorphism"), paletas de Modo Oscuro, y una arquitectura CSS con `CSS Variables` preparadas para futura integración de temas.
- **UX:** Todo el código relacionado con drag-and-drop de archivos ocurre aquí, facilitando la vida al usuario antes de que sus datos siquieran toquen a `app.py`.

---

## 🚀 Cómo ejecutar en desarrollo

Para iniciar el servidor localmente:

```bash
# 1. Asegúrate de tener Flask instalado (pip install -r requirements.txt)
# 2. Ejecuta el servidor principal
python3 app.py
```
> El servicio estará disponible en http://127.0.0.1:5001
