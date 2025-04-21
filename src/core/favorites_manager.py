"""
Módulo para gestionar operaciones favoritas.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

class FavoritesManager:
    """Administrador de operaciones favoritas."""
    
    def __init__(self, favorites_file: str = "favorites.json"):
        """
        Inicializa el administrador de favoritos.
        
        Args:
            favorites_file: Ruta al archivo de favoritos.
        """
        self.favorites_file = Path(favorites_file)
        self.favorites: List[Dict] = []
        self.load_favorites()
        
    def load_favorites(self) -> None:
        """Carga los favoritos desde el archivo."""
        try:
            if self.favorites_file.exists():
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    self.favorites = json.load(f)
                logging.info(f"Favoritos cargados: {len(self.favorites)} entradas")
            else:
                self.favorites = []
                logging.info("Archivo de favoritos no encontrado, se creará uno nuevo")
        except Exception as e:
            logging.error(f"Error al cargar favoritos: {e}")
            self.favorites = []
            
    def save_favorites(self) -> None:
        """Guarda los favoritos en el archivo."""
        try:
            with open(self.favorites_file, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
            logging.info("Favoritos guardados correctamente")
        except Exception as e:
            logging.error(f"Error al guardar favoritos: {e}")
            
    def add_favorite(
        self,
        name: str,
        operation: str,
        tag: str,
        old_value: str,
        new_value: str,
        use_regex: bool = False,
        description: Optional[str] = None
    ) -> bool:
        """
        Agrega una operación a favoritos.
        
        Args:
            name: Nombre identificador del favorito.
            operation: Tipo de operación.
            tag: Etiqueta a modificar.
            old_value: Valor a buscar.
            new_value: Valor de reemplazo.
            use_regex: Si usa expresiones regulares.
            description: Descripción opcional.
            
        Returns:
            True si se agregó correctamente, False si ya existe.
        """
        if any(f["name"] == name for f in self.favorites):
            logging.warning(f"Ya existe un favorito con el nombre: {name}")
            return False
            
        favorite = {
            "name": name,
            "operation": operation,
            "tag": tag,
            "old_value": old_value,
            "new_value": new_value,
            "use_regex": use_regex
        }
        
        if description:
            favorite["description"] = description
            
        self.favorites.append(favorite)
        self.save_favorites()
        logging.info(f"Nuevo favorito agregado: {name}")
        return True
        
    def get_favorite(self, name: str) -> Optional[Dict]:
        """
        Obtiene un favorito por su nombre.
        
        Args:
            name: Nombre del favorito.
            
        Returns:
            Diccionario con los datos del favorito o None si no existe.
        """
        for favorite in self.favorites:
            if favorite["name"] == name:
                return favorite
        return None
        
    def update_favorite(
        self,
        name: str,
        operation: Optional[str] = None,
        tag: Optional[str] = None,
        old_value: Optional[str] = None,
        new_value: Optional[str] = None,
        use_regex: Optional[bool] = None,
        description: Optional[str] = None
    ) -> bool:
        """
        Actualiza un favorito existente.
        
        Args:
            name: Nombre del favorito a actualizar.
            operation: Nuevo tipo de operación.
            tag: Nueva etiqueta.
            old_value: Nuevo valor a buscar.
            new_value: Nuevo valor de reemplazo.
            use_regex: Nuevo estado de uso de regex.
            description: Nueva descripción.
            
        Returns:
            True si se actualizó correctamente, False si no existe.
        """
        for favorite in self.favorites:
            if favorite["name"] == name:
                if operation is not None:
                    favorite["operation"] = operation
                if tag is not None:
                    favorite["tag"] = tag
                if old_value is not None:
                    favorite["old_value"] = old_value
                if new_value is not None:
                    favorite["new_value"] = new_value
                if use_regex is not None:
                    favorite["use_regex"] = use_regex
                if description is not None:
                    favorite["description"] = description
                elif "description" in favorite:
                    del favorite["description"]
                    
                self.save_favorites()
                logging.info(f"Favorito actualizado: {name}")
                return True
                
        logging.warning(f"No se encontró el favorito: {name}")
        return False
        
    def delete_favorite(self, name: str) -> bool:
        """
        Elimina un favorito.
        
        Args:
            name: Nombre del favorito a eliminar.
            
        Returns:
            True si se eliminó correctamente, False si no existe.
        """
        for i, favorite in enumerate(self.favorites):
            if favorite["name"] == name:
                self.favorites.pop(i)
                self.save_favorites()
                logging.info(f"Favorito eliminado: {name}")
                return True
                
        logging.warning(f"No se encontró el favorito: {name}")
        return False
        
    def get_all_favorites(self) -> List[Dict]:
        """
        Obtiene todos los favoritos.
        
        Returns:
            Lista de favoritos ordenada por nombre.
        """
        return sorted(self.favorites, key=lambda x: x["name"]) 