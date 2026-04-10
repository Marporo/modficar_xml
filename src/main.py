import sys
import os

# Asegurar que el directorio 'src' esté en el path para las importaciones locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from ui.main_window import XMLModifierApp

def main():
    """Punto de entrada principal de la aplicación.
    
    Inicializa el ciclo de vida de la aplicación Qt, configura los 
    metadatos del sistema y lanza la ventana principal.
    """
    app = QApplication(sys.argv)
    
    # Configurar metadatos globales para el sistema operativo
    app.setApplicationName("XML Modifier Pro")
    app.setOrganizationName("XMLModifier")  # Nombre genérico para evitar referencias a terceros
    
    window = XMLModifierApp()
    window.show()
    
    # app.exec() inicia el event loop nativo
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
