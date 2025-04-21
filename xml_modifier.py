# xml_modifier.py - Contiene la lógica de negocio

import xml.etree.ElementTree as ET
import re
import logging
from typing import Optional, Union, List, Set

def modificar_xml(archivo_xml: str, 
                 etiqueta_buscar: str, 
                 valor_viejo: str, 
                 valor_nuevo: str,
                 preview: bool = False,
                 usar_regex: bool = False,
                 atributo: Optional[str] = None) -> int:
    """
    Modifica un archivo XML cambiando un valor específico en una etiqueta dada.
    
    Args:
        archivo_xml (str): Ruta al archivo XML
        etiqueta_buscar (str): Nombre de la etiqueta a buscar
        valor_viejo (str): Valor que se desea reemplazar
        valor_nuevo (str): Nuevo valor a colocar
        preview (bool): Si es True, solo muestra los cambios sin aplicarlos
        usar_regex (bool): Si es True, usa expresiones regulares para la búsqueda
        atributo (str, optional): Nombre del atributo a modificar. Si es None, modifica el texto
    
    Returns:
        int: Número de cambios realizados
    """
    try:
        # Parsear el archivo XML
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        
        # Contador de cambios realizados
        cambios = 0
        
        # Compilar el patrón regex si es necesario
        patron = re.compile(valor_viejo) if usar_regex else None
        
        # Buscar todas las instancias de la etiqueta especificada
        for elemento in root.findall(f".//{etiqueta_buscar}"):
            if atributo:
                # Modificar atributo
                valor_actual = elemento.get(atributo)
                if valor_actual is not None:
                    if usar_regex:
                        if patron.search(valor_actual):
                            if not preview:
                                elemento.set(atributo, patron.sub(valor_nuevo, valor_actual))
                            cambios += 1
                    else:
                        if valor_actual == valor_viejo:
                            if not preview:
                                elemento.set(atributo, valor_nuevo)
                            cambios += 1
            else:
                # Modificar texto
                if elemento.text:
                    if usar_regex:
                        if patron.search(elemento.text):
                            if not preview:
                                elemento.text = patron.sub(valor_nuevo, elemento.text)
                            cambios += 1
                    else:
                        if elemento.text == valor_viejo:
                            if not preview:
                                elemento.text = valor_nuevo
                            cambios += 1
        
        # Si se realizaron cambios y no es preview, guardar el archivo
        if cambios > 0 and not preview:
            tree.write(archivo_xml, encoding='utf-8', xml_declaration=True)
        
        return cambios
        
    except ET.ParseError as e:
        logging.error(f"Error al parsear el archivo XML {archivo_xml}: {str(e)}")
        raise ValueError(f"El archivo XML no es válido: {str(e)}")
    except Exception as e:
        logging.error(f"Error al modificar el archivo XML {archivo_xml}: {str(e)}")
        raise ValueError(f"Error al procesar el archivo: {str(e)}")

def validar_xml(archivo_xml: str) -> bool:
    """
    Valida si un archivo es un XML válido.
    
    Args:
        archivo_xml (str): Ruta al archivo XML
    
    Returns:
        bool: True si el archivo es válido, False en caso contrario
    """
    try:
        ET.parse(archivo_xml)
        return True
    except ET.ParseError:
        return False
    except Exception:
        return False

def obtener_etiquetas_unicas(archivo_xml: str) -> Set[str]:
    """
    Obtiene todas las etiquetas únicas presentes en un archivo XML.
    
    Args:
        archivo_xml (str): Ruta al archivo XML
    
    Returns:
        Set[str]: Conjunto de etiquetas únicas encontradas
    """
    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        
        etiquetas = set()
        
        def agregar_etiquetas(elemento):
            etiquetas.add(elemento.tag)
            for hijo in elemento:
                agregar_etiquetas(hijo)
        
        agregar_etiquetas(root)
        return etiquetas
        
    except ET.ParseError as e:
        logging.error(f"Error al parsear el archivo XML {archivo_xml}: {str(e)}")
        raise ValueError(f"El archivo XML no es válido: {str(e)}")
    except Exception as e:
        logging.error(f"Error al obtener etiquetas del archivo XML {archivo_xml}: {str(e)}")
        raise ValueError(f"Error al procesar el archivo: {str(e)}")

def obtener_valores_etiqueta(archivo_xml: str, etiqueta: str) -> Set[str]:
    """
    Obtiene todos los valores únicos de una etiqueta específica en un archivo XML.
    
    Args:
        archivo_xml (str): Ruta al archivo XML
        etiqueta (str): Nombre de la etiqueta a buscar
    
    Returns:
        Set[str]: Conjunto de valores únicos encontrados
    """
    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        
        valores = set()
        
        # Buscar todas las instancias de la etiqueta
        for elemento in root.findall(f".//{etiqueta}"):
            if elemento.text:
                valores.add(elemento.text.strip())
        
        return valores
        
    except ET.ParseError as e:
        logging.error(f"Error al parsear el archivo XML {archivo_xml}: {str(e)}")
        raise ValueError(f"El archivo XML no es válido: {str(e)}")
    except Exception as e:
        logging.error(f"Error al obtener valores de la etiqueta {etiqueta}: {str(e)}")
        raise ValueError(f"Error al procesar el archivo: {str(e)}")