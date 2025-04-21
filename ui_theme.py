# ui_theme.py - Contiene la definición del tema y estilos

import sys
import tkinter as tk
from tkinter import ttk

class ModernoTema:
    """Clase para definir colores y estilos modernos"""
    BG_COLOR = "#f5f5f7"
    TEXT_COLOR = "#333333"
    ACCENT_COLOR = "#0071e3"
    SUCCESS_COLOR = "#34c759"
    WARNING_COLOR = "#ff9500"
    ERROR_COLOR = "#ff3b30"
    LIGHT_ACCENT = "#e8f0fe"
    BORDER_COLOR = "#d1d1d6"
    
    FONT_FAMILY = "Segoe UI" if sys.platform.startswith('win') else "Helvetica Neue"
    FONT_SIZE = 10
    TITLE_SIZE = 16
    
    @classmethod
    def configurar_estilo(cls):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configuración general
        style.configure('TFrame', background=cls.BG_COLOR)
        style.configure('TLabel', background=cls.BG_COLOR, foreground=cls.TEXT_COLOR,
                         font=(cls.FONT_FAMILY, cls.FONT_SIZE))
        style.configure('TEntry', foreground=cls.TEXT_COLOR, fieldbackground='white',
                         borderwidth=1, relief='solid')
        style.map('TEntry', bordercolor=[('focus', cls.ACCENT_COLOR)])
        
        # Botón principal
        style.configure('Accent.TButton', background=cls.ACCENT_COLOR, foreground='white',
                         font=(cls.FONT_FAMILY, cls.FONT_SIZE, 'bold'),
                         borderwidth=0, focusthickness=0)
        style.map('Accent.TButton', 
                  background=[('active', '#005bbf'), ('pressed', '#0062cc')],
                  relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # Botón secundario
        style.configure('Secondary.TButton', background='#e0e0e0', foreground=cls.TEXT_COLOR,
                         font=(cls.FONT_FAMILY, cls.FONT_SIZE),
                         borderwidth=0, focusthickness=0)
        style.map('Secondary.TButton', 
                  background=[('active', '#d0d0d0'), ('pressed', '#c0c0c0')],
                  relief=[('pressed', 'flat'), ('!pressed', 'flat')])
        
        # Títulos
        style.configure('Title.TLabel', font=(cls.FONT_FAMILY, cls.TITLE_SIZE, 'bold'),
                        background=cls.BG_COLOR, foreground=cls.TEXT_COLOR)
        
        # Treeview (para listas y tablas)
        style.configure('Treeview', 
                       background='white',
                       foreground=cls.TEXT_COLOR,
                       fieldbackground='white',
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE))
        style.configure('Treeview.Heading',
                       background=cls.BG_COLOR,
                       foreground=cls.TEXT_COLOR,
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE, 'bold'))
        style.map('Treeview',
                 background=[('selected', cls.ACCENT_COLOR)],
                 foreground=[('selected', 'white')])
        
        # Progressbar
        style.configure('TProgressbar',
                       background=cls.ACCENT_COLOR,
                       troughcolor=cls.BG_COLOR,
                       borderwidth=0,
                       thickness=10)
        
        # Notebook (pestañas)
        style.configure('TNotebook',
                       background=cls.BG_COLOR,
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=cls.BG_COLOR,
                       foreground=cls.TEXT_COLOR,
                       padding=[10, 5],
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE))
        style.map('TNotebook.Tab',
                 background=[('selected', cls.ACCENT_COLOR)],
                 foreground=[('selected', 'white')])
        
        # LabelFrame
        style.configure('TLabelframe',
                       background=cls.BG_COLOR,
                       foreground=cls.TEXT_COLOR)
        style.configure('TLabelframe.Label',
                       background=cls.BG_COLOR,
                       foreground=cls.TEXT_COLOR,
                       font=(cls.FONT_FAMILY, cls.FONT_SIZE, 'bold'))
        
        # Scrollbar
        style.configure('TScrollbar',
                       background=cls.BG_COLOR,
                       troughcolor=cls.BG_COLOR,
                       borderwidth=0,
                       arrowcolor=cls.TEXT_COLOR)
        style.map('TScrollbar',
                 background=[('active', cls.ACCENT_COLOR)],
                 arrowcolor=[('active', 'white')])