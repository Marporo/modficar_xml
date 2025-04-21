"""
Punto de entrada principal de la aplicación.
"""

import logging
from pathlib import Path
from src.ui.main_window import MainWindow

def setup_logging():
    """Configura el sistema de logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log", encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def main():
    """Función principal que inicia la aplicación."""
    setup_logging()
    logging.info("Iniciando aplicación...")
    
    app = MainWindow()
    app.run()

if __name__ == "__main__":
    main() 