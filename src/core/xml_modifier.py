# xml_modifier.py - Motor de procesamiento XML con soporte para Regex y procesamiento masivo.

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
    """Modifica valores de etiquetas o atributos en un archivo XML.

    Esta función es el núcleo del sistema. Permite buscar coincidencias exactas 
    o mediante expresiones regulares (Regex). También soporta la instrucción 
    especial '[TODOS]' para sobreescritura masiva.

    Args:
        archivo_xml: Ruta absoluta al archivo XML a procesar.
        etiqueta_buscar: Nombre del tag XML (ej: 'Reference').
        valor_viejo: Valor actual a buscar. Si es '[TODOS]', reemplaza todo.
        valor_nuevo: El nuevo texto o valor a insertar.
        preview: Si es True, cuenta los cambios pero no guarda el archivo en disco.
        usar_regex: Indica si 'valor_viejo' debe tratarse como un patrón Regex.
        atributo: Nombre del atributo si se desea modificar un property (ej: 'id').
            Si es None, se modifica el contenido de texto de la etiqueta.

    Returns:
        Número total de coincidencias encontradas y/o modificadas.

    Raises:
        ValueError: Si el archivo está corrupto o no es un XML válido.
    """
    try:
        # Parsear el archivo XML usando la librería nativa de Python
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        
        cambios = 0
        patron = re.compile(valor_viejo) if usar_regex else None
        
        # Búsqueda recursiva: .// busca en cualquier nivel de profundidad
        for elemento in root.findall(f".//{etiqueta_buscar}"):
            if atributo:
                # Lógica para modificación de ATRIBUTO
                valor_actual = elemento.get(atributo)
                if valor_actual is not None:
                    # Caso 1: Sobreescritura total
                    if valor_viejo == "[TODOS]":
                        if not preview:
                            elemento.set(atributo, valor_nuevo)
                        cambios += 1
                    # Caso 2: Expresiones Regulares
                    elif usar_regex:
                        if patron.search(valor_actual):
                            if not preview:
                                elemento.set(atributo, patron.sub(valor_nuevo, valor_actual))
                            cambios += 1
                    # Caso 3: Coincidencia exacta
                    else:
                        if valor_actual == valor_viejo:
                            if not preview:
                                elemento.set(atributo, valor_nuevo)
                            cambios += 1
            else:
                # Lógica para modificación de TEXTO (Tag Content)
                if elemento.text:
                    v_act = elemento.text.strip()
                    # Caso 1: Sobreescritura total
                    if valor_viejo == "[TODOS]":
                        if not preview:
                            elemento.text = valor_nuevo
                        cambios += 1
                    # Caso 2: Expresiones Regulares
                    elif usar_regex:
                        if patron.search(elemento.text):
                            if not preview:
                                # sub() de re maneja los grupos de captura si los hay
                                elemento.text = patron.sub(valor_nuevo, elemento.text)
                            cambios += 1
                    # Caso 3: Coincidencia exacta
                    else:
                        if elemento.text == valor_viejo:
                            if not preview:
                                elemento.text = valor_nuevo
                            cambios += 1
        
        # Solo escribir en disco si hubo cambios y no es modo Vista Previa
        if cambios > 0 and not preview:
            # Se especifica encoding utf-8 y declaración XML para compatibilidad total
            tree.write(archivo_xml, encoding='utf-8', xml_declaration=True)
        
        return cambios
        
    except ET.ParseError as e:
        logging.error(f"Error de parseo en {archivo_xml}: {str(e)}")
        raise ValueError(f"XML inválido: {str(e)}")
    except Exception as e:
        logging.error(f"Error crítico en {archivo_xml}: {str(e)}")
        raise ValueError(f"Error de procesamiento: {str(e)}")

def validar_xml(archivo_xml: str) -> bool:
    """Verifica si un archivo tiene una estructura XML válida.

    Args:
        archivo_xml: Ruta al archivo a validar.

    Returns:
        True si el parser logra leer el archivo sin errores catastróficos.
    """
    try:
        ET.parse(archivo_xml)
        return True
    except (ET.ParseError, Exception):
        return False

def obtener_etiquetas_unicas(archivo_xml: str) -> Set[str]:
    """Escanea el archivo XML para extraer todos los nombres de etiquetas.

    Útil para el llenado dinámico de dropdowns en la interfaz de usuario.

    Args:
        archivo_xml: Ruta al archivo XML.

    Returns:
        Un conjunto (Set) con los nombres de las etiquetas sin duplicados.
    """
    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        etiquetas = set()
        
        # Función interna recursiva para recorrer todo el árbol
        def agregar_etiquetas(elemento):
            etiquetas.add(elemento.tag)
            for hijo in elemento:
                agregar_etiquetas(hijo)
        
        agregar_etiquetas(root)
        return etiquetas
    except Exception as e:
        raise ValueError(f"No se pudieron extraer etiquetas: {str(e)}")

def obtener_valores_etiqueta(archivo_xml: str, etiqueta: str) -> Set[str]:
    """Extrae todos los valores de texto presentes en una etiqueta específica.

    Args:
        archivo_xml: Ruta al archivo XML.
        etiqueta: Nombre del tag a inspeccionar.

    Returns:
        Un conjunto con todos los valores de texto únicos encontrados.
    """
    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        valores = set()
        
        # Buscamos en todo el árbol elementos que coincidan con el tag
        for elemento in root.findall(f".//{etiqueta}"):
            if elemento.text:
                val = elemento.text.strip()
                if val:
                    valores.add(val)
        
        return valores
    except Exception as e:
        raise ValueError(f"Error al extraer valores de <{etiqueta}>: {str(e)}")