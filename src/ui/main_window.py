"""
Módulo que define la ventana principal de la aplicación.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import logging
from typing import List, Optional
from pathlib import Path

from .base_window import BaseWindow
from ..core.config_manager import ConfigManager
from ..core.xml_modifier import XMLModifier

class MainWindow(BaseWindow):
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__(title="Modificador XML")
        self.config_manager = ConfigManager()
        self.xml_modifier = XMLModifier()
        
    def _create_widgets(self) -> None:
        """Crea los widgets de la ventana principal."""
        self._create_notebook()
        self._create_main_tab()
        self._create_history_tab()
        self._create_favorites_tab()
        self._create_settings_tab()
        
    def _create_notebook(self) -> None:
        """Crea el notebook con las pestañas."""
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Crear frames para cada pestaña
        self.main_frame = ttk.Frame(self.notebook)
        self.history_frame = ttk.Frame(self.notebook)
        self.favorites_frame = ttk.Frame(self.notebook)
        self.settings_frame = ttk.Frame(self.notebook)
        
        # Agregar pestañas
        self.notebook.add(self.main_frame, text="Modificar XML")
        self.notebook.add(self.history_frame, text="Historial")
        self.notebook.add(self.favorites_frame, text="Favoritos")
        self.notebook.add(self.settings_frame, text="Configuración")
        
    def _create_main_tab(self) -> None:
        """Crea el contenido de la pestaña principal."""
        # Frame para modo de operación
        mode_frame = ttk.LabelFrame(self.main_frame, text="Modo de operación")
        mode_frame.pack(fill="x", padx=5, pady=5)
        
        self.mode_var = tk.StringVar(value="single")
        ttk.Radiobutton(
            mode_frame,
            text="Archivo único",
            variable=self.mode_var,
            value="single",
            command=self._on_mode_change
        ).pack(side="left", padx=5)
        
        ttk.Radiobutton(
            mode_frame,
            text="Múltiples archivos",
            variable=self.mode_var,
            value="multiple",
            command=self._on_mode_change
        ).pack(side="left", padx=5)
        
        # Frame para selección de archivos
        file_frame = ttk.LabelFrame(self.main_frame, text="Selección de archivos")
        file_frame.pack(fill="x", padx=5, pady=5)
        
        self.file_entry = self.create_labeled_entry(
            file_frame,
            "Archivo XML:",
            0, 0, width=40
        )
        
        self.browse_button = self.create_button(
            file_frame,
            "Buscar",
            self._browse_file,
            0, 2
        )
        
        # Frame para modificación
        mod_frame = ttk.LabelFrame(self.main_frame, text="Modificación")
        mod_frame.pack(fill="x", padx=5, pady=5)
        
        self.tag_entry = self.create_labeled_entry(
            mod_frame,
            "Etiqueta:",
            0, 0
        )
        
        self.attr_entry = self.create_labeled_entry(
            mod_frame,
            "Atributo:",
            1, 0
        )
        
        self.old_value_entry = self.create_labeled_entry(
            mod_frame,
            "Valor actual:",
            2, 0
        )
        
        self.new_value_entry = self.create_labeled_entry(
            mod_frame,
            "Valor nuevo:",
            3, 0
        )
        
        # Frame para opciones
        options_frame = ttk.Frame(mod_frame)
        options_frame.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)
        
        self.regex_var = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="Usar expresiones regulares",
            variable=self.regex_var
        ).pack(side="left", padx=5)
        
        # Frame para botones
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        self.preview_button = self.create_button(
            button_frame,
            "Vista previa",
            self._preview_changes,
            0, 0
        )
        
        self.execute_button = self.create_button(
            button_frame,
            "Ejecutar",
            self._execute_changes,
            0, 1,
            style="Accent.TButton"
        )
        
        # Barra de progreso
        self.progress = ttk.Progressbar(
            self.main_frame,
            mode="determinate"
        )
        self.progress.pack(fill="x", padx=5, pady=5)
        
        # Área de resultados
        results_frame = ttk.LabelFrame(self.main_frame, text="Resultados")
        results_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.results_text = tk.Text(
            results_frame,
            height=10,
            wrap="word"
        )
        self.results_text.pack(fill="both", expand=True, padx=5, pady=5)
        
    def _create_history_tab(self) -> None:
        """Crea el contenido de la pestaña de historial."""
        # TODO: Implementar historial
        pass
        
    def _create_favorites_tab(self) -> None:
        """Crea el contenido de la pestaña de favoritos."""
        # TODO: Implementar favoritos
        pass
        
    def _create_settings_tab(self) -> None:
        """Crea el contenido de la pestaña de configuración."""
        # TODO: Implementar configuración
        pass
        
    def _on_mode_change(self) -> None:
        """Maneja el cambio de modo de operación."""
        is_single = self.mode_var.get() == "single"
        self.browse_button.configure(
            text="Buscar archivo" if is_single else "Buscar directorio"
        )
        
    def _browse_file(self) -> None:
        """Abre el diálogo para seleccionar archivo o directorio."""
        if self.mode_var.get() == "single":
            path = filedialog.askopenfilename(
                filetypes=[("Archivos XML", "*.xml")]
            )
        else:
            path = filedialog.askdirectory()
            
        if path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)
            
    def _preview_changes(self) -> None:
        """Muestra una vista previa de los cambios."""
        # TODO: Implementar vista previa
        pass
        
    def _execute_changes(self) -> None:
        """Ejecuta los cambios en los archivos XML."""
        # TODO: Implementar ejecución de cambios
        pass 