# src/ui/styles.py - Estilos modernos para macOS
import os

def get_main_style(resources_dir):
    """Genera el motor de estilos CSS (QSS) para la aplicación.
    
    Esta función construye una hoja de estilos dinámica que inyecta las rutas 
    absolutas de los iconos SVG. Utiliza una paleta de colores basada en 
    las guías de diseño de Apple (Apple Design Language) para lograr 
    una apariencia nativa y premium.

    Args:
        resources_dir: Directorio absoluto donde se encuentran los archivos .svg.

    Returns:
        str: Cadena de texto formateada con todo el CSS compatible con Qt.
    """
    # Normalización de rutas para asegurar compatibilidad con Windows y macOS en Qt
    chevron = os.path.join(resources_dir, 'chevron_down.svg').replace('\\', '/')
    checkmark = os.path.join(resources_dir, 'check_white.svg').replace('\\', '/')
    
    return f"""
QMainWindow {{
    background-color: #F5F5F7;
}}

QWidget {{
    font-family: 'Helvetica Neue', 'Helvetica', 'Arial';
    font-size: 13px;
    color: #1D1D1F;
}}

QTabWidget::pane {{
    border: none;
    background: white;
    border-radius: 12px;
}}

QTabBar::tab {{
    background: transparent;
    padding: 8px 16px;
    margin-right: 4px;
    color: #86868B;
    font-weight: 500;
}}

QTabBar::tab:selected {{
    color: #0071E3;
    border-bottom: 2px solid #0071E3;
}}

QPushButton {{
    background-color: #F5F5F7;
    border: 1px solid #D2D2D7;
    border-radius: 8px;
    padding: 8px 16px;
    font-weight: 500;
}}

QPushButton:hover {{
    background-color: #E8E8ED;
}}

QPushButton#AccentButton {{
    background-color: #0071E3;
    color: white;
    border: none;
}}

QPushButton#AccentButton:hover {{
    background-color: #0077ED;
}}

/* Inputs */
QLineEdit {{
    background-color: white;
    border: 1px solid #D2D2D7;
    border-radius: 8px;
    padding: 8px 12px;
    selection-background-color: #0071E3;
}}

QLineEdit:focus {{
    border: 1px solid #0071E3;
}}

/* ComboBox */
QComboBox {{
    background-color: white;
    border: 1px solid #D2D2D7;
    border-radius: 8px;
    padding: 8px 12px;
    padding-right: 30px;
    selection-background-color: #0071E3;
}}

QComboBox:focus {{
    border: 1px solid #0071E3;
}}

QComboBox::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 30px;
    border: none;
}}

QComboBox::down-arrow {{
    image: url({chevron});
    width: 12px;
    height: 12px;
}}

/* Lista desplegable del ComboBox */
QComboBox QAbstractItemView {{
    background-color: white;
    color: #1D1D1F;
    border: 1px solid #D2D2D7;
    border-radius: 6px;
    selection-background-color: #0071E3;
    selection-color: white;
    outline: none;
    padding: 4px;
}}

QComboBox QAbstractItemView::item {{
    padding: 6px 12px;
    min-height: 26px;
}}

QComboBox QAbstractItemView::item:hover {{
    background-color: #E8E8ED;
    color: #1D1D1F;
}}

/* Checkbox con checkmark visible */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid #D2D2D7;
    border-radius: 4px;
    background-color: white;
}}

QCheckBox::indicator:hover {{
    border: 1.5px solid #0071E3;
}}

QCheckBox::indicator:checked {{
    background-color: #0071E3;
    border: 1.5px solid #0071E3;
    image: url({checkmark});
}}

/* Cuadros de Diálogo */
QMessageBox {{
    background-color: white;
}}

QMessageBox QLabel {{
    color: #1D1D1F;
    font-size: 13px;
}}

QMessageBox QPushButton {{
    min-width: 80px;
    background-color: #0071E3;
    color: white;
}}

/* Botón de Ayuda Circular */
QPushButton#HelpButton {{
    background-color: rgba(0, 113, 227, 0.1);
    color: #0071E3;
    border: 1px solid rgba(0, 113, 227, 0.2);
    border-radius: 10px;
    width: 20px;
    height: 20px;
    min-width: 20px;
    max-width: 20px;
    padding: 0px;
    font-weight: bold;
    font-size: 12px;
}}

QPushButton#HelpButton:hover {{
    background-color: rgba(0, 113, 227, 0.2);
}}

QLabel#Title {{
    font-size: 24px;
    font-weight: 700;
    color: #1D1D1F;
    letter-spacing: -0.5px;
}}

/* Tabla de Historial con grid visible */
QTableWidget {{
    border: 1px solid #D2D2D7;
    background-color: white;
    alternate-background-color: #FAFAFA;
}}

QTableWidget::item {{
    border-bottom: 1px solid #E0E0E0;
    border-right: 1px solid #E0E0E0;
    padding: 8px;
}}

QHeaderView::section {{
    background-color: #F5F5F7;
    padding: 10px 8px;
    border: none;
    border-right: 1px solid #D2D2D7;
    border-bottom: 1px solid #D2D2D7;
    font-weight: 600;
    color: #86868B;
    text-transform: uppercase;
    font-size: 11px;
}}

/* Panel de Vista Previa */
QTextEdit#PreviewPanel {{
    background-color: #FAFAFA;
    border: 1px solid #D2D2D7;
    border-radius: 8px;
    padding: 12px;
    color: #1D1D1F;
    font-size: 12px;
}}

/* Guía de Uso */
QTextEdit#GuideText {{
    background-color: white;
    border: 1px solid #D2D2D7;
    border-radius: 12px;
    padding: 20px;
    selection-background-color: #0071E3;
}}

QProgressBar {{
    border: none;
    background-color: #E8E8ED;
    border-radius: 4px;
    text-align: center;
    color: transparent;
}}

QProgressBar::chunk {{
    background-color: #34C759;
    border-radius: 4px;
}}

QGroupBox {{
    font-weight: 600;
    border: 1px solid #D2D2D7;
    border-radius: 12px;
    margin-top: 20px;
    padding-top: 15px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 15px;
    padding: 0 5px;
}}
"""
