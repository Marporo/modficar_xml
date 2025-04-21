# xml_modifier.py - Contiene la lógica de negocio

import xml.etree.ElementTree as ET

def modificar_xml(archivo_xml, etiqueta_buscar, valor_viejo, valor_nuevo):
    """
    Modifica un archivo XML cambiando un valor específico en una etiqueta dada.
    
    Args:
        archivo_xml (str): Ruta al archivo XML
        etiqueta_buscar (str): Nombre de la etiqueta a buscar
        valor_viejo (str): Valor que se desea reemplazar
        valor_nuevo (str): Nuevo valor a colocar
    
    Returns:
        int: Número de cambios realizados
    """
    try:
        # Parsear el archivo XML
        tree = ET.parse(archivo_xml)
        root = tree.getroot()
        
        # Contador de cambios realizados
        cambios = 0
        
        # Buscar todas las instancias de la etiqueta especificada
        for elemento in root.findall(f".//{etiqueta_buscar}"):
            if elemento.text == valor_viejo:
                elemento.text = valor_nuevo
                cambios += 1
        
        # Si se realizaron cambios, guardar el archivo
        if cambios > 0:
            tree.write(archivo_xml)
            return cambios
        else:
            return 0
    except Exception as e:
        raise e