"""
models.py - Definición del Esquema de Datos (Persistence Layer)

Contiene las clases del ORM SQLAlchemy que representan las tablas en la 
base de datos relacional de la plataforma.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """
    Representa un usuario autenticado del sistema.
    Gestiona la identidad para el sistema de control de accesos (Flask-Login).
    """
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    activities = db.relationship('XMLActivity', backref='owner', lazy=True)

class XMLActivity(db.Model):
    """
    Registro histórico de operaciones realizadas por los usuarios.
    Mantiene la trazabilidad de los archivos procesados y sus modificaciones.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    modified_filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(512), nullable=False)
    tag = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.String(255), nullable=False)
    new_value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
