"""
Módulo para gestionar el historial de operaciones.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class HistoryManager:
    """Administrador del historial de operaciones."""
    
    def __init__(self, history_file: str = "history.json"):
        """
        Inicializa el administrador de historial.
        
        Args:
            history_file: Ruta al archivo de historial.
        """
        self.history_file = Path(history_file)
        self.history: List[Dict] = []
        self.load_history()
        
    def load_history(self) -> None:
        """Carga el historial desde el archivo."""
        try:
            if self.history_file.exists():
                with open(self.history_file, "r", encoding="utf-8") as f:
                    self.history = json.load(f)
                logging.info(f"Historial cargado: {len(self.history)} entradas")
            else:
                self.history = []
                logging.info("Archivo de historial no encontrado, se creará uno nuevo")
        except Exception as e:
            logging.error(f"Error al cargar historial: {e}")
            self.history = []
            
    def save_history(self) -> None:
        """Guarda el historial en el archivo."""
        try:
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            logging.info("Historial guardado correctamente")
        except Exception as e:
            logging.error(f"Error al guardar historial: {e}")
            
    def add_entry(
        self,
        operation: str,
        files: List[str],
        tag: str,
        old_value: str,
        new_value: str,
        changes: List[str],
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """
        Agrega una entrada al historial.
        
        Args:
            operation: Tipo de operación realizada.
            files: Lista de archivos procesados.
            tag: Etiqueta modificada.
            old_value: Valor anterior.
            new_value: Nuevo valor.
            changes: Lista de cambios realizados.
            success: Si la operación fue exitosa.
            error: Mensaje de error si hubo alguno.
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "files": files,
            "tag": tag,
            "old_value": old_value,
            "new_value": new_value,
            "changes": changes,
            "success": success
        }
        
        if error:
            entry["error"] = error
            
        self.history.append(entry)
        self.save_history()
        logging.info("Nueva entrada agregada al historial")
        
    def get_entries(
        self,
        limit: Optional[int] = None,
        success_only: bool = False
    ) -> List[Dict]:
        """
        Obtiene entradas del historial.
        
        Args:
            limit: Número máximo de entradas a retornar.
            success_only: Si solo se retornan operaciones exitosas.
            
        Returns:
            Lista de entradas del historial.
        """
        entries = [e for e in self.history if not success_only or e["success"]]
        entries.reverse()  # Más recientes primero
        
        if limit:
            entries = entries[:limit]
            
        return entries
        
    def clear_history(self) -> None:
        """Limpia el historial."""
        self.history = []
        self.save_history()
        logging.info("Historial limpiado") 