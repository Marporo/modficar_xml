"""
Módulo para procesar y modificar archivos XML.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple
from xml.etree import ElementTree as ET

class XMLProcessor:
    """Procesador de archivos XML."""
    
    @staticmethod
    def modify_xml(
        file_path: str,
        tag: str,
        old_value: str,
        new_value: str,
        use_regex: bool = False,
        preview: bool = False
    ) -> Tuple[bool, List[str], Optional[str]]:
        """
        Modifica un archivo XML.
        
        Args:
            file_path: Ruta al archivo XML.
            tag: Etiqueta a buscar.
            old_value: Valor actual a reemplazar.
            new_value: Nuevo valor.
            use_regex: Si se usa expresión regular.
            preview: Si es solo vista previa.
            
        Returns:
            Tupla con:
            - bool: Si se realizaron cambios
            - List[str]: Lista de cambios realizados
            - Optional[str]: Error si ocurrió alguno
        """
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            changes = []
            modified = False
            
            for elem in root.findall(f".//{tag}"):
                current_value = elem.text or ""
                if use_regex:
                    if re.search(old_value, current_value):
                        new_text = re.sub(old_value, new_value, current_value)
                        changes.append(f"'{current_value}' -> '{new_text}'")
                        if not preview:
                            elem.text = new_text
                            modified = True
                else:
                    if current_value == old_value:
                        changes.append(f"'{current_value}' -> '{new_value}'")
                        if not preview:
                            elem.text = new_value
                            modified = True
            
            if modified:
                tree.write(file_path, encoding="utf-8", xml_declaration=True)
                logging.info(f"Archivo {file_path} modificado correctamente")
                
            return modified, changes, None
            
        except Exception as e:
            error_msg = f"Error al procesar {file_path}: {str(e)}"
            logging.error(error_msg)
            return False, [], error_msg
    
    @staticmethod
    def get_xml_files(directory: str) -> List[str]:
        """
        Obtiene la lista de archivos XML en un directorio.
        
        Args:
            directory: Ruta al directorio.
            
        Returns:
            Lista de rutas a archivos XML.
        """
        try:
            path = Path(directory)
            if not path.exists():
                logging.error(f"El directorio {directory} no existe")
                return []
                
            xml_files = list(path.glob("**/*.xml"))
            logging.info(f"Encontrados {len(xml_files)} archivos XML en {directory}")
            return [str(f) for f in xml_files]
            
        except Exception as e:
            logging.error(f"Error al buscar archivos XML: {e}")
            return []
            
    @staticmethod
    def validate_xml(file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Valida si un archivo XML está bien formado.
        
        Args:
            file_path: Ruta al archivo XML.
            
        Returns:
            Tupla con:
            - bool: Si el archivo es válido
            - Optional[str]: Mensaje de error si no es válido
        """
        try:
            ET.parse(file_path)
            return True, None
        except Exception as e:
            error_msg = f"XML inválido: {str(e)}"
            logging.error(f"{error_msg} en {file_path}")
            return False, error_msg 