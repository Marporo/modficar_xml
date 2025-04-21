"""
Módulo que contiene la ventana de ayuda para expresiones regulares.
Sigue el patrón de diseño Single Responsibility Principle.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from ..assets.themes.modern_theme import ModernoTema

class RegexHelpWindow:
    """Ventana de ayuda para expresiones regulares."""
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa la ventana de ayuda.
        
        Args:
            parent: Widget padre al que estará asociada la ventana
        """
        self.parent = parent
        self.window: Optional[tk.Toplevel] = None
        
    def show(self):
        """Muestra la ventana de ayuda."""
        self.window = tk.Toplevel(self.parent)
        self._configure_window()
        self._create_widgets()
        self._center_window()
        
    def _configure_window(self):
        """Configura las propiedades básicas de la ventana."""
        self.window.title("Ayuda - Expresiones Regulares")
        self.window.geometry("650x600")
        self.window.minsize(500, 400)
        self.window.transient(self.parent)
        self.window.grab_set()
        self.window.resizable(True, True)
        
    def _create_widgets(self):
        """Crea y configura todos los widgets de la ventana."""
        self._create_main_frame()
        self._create_title()
        self._create_text_area()
        self._create_close_button()
        self._insert_help_content()
        
    def _create_main_frame(self):
        """Crea y configura el frame principal."""
        self.main_frame = ttk.Frame(self.window, style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Configurar grid
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
    def _create_title(self):
        """Crea y configura el título de la ventana."""
        titulo_frame = ttk.Frame(self.main_frame)
        titulo_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        ttk.Label(
            titulo_frame,
            text="Guía de Expresiones Regulares",
            style='Title.TLabel',
            font=(ModernoTema.FONT_FAMILY, ModernoTema.TITLE_SIZE + 2, 'bold')
        ).pack(side=tk.LEFT)
        
    def _create_text_area(self):
        """Crea y configura el área de texto con scroll."""
        texto_frame = ttk.Frame(self.main_frame)
        texto_frame.grid(row=2, column=0, sticky='nsew')
        
        texto_frame.grid_columnconfigure(0, weight=1)
        texto_frame.grid_rowconfigure(0, weight=1)
        
        # Scrollbar
        scroll = ttk.Scrollbar(texto_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        self.texto = tk.Text(
            texto_frame,
            wrap=tk.WORD,
            font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE + 1),
            bg=ModernoTema.BG_COLOR,
            fg=ModernoTema.TEXT_COLOR,
            relief="flat",
            padx=15,
            pady=10,
            spacing1=8,
            spacing2=2,
            spacing3=8,
            yscrollcommand=scroll.set
        )
        self.texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=self.texto.yview)
        
        self._configure_text_tags()
        
    def _configure_text_tags(self):
        """Configura los estilos de texto."""
        self.texto.tag_configure(
            'titulo',
            font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE + 2, 'bold'),
            foreground=ModernoTema.ACCENT_COLOR,
            spacing1=15,
            spacing3=10
        )
        
        self.texto.tag_configure(
            'subtitulo',
            font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE + 1, 'bold'),
            spacing1=10,
            spacing3=5
        )
        
        self.texto.tag_configure(
            'codigo',
            font=('Consolas', ModernoTema.FONT_SIZE),
            background='#f8f9fa',
            spacing1=5,
            spacing3=5
        )
        
    def _create_close_button(self):
        """Crea y configura el botón de cerrar."""
        botones_frame = ttk.Frame(self.main_frame)
        botones_frame.grid(row=3, column=0, sticky='e', pady=(20, 0))
        
        ttk.Button(
            botones_frame,
            text="Cerrar",
            command=self.window.destroy,
            style='Secondary.TButton',
            width=15
        ).pack(side=tk.RIGHT)
        
    def _insert_help_content(self):
        """Inserta el contenido de ayuda con formato."""
        self._insert_section_what_is()
        self._insert_section_when_to_use()
        self._insert_section_examples()
        self._insert_section_tips()
        self._insert_section_recommendation()
        self.texto.config(state='disabled')
        
    def _insert_section_what_is(self):
        """Inserta la sección '¿Qué son las expresiones regulares?'"""
        self.texto.insert('end', "¿Qué son las expresiones regulares?\n", 'titulo')
        self.texto.insert('end', "Las expresiones regulares son patrones de búsqueda que permiten "
                         "encontrar texto de forma flexible y potente. Son especialmente útiles cuando "
                         "necesitas buscar variaciones de un mismo texto o patrones específicos.\n\n")
    
    def _insert_section_when_to_use(self):
        """Inserta la sección '¿Cuándo usar expresiones regulares?'"""
        self.texto.insert('end', "¿Cuándo usar expresiones regulares?\n", 'titulo')
        self.texto.insert('end', "• Cuando necesitas buscar variaciones de un mismo texto\n")
        self.texto.insert('end', "• Cuando quieres encontrar patrones (como números, fechas, códigos)\n")
        self.texto.insert('end', "• Cuando necesitas hacer búsquedas que ignoren mayúsculas/minúsculas\n\n")
    
    def _insert_section_examples(self):
        """Inserta la sección de ejemplos."""
        self.texto.insert('end', "Ejemplos comunes\n", 'titulo')
        
        examples = [
            ("1. Buscar con o sin mayúsculas:", "[Pp]recio → Encuentra \"precio\" y \"Precio\""),
            ("2. Buscar números:", "precio\\d+ → Encuentra \"precio1\", \"precio2\", \"precio123\""),
            ("3. Buscar texto que empiece o termine con algo:", 
             "^precio → Encuentra texto que empiece con \"precio\"\n"
             "precio$ → Encuentra texto que termine con \"precio\""),
            ("4. Buscar cualquier carácter:", 
             "precio.* → Encuentra \"precio final\", \"precio base\", etc."),
            ("5. Buscar opciones específicas:",
             "precio(base|final) → Encuentra \"preciobase\" o \"preciofinal\"")
        ]
        
        for title, code in examples:
            self.texto.insert('end', f"\n{title}\n", 'subtitulo')
            self.texto.insert('end', f"{code}\n", 'codigo')
    
    def _insert_section_tips(self):
        """Inserta la sección de consejos."""
        self.texto.insert('end', "\nConsejos útiles\n", 'titulo')
        tips = [
            "• El punto (.) representa cualquier carácter",
            "• El asterisco (*) significa \"0 o más veces\"",
            "• El más (+) significa \"1 o más veces\"",
            "• Los corchetes [] definen un conjunto de caracteres",
            "• El circunflejo (^) al inicio busca al comienzo del texto",
            "• El dólar ($) al final busca al final del texto"
        ]
        for tip in tips:
            self.texto.insert('end', f"{tip}\n")
    
    def _insert_section_recommendation(self):
        """Inserta la sección de recomendación."""
        self.texto.insert('end', "\nRecomendación\n", 'titulo')
        self.texto.insert('end', "Siempre usa primero el botón de \"Vista Previa\" para "
                         "verificar qué cambios se realizarán antes de ejecutar la modificación.")
    
    def _center_window(self):
        """Centra la ventana en la pantalla."""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'{width}x{height}+{x}+{y}') 