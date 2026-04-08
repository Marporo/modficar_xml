"""
app.py - Controlador Principal Pro (Plataforma XML)

Este archivo gestiona la autenticación, la base de datos y la orquestación
entre la interfaz web y el núcleo de procesamiento core/xml_modifier.py.
"""

import os
from datetime import datetime
from flask import Flask, render_template, request, send_file, flash, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Importaciones locales
from models import db, User, XMLActivity
from core.xml_modifier import modificar_xml, obtener_etiquetas_unicas, obtener_valores_etiqueta

app = Flask(__name__)
app.secret_key = "xml_modifier_pro_ultra_secret_key"

# Configuración de Base de Datos SQLite
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'xml_pro.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'storage')

# Inicialización de extensiones
db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- RUTAS DE AUTENTICACIÓN ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and check_password_hash(user.password_hash, request.form.get('password')):
            login_user(user)
            return redirect(url_for('index'))
        flash('Usuario o contraseña incorrectos', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password, method='pbkdf2:sha256')
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registro exitoso. Procede a iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- RUTAS PRINCIPALES ---

@app.route('/')
@login_required
def index():
    activities = XMLActivity.query.filter_by(user_id=current_user.id).order_by(XMLActivity.timestamp.desc()).all()
    return render_template('index.html', activities=activities)

@app.route('/api/parse', methods=['POST'])
@login_required
def parse_xml():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No select'}), 400
    
    # Generar un ID temporal para este análisis
    temp_id = f"{current_user.id}_{int(datetime.now().timestamp())}"
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp', f"{temp_id}.xml")
    file.save(temp_path)
    
    try:
        tags = sorted(list(obtener_etiquetas_unicas(temp_path)))
        return jsonify({'tags': tags, 'file_id': temp_id})
    except Exception as e:
        if os.path.exists(temp_path): os.remove(temp_path)
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_values', methods=['POST'])
@login_required
def get_values():
    data = request.json
    file_id = data.get('file_id')
    tag = data.get('tag')
    
    if not file_id or not tag:
        return jsonify({'error': 'Missing data'}), 400
        
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp', f"{file_id}.xml")
    
    if not os.path.exists(temp_path):
        return jsonify({'error': 'Session expired or file not found'}), 404
        
    try:
        values = sorted(list(obtener_valores_etiqueta(temp_path, tag)))
        # Añadimos la opción TODOS al inicio
        values.insert(0, "[TODOS]")
        return jsonify({'values': values})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preview_changes', methods=['POST'])
@login_required
def preview_changes():
    data = request.json
    file_id = data.get('file_id')
    tag = data.get('tag')
    old_val = data.get('old_val')
    new_val = data.get('new_val')
    use_regex = data.get('use_regex', False)
    
    if not all([file_id, tag, old_val, new_val]):
        return jsonify({'error': 'Missing data'}), 400
        
    temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp', f"{file_id}.xml")
    if not os.path.exists(temp_path):
        return jsonify({'error': 'Session expired or file not found'}), 404
        
    try:
        cambios = modificar_xml(temp_path, tag, old_val, new_val, preview=True, usar_regex=use_regex)
        return jsonify({'cambios': cambios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])

@login_required
def upload_process():
    if 'file' not in request.files:
        flash('No file')
        return redirect(url_for('index'))
    
    file = request.files['file']
    tag = request.form.get('etiqueta')
    old_val = request.form.get('valor_actual')
    new_val = request.form.get('valor_nuevo')
    use_regex = request.form.get('usar_regex') == 'on'
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    orig_path = os.path.join(app.config['UPLOAD_FOLDER'], 'originals', f"{timestamp}_{filename}")
    mod_path = os.path.join(app.config['UPLOAD_FOLDER'], 'modified', f"{timestamp}_{filename}")
    
    file.save(orig_path)
    # Crear una copia para modificar
    import shutil
    shutil.copy(orig_path, mod_path)
    
    try:
        cambios = modificar_xml(mod_path, tag, old_val, new_val, usar_regex=use_regex)
        
        if cambios > 0:
            # Guardar en base de datos
            activity = XMLActivity(
                user_id=current_user.id,
                original_filename=filename,
                modified_filename=f"mod_{filename}",
                storage_path=f"{timestamp}_{filename}",
                tag=tag,
                old_value=old_val,
                new_value=new_val
            )
            db.session.add(activity)
            db.session.commit()
            flash(f'Éxito: Se realizaron {cambios} cambios. Revisa tu historial.', 'success')
        else:
            flash('No se encontraron coincidencias.', 'info')
            if os.path.exists(mod_path): os.remove(mod_path)
            if os.path.exists(orig_path): os.remove(orig_path)
            
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        
    return redirect(url_for('index'))

@app.route('/download/<int:activity_id>')
@login_required
def download_file(activity_id):
    activity = XMLActivity.query.get_or_404(activity_id)
    if activity.user_id != current_user.id:
        return "Acceso denegado", 403
    
    path = os.path.join(app.config['UPLOAD_FOLDER'], 'modified', activity.storage_path)
    return send_file(path, as_attachment=True, download_name=f"modificado_{activity.original_filename}")

# Crear la base de datos al inicio
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5001)
