# XML Modifier Pro - Documentación de Arquitectura Técnica

Este documento describe la arquitectura de software, los patrones de diseño y las decisiones técnicas adoptadas en la plataforma **XML Modifier Pro**. Está diseñado para proporcionar una comprensión profunda del sistema a desarrolladores y auditores técnicos.

---

## 1. Visión General del Sistema
La plataforma es una aplicación web full-stack diseñada para el procesamiento masivo y seguro de archivos XML. El sistema permite la identificación dinámica de nodos, el reemplazo de valores y el mantenimiento de una trazabilidad completa de las modificaciones por usuario.

---

## 2. Patrón Arquitectónico: MVC (Model-View-Controller)
El proyecto implementa una variante del patrón **Modelo-Vista-Controlador**, asegurando una clara separación de responsabilidades (*Separation of Concerns*).

### A. Capa de Datos (Model) - `models.py`
Utiliza **SQLAlchemy ORM** para abstraer la base de datos relacional (**SQLite**).
- **User**: Gestiona la identidad, perfiles y autenticación (Sessions).
- **XMLActivity**: Entidad de auditoría que vincula metadatos del proceso con archivos físicos en disco.

### B. Capa de Lógica de Negocio (Core) - `core/xml_modifier.py`
Se comporta como un **Motor de Procesamiento Agnostico**. 
- **Desacoplamiento**: No tiene dependencias de protocolos de red (HTTP) ni de interfaces de usuario.
- **Funcionalidad**: Implementa algoritmos de manipulación de árboles DOM (`xml.etree.ElementTree`) y motores de búsqueda por expresiones regulares (`re`).

### C. Capa de Servicio y Control (Controller) - `app.py`
Actúa como el orquestador central del sistema utilizando el framework **Flask**.
- **Gestión de Sesiones**: Implementada mediante `Flask-Login`.
- **API RESTful**: Expone endpoints JSON para operaciones asíncronas desde el cliente (Detección de etiquetas, valores y previsualización de cambios).

---

## 3. Estrategia de Persistencia y Almacenamiento Híbrido
Para optimizar el rendimiento y la escalabilidad, el sistema utiliza un enfoque híbrido:

1.  **Metadatos (Structured Data)**: El historial, usuarios y rutas se almacenan en la base de datos relacional.
2.  **Archivos Binarios (Unstructured Data)**: Los documentos XML originales y modificados se almacenan en el sistema de archivos (`storage/`), organizados por estados:
    - `/originals`: Archivos fuente inalterados.
    - `/modified`: Archivos resultantes tras el proceso de negocio.
    - `/temp`: Almacenamiento volátil para análisis en tiempo real vía AJAX.

---

## 4. Seguridad y Robustez
- **Criptografía**: Las credenciales de usuario se protegen mediante hashing **PBKDF2 con SHA256**, garantizando que la información sensible nunca se almacene en texto plano.
- **Sanitización**: Todas las entradas de archivos se procesan mediante `secure_filename` para prevenir ataques de Directory Traversal.
- **Simulación (Pre-flight Check)**: El sistema permite ejecutar transacciones en modo `preview=True` para devolver al usuario un resumen de impacto antes de persistir cambios en disco.

---

## 5. Frontend y Diseño Visual
La interfaz está construida sobre estándares de **HTML5 Semántico** y **CSS3 nativo** (sin frameworks pesados), priorizando la velocidad de carga y la estética moderna (**Glassmorphism**).
- **Componentes Custom**: Se utilizan dropdowns personalizados para evitar el autocompletado intrusivo de los navegadores y mejorar la experiencia de usuario personalizada.

---

## 6. Mantenimiento y Calidad
- **Aislamiento**: La arquitectura permite realizar cambios en la lógica de procesamiento (`core/`) sin afectar la disponibilidad del servidor web, facilitando las pruebas unitarias.
- **Logs**: Se registran operaciones críticas en `app.log` para auditoría y resolución de problemas.
