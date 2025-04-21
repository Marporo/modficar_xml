"""
Módulo que define la clase base para todas las ventanas de la aplicación.
"""

import tkinter as tk
from tkinter import ttk
import logging
from typing import Optional, Tuple

class BaseWindow:
    """Clase base para todas las ventanas de la aplicación."""
    
    def __init__(self, parent: Optional[tk.Tk] = None, title: str = ""):
        """
        Inicializa una ventana base.
        
        Args:
            parent: Ventana padre (None si es la principal)
            title: Título de la ventana
        """
        self.parent = parent
        if parent is None:
            self.window = tk.Tk()
        else:
            self.window = tk.Toplevel(parent)
        
        self.window.title(title)
        self._configure_window()
        self._create_widgets()
        
    def _configure_window(self) -> None:
        """Configura las propiedades básicas de la ventana."""
        self.window.resizable(True, True)
        self._center_window()
        
    def _center_window(self, size: Optional[Tuple[int, int]] = None) -> None:
        """
        Centra la ventana en la pantalla.
        
        Args:
            size: Tupla opcional con (ancho, alto) de la ventana
        """
        if size is None:
            size = (800, 600)
            
        width, height = size
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
        
    def _create_widgets(self) -> None:
        """
        Crea los widgets de la ventana.
        Debe ser implementado por las clases hijas.
        """
        raise NotImplementedError
        
    def create_labeled_entry(
        self,
        parent: tk.Widget,
        text: str,
        row: int,
        column: int,
        width: int = 20
    ) -> ttk.Entry:
        """
        Crea un campo de entrada con etiqueta.
        
        Args:
            parent: Widget contenedor
            text: Texto de la etiqueta
            row: Fila en el grid
            column: Columna en el grid
            width: Ancho del campo de entrada
            
        Returns:
            El widget Entry creado
        """
        ttk.Label(parent, text=text).grid(
            row=row,
            column=column,
            sticky="e",
            padx=5,
            pady=2
        )
        
        entry = ttk.Entry(parent, width=width)
        entry.grid(
            row=row,
            column=column + 1,
            sticky="ew",
            padx=5,
            pady=2
        )
        return entry
        
    def create_button(
        self,
        parent: tk.Widget,
        text: str,
        command,
        row: int,
        column: int,
        columnspan: int = 1,
        style: str = "Secondary.TButton"
    ) -> ttk.Button:
        """
        Crea un botón estilizado.
        
        Args:
            parent: Widget contenedor
            text: Texto del botón
            command: Función a ejecutar
            row: Fila en el grid
            column: Columna en el grid
            columnspan: Número de columnas que ocupa
            style: Estilo del botón
            
        Returns:
            El botón creado
        """
        button = ttk.Button(
            parent,
            text=text,
            command=command,
            style=style
        )
        button.grid(
            row=row,
            column=column,
            columnspan=columnspan,
            sticky="ew",
            padx=5,
            pady=5
        )
        return button
        
    def show_error(self, message: str) -> None:
        """
        Muestra un mensaje de error.
        
        Args:
            message: Mensaje a mostrar
        """
        logging.error(message)
        tk.messagebox.showerror("Error", message)
        
    def show_info(self, message: str) -> None:
        """
        Muestra un mensaje informativo.
        
        Args:
            message: Mensaje a mostrar
        """
        logging.info(message)
        tk.messagebox.showinfo("Información", message)
        
    def run(self) -> None:
        """Inicia el loop principal de la ventana."""
        self.window.mainloop() 