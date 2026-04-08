"""
app.py - Controlador Principal (Capa de Presentación Web)

Este archivo actúa como el "Camarero" del proyecto.
Su única responsabilidad es abrir un servidor web web mediante Flask,
recibir las peticiones HTTP del usuario (formularios y archivos cargados),
y pasarle esos datos a nuestro núcleo de procesamiento (El "Cocinero").
No contiene lógica profunda sobre cómo modificar un XML, solo sabe cómo
recibir solicitudes y devolver respuestas.
"""

import os
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

# Importamos la lógica de negocio desde nuestro núcleo aislado
from core.xml_modifier import modificar_xml

app = Flask(__name__)
app.secret_key = "xml_modifier_secret_key"
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Asegurar que la carpeta de subidas existe
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No se subió ningún archivo')
        return redirect(request.url)
    
    file = request.files['file']
    etiqueta = request.form.get('etiqueta')
    valor_actual = request.form.get('valor_actual')
    valor_nuevo = request.form.get('valor_nuevo')
    
    if file.filename == '':
        flash('Archivo no seleccionado')
        return redirect(request.url)
        
    if not all([etiqueta, valor_actual, valor_nuevo]):
        flash('Todos los campos son obligatorios')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Procesar el XML usando la lógica existente
            cambios = modificar_xml(filepath, etiqueta, valor_actual, valor_nuevo)
            
            if cambios > 0:
                # Devolver el archivo modificado para descarga
                return send_file(filepath, as_attachment=True, download_name=f"modificado_{filename}")
            else:
                flash(f"No se encontraron coincidencias para la etiqueta '{etiqueta}' con el valor '{valor_actual}'")
                return redirect(url_for('index'))
                
        except Exception as e:
            flash(f"Error al procesar el archivo: {str(e)}")
            return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
