"""
Módulo para gestionar la configuración de la aplicación.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

class ConfigManager:
    """Administrador de configuración de la aplicación."""
    
    DEFAULT_CONFIG = {
        "theme": "light",
        "language": "es",
        "default_directory": "",
        "use_regex_default": False,
        "auto_backup": True,
        "backup_directory": "backups",
        "max_history": 100,
        "show_preview_default": True,
        "window_size": {
            "width": 800,
            "height": 600
        },
        "recent_directories": [],
        "recent_files": []
    }
    
    def __init__(self, config_file: str = "config.json"):
        """
        Inicializa el administrador de configuración.
        
        Args:
            config_file: Ruta al archivo de configuración.
        """
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load_config()
        
    def load_config(self) -> None:
        """Carga la configuración desde el archivo."""
        try:
            if self.config_file.exists():
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Combinar con la configuración por defecto para asegurar todos los campos
                    self.config = {**self.DEFAULT_CONFIG, **loaded_config}
                logging.info("Configuración cargada correctamente")
            else:
                self.config = self.DEFAULT_CONFIG.copy()
                self.save_config()
                logging.info("Creada nueva configuración con valores por defecto")
        except Exception as e:
            logging.error(f"Error al cargar la configuración: {e}")
            self.config = self.DEFAULT_CONFIG.copy()
            
    def save_config(self) -> None:
        """Guarda la configuración en el archivo."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            logging.info("Configuración guardada correctamente")
        except Exception as e:
            logging.error(f"Error al guardar la configuración: {e}")
            
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de la configuración.
        
        Args:
            key: Clave del valor a obtener.
            default: Valor por defecto si no existe la clave.
            
        Returns:
            Valor de la configuración o el valor por defecto.
        """
        return self.config.get(key, default)
        
    def set_value(self, key: str, value: Any) -> None:
        """
        Establece un valor en la configuración.
        
        Args:
            key: Clave del valor a establecer.
            value: Nuevo valor.
        """
        self.config[key] = value
        self.save_config()
        logging.info(f"Actualizado valor de configuración: {key}")
        
    def add_recent_directory(self, directory: str, max_items: int = 10) -> None:
        """
        Agrega un directorio a la lista de recientes.
        
        Args:
            directory: Ruta del directorio.
            max_items: Número máximo de elementos a mantener.
        """
        recent = self.config["recent_directories"]
        if directory in recent:
            recent.remove(directory)
        recent.insert(0, directory)
        self.config["recent_directories"] = recent[:max_items]
        self.save_config()
        
    def add_recent_file(self, file_path: str, max_items: int = 10) -> None:
        """
        Agrega un archivo a la lista de recientes.
        
        Args:
            file_path: Ruta del archivo.
            max_items: Número máximo de elementos a mantener.
        """
        recent = self.config["recent_files"]
        if file_path in recent:
            recent.remove(file_path)
        recent.insert(0, file_path)
        self.config["recent_files"] = recent[:max_items]
        self.save_config()
        
    def clear_recent_items(self, item_type: str = "all") -> None:
        """
        Limpia las listas de elementos recientes.
        
        Args:
            item_type: Tipo de elementos a limpiar ("all", "directories" o "files").
        """
        if item_type in ["all", "directories"]:
            self.config["recent_directories"] = []
        if item_type in ["all", "files"]:
            self.config["recent_files"] = []
        self.save_config()
        logging.info(f"Limpiada lista de recientes: {item_type}")
        
    def reset_to_defaults(self) -> None:
        """Restablece la configuración a los valores por defecto."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        logging.info("Configuración restablecida a valores por defecto")
        
    def update_window_size(self, width: int, height: int) -> None:
        """
        Actualiza el tamaño de la ventana.
        
        Args:
            width: Ancho de la ventana.
            height: Alto de la ventana.
        """
        self.config["window_size"] = {"width": width, "height": height}
        self.save_config()
        
    def get_window_size(self) -> Dict[str, int]:
        """
        Obtiene el tamaño de la ventana.
        
        Returns:
            Diccionario con el ancho y alto de la ventana.
        """
        return self.config["window_size"] 