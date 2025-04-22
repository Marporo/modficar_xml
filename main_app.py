# main_app.py - Archivo principal que integra todo

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext, simpledialog
import os
import sys
import ctypes
import re
import json
from datetime import datetime
from threading import Thread
import logging
from lxml import etree as ET
from copy import deepcopy
import pandas as pd
from typing import Dict, List, Set, Optional, Tuple

# Importar nuestros propios módulos
from xml_modifier import modificar_xml, validar_xml, obtener_etiquetas_unicas, obtener_valores_etiqueta
from ui_theme import ModernoTema

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

# Hacer que la aplicación sea consciente de la alta resolución (DPI-aware) en Windows
if sys.platform.startswith('win'):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

class AplicacionXML(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title("Modificador de XML")
        self.geometry("800x600")
        
        # Variables de la aplicación
        self.archivo_seleccionado = tk.StringVar()
        self.directorio_seleccionado = tk.StringVar()
        self.modo_multiple = tk.BooleanVar(value=False)
        self.etiqueta = tk.StringVar()
        self.valor_actual = tk.StringVar()
        self.valor_nuevo = tk.StringVar()
        self.usar_regex = tk.BooleanVar(value=False)
        self.progress_var = tk.DoubleVar()
        self.etiquetas_disponibles = []  # Lista para almacenar las etiquetas disponibles
        
        # Inicialización de listas y diccionarios
        self.historial_cambios = []
        
        # Crear notebook para pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear pestañas
        self.pestaña_principal = ttk.Frame(self.notebook)
        self.pestaña_historial = ttk.Frame(self.notebook)
        self.pestaña_tabular = ttk.Frame(self.notebook)
        
        # Agregar pestañas al notebook
        self.notebook.add(self.pestaña_principal, text="Modificar XML")
        self.notebook.add(self.pestaña_historial, text="Historial")
        self.notebook.add(self.pestaña_tabular, text="Editor Tabular XML")
        
        # Configurar cada pestaña
        self.configurar_pestaña_principal()
        self.configurar_pestaña_historial()
        self.configurar_pestaña_tabular()
        
        # Centrar la ventana
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def configurar_pestaña_principal(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self.pestaña_principal, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = ttk.Label(main_frame, text="Modificador Avanzado de XML", 
                          style='Title.TLabel',
                          font=(ModernoTema.FONT_FAMILY, ModernoTema.TITLE_SIZE + 4, 'bold'),
                          foreground='#0066cc')  # Azul
        titulo.pack(pady=(0, 25))
        
        # Frame para selección de modo y archivo/directorio
        seleccion_frame = ttk.Frame(main_frame)
        seleccion_frame.pack(fill=tk.X, pady=5)
        
        # Modo de operación
        modo_frame = ttk.Frame(seleccion_frame)
        modo_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(modo_frame, text="Archivo único", variable=self.modo_multiple, 
                       value=False, command=self.cambiar_modo).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(modo_frame, text="Múltiples archivos", variable=self.modo_multiple, 
                       value=True, command=self.cambiar_modo).pack(side=tk.LEFT, padx=5)
        
        # Frame contenedor para archivo/directorio
        self.selector_frame = ttk.Frame(seleccion_frame)
        self.selector_frame.pack(fill=tk.X, pady=5)
        
        # Frame para selección de archivo
        self.archivo_frame = ttk.Frame(self.selector_frame)
        ttk.Label(self.archivo_frame, text="Archivo XML:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(self.archivo_frame, textvariable=self.archivo_seleccionado, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.archivo_frame, text="Buscar", command=self.buscar_archivo, 
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para selección de directorio
        self.directorio_frame = ttk.Frame(self.selector_frame)
        ttk.Label(self.directorio_frame, text="Directorio:").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Entry(self.directorio_frame, textvariable=self.directorio_seleccionado, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(self.directorio_frame, text="Buscar", command=self.buscar_directorio, 
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para etiqueta y valores
        valores_frame = ttk.LabelFrame(main_frame, text="Modificación")
        valores_frame.pack(fill=tk.X, pady=10)
        
        # Etiqueta
        ttk.Label(valores_frame, text="Etiqueta:").pack(anchor=tk.W, padx=5, pady=2)
        self.etiqueta_combobox = ttk.Combobox(valores_frame, textvariable=self.etiqueta)
        self.etiqueta_combobox.pack(fill=tk.X, padx=5, pady=2)
        self.etiqueta_combobox.bind('<<ComboboxSelected>>', self.actualizar_valores_disponibles)
        
        # Valor actual y opciones de regex
        valor_actual_frame = ttk.Frame(valores_frame)
        valor_actual_frame.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(valor_actual_frame, text="Valor actual:").pack(anchor=tk.W)
        
        valor_entrada_frame = ttk.Frame(valor_actual_frame)
        valor_entrada_frame.pack(fill=tk.X, pady=2)
        
        self.valor_actual_combobox = ttk.Combobox(valor_entrada_frame, textvariable=self.valor_actual)
        self.valor_actual_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        regex_frame = ttk.Frame(valor_actual_frame)
        regex_frame.pack(fill=tk.X, pady=(2, 0))
        
        ttk.Checkbutton(regex_frame, text="Usar expresiones regulares", 
                       variable=self.usar_regex).pack(side=tk.LEFT)
        ttk.Button(regex_frame, text="?", width=3, 
                  command=self.mostrar_ayuda_regex,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(5, 0))
        
        # Valor nuevo
        ttk.Label(valores_frame, text="Valor nuevo:").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Entry(valores_frame, textvariable=self.valor_nuevo).pack(fill=tk.X, padx=5, pady=2)
        
        # Botones de acción
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(botones_frame, text="Vista Previa", command=self.vista_previa, 
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Ejecutar", command=self.ejecutar_modificacion, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Área de resultados
        resultados_frame = ttk.LabelFrame(main_frame, text="Resultados")
        resultados_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(resultados_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Listo")
        self.status_label.pack(side=tk.LEFT, pady=5)
        
        # Inicializar modo
        self.cambiar_modo()
    
    def configurar_pestaña_historial(self):
        # Frame principal
        main_frame = ttk.Frame(self.pestaña_historial)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Lista de historial
        self.historial_tree = ttk.Treeview(main_frame, columns=("fecha", "archivo", "etiqueta", "cambios"), show="headings")
        self.historial_tree.heading("fecha", text="Fecha")
        self.historial_tree.heading("archivo", text="Archivo")
        self.historial_tree.heading("etiqueta", text="Etiqueta")
        self.historial_tree.heading("cambios", text="Cambios")
        
        self.historial_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Botones
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Exportar", command=self.exportar_historial, 
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpiar", command=self.limpiar_historial, 
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
    
    def configurar_pestaña_tabular(self):
        """Configura la pestaña de vista tabular del XML"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.pestaña_tabular, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = ttk.Label(main_frame, text="Editor Tabular XML", 
                          style='Title.TLabel',
                          font=(ModernoTema.FONT_FAMILY, ModernoTema.TITLE_SIZE + 4, 'bold'),
                          foreground='#0066cc')
        titulo.pack(pady=(0, 25))
        
        # Frame para controles superiores
        controles_frame = ttk.Frame(main_frame)
        controles_frame.pack(fill=tk.X, pady=5)
        
        # Frame para selección de archivo
        archivo_frame = ttk.Frame(controles_frame)
        archivo_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(archivo_frame, text="Archivo XML:").pack(side=tk.LEFT, padx=(0, 10))
        self.archivo_tabular = tk.StringVar()
        ttk.Entry(archivo_frame, textvariable=self.archivo_tabular, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(archivo_frame, text="Buscar", command=self.buscar_archivo_tabular, 
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para búsqueda y filtros
        filtros_frame = ttk.Frame(controles_frame)
        filtros_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(filtros_frame, text="Buscar:").pack(side=tk.LEFT, padx=(0, 5))
        self.busqueda_var = tk.StringVar()
        self.busqueda_var.trace('w', self.filtrar_tabla)
        ttk.Entry(filtros_frame, textvariable=self.busqueda_var, width=20).pack(side=tk.LEFT)
        
        # Contenedor principal para la tabla
        self.tabla_container = ttk.Frame(main_frame)
        self.tabla_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Configurar el contenedor para usar grid
        self.tabla_container.grid_rowconfigure(0, weight=1)
        self.tabla_container.grid_columnconfigure(0, weight=1)
        
        # Crear Treeview con estilo mejorado
        style = ttk.Style()
        style.configure("Tabular.Treeview",
                       background="white",
                       foreground="black",
                       fieldbackground="white",
                       borderwidth=1,
                       relief="solid")
        style.configure("Tabular.Treeview.Heading",
                       background=ModernoTema.BG_COLOR,
                       foreground=ModernoTema.TEXT_COLOR,
                       relief="solid",
                       borderwidth=1)
        style.layout("Tabular.Treeview", [
            ('Tabular.Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # Crear y configurar la tabla
        self.tabla_xml = ttk.Treeview(self.tabla_container, 
                                     style="Tabular.Treeview", 
                                     show="headings",
                                     selectmode="extended")
        
        # Scrollbars
        self.scrollbar_y = ttk.Scrollbar(self.tabla_container, 
                                        orient="vertical", 
                                        command=self.tabla_xml.yview)
        self.scrollbar_x = ttk.Scrollbar(self.tabla_container, 
                                        orient="horizontal", 
                                        command=self.tabla_xml.xview)
        
        # Configurar la tabla para usar los scrollbars
        self.tabla_xml.configure(yscrollcommand=self.set_scroll_y,
                               xscrollcommand=self.scrollbar_x.set)
        
        # Posicionar elementos usando grid
        self.tabla_xml.grid(row=0, column=0, sticky="nsew")
        self.scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Frame para botones de acción
        botones_frame = ttk.Frame(main_frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        # Botones de acción
        ttk.Button(botones_frame, text="Exportar a Excel", command=self.exportar_excel,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Vista Previa XML", command=self.mostrar_vista_previa_xml,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Deshacer", command=self.deshacer_cambio,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Rehacer", command=self.rehacer_cambio,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(botones_frame, text="Guardar Cambios", command=self.guardar_cambios_tabular,
                  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
        
        # Configurar eventos de la tabla
        self.tabla_xml.bind('<Double-1>', self.editar_celda_tabular)
        self.tabla_xml.bind('<Control-c>', self.copiar_seleccion)
        self.tabla_xml.bind('<Control-v>', self.pegar_seleccion)
        self.tabla_xml.bind('<Return>', lambda e: self.editar_celda_tabular(e))
        self.tabla_xml.bind('<Tab>', self.mover_siguiente_celda)
        self.tabla_xml.bind('<Shift-Tab>', self.mover_celda_anterior)
        
        # Configurar el scrolling con la rueda del mouse
        self.tabla_xml.bind('<MouseWheel>', self.on_mousewheel)
        self.tabla_xml.bind('<Shift-MouseWheel>', self.on_shift_mousewheel)
        
        # Variables para el historial de cambios
        self.historial_cambios = []
        self.indice_actual = -1
        self.xml_original = None
        
        # Configurar estilos para diferentes tipos de contenido
        self.tabla_xml.tag_configure('json', background='#e8f0fe')
        self.tabla_xml.tag_configure('sql', background='#f0f8ff')
        self.tabla_xml.tag_configure('xml', background='#f5f5f5')
    
    def cambiar_modo(self):
        # Ocultar ambos frames primero
        for widget in self.selector_frame.winfo_children():
            widget.pack_forget()
            
        # Mostrar el frame correspondiente
        if self.modo_multiple.get():
            self.directorio_frame.pack(fill=tk.X)
        else:
            self.archivo_frame.pack(fill=tk.X)
        
        self.actualizar_etiquetas_disponibles()
    
    def actualizar_etiquetas_disponibles(self):
        """Actualiza la lista de etiquetas disponibles basado en los archivos seleccionados"""
        try:
            self.etiquetas_disponibles = set()
            
            if self.modo_multiple.get():
                directorio = self.directorio_seleccionado.get()
                if os.path.exists(directorio):
                    for archivo in os.listdir(directorio):
                        if archivo.endswith('.xml'):
                            ruta_completa = os.path.join(directorio, archivo)
                            etiquetas = obtener_etiquetas_unicas(ruta_completa)
                            self.etiquetas_disponibles.update(etiquetas)
            else:
                archivo = self.archivo_seleccionado.get()
                if os.path.exists(archivo) and archivo.endswith('.xml'):
                    self.etiquetas_disponibles = obtener_etiquetas_unicas(archivo)
            
            # Actualizar el combobox
            self.etiqueta_combobox['values'] = sorted(list(self.etiquetas_disponibles))
            if self.etiquetas_disponibles:
                self.etiqueta_combobox.set('')  # Limpiar selección actual
                self.valor_actual_combobox.set('')  # Limpiar también el valor actual
                self.valor_actual_combobox['values'] = []  # Limpiar lista de valores
                
        except Exception as e:
            self.actualizar_log(f"Error al actualizar etiquetas: {str(e)}")
            messagebox.showerror("Error", f"Error al actualizar etiquetas: {str(e)}")
    
    def buscar_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")])
        if archivo:
            self.archivo_seleccionado.set(archivo)
            self.actualizar_log(f"Archivo seleccionado: {os.path.basename(archivo)}")
            self.actualizar_etiquetas_disponibles()
    
    def actualizar_log(self, mensaje):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, mensaje)
        self.log_text.config(state=tk.DISABLED)
    
    def buscar_directorio(self):
        directorio = filedialog.askdirectory()
        if directorio:
            self.directorio_seleccionado.set(directorio)
            self.actualizar_log(f"Directorio seleccionado: {directorio}")
            self.actualizar_etiquetas_disponibles()
    
    def vista_previa(self):
        try:
            # Validar campos
            self.validar_campos()
            
            # Obtener archivos a procesar
            archivos = self.obtener_archivos_xml()
            
            # Mostrar vista previa
            self.actualizar_log("Vista previa de cambios:\n")
            for archivo in archivos:
                cambios = modificar_xml(archivo, self.etiqueta.get(), 
                                     self.valor_actual.get(), self.valor_nuevo.get(),
                                     preview=True, usar_regex=self.usar_regex.get())
                self.actualizar_log(f"\nArchivo: {os.path.basename(archivo)}")
                self.actualizar_log(f"Cambios encontrados: {cambios}")
            
        except Exception as e:
            self.actualizar_log(f"Error en vista previa: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def ejecutar_modificacion(self):
        try:
            # Validar campos
            self.validar_campos()
            
            # Obtener archivos a procesar
            archivos = self.obtener_archivos_xml()
            
            # Iniciar barra de progreso
            self.progress_var.set(0)
            total_archivos = len(archivos)
            
            # Procesar archivos
            for i, archivo in enumerate(archivos):
                # Actualizar progreso
                self.progress_var.set((i / total_archivos) * 100)
                self.update()
                
                # Procesar archivo
                cambios = modificar_xml(archivo, self.etiqueta.get(), 
                                     self.valor_actual.get(), self.valor_nuevo.get(),
                                     usar_regex=self.usar_regex.get())
                
                # Registrar en historial
                self.registrar_historial(archivo, cambios)
                
                # Actualizar log
                self.actualizar_log(f"\nArchivo: {os.path.basename(archivo)}")
                self.actualizar_log(f"Cambios realizados: {cambios}")
            
            # Completar progreso
            self.progress_var.set(100)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Modificación completada")
            
        except Exception as e:
            self.actualizar_log(f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def validar_campos(self):
        if self.modo_multiple.get():
            if not self.directorio_seleccionado.get():
                raise ValueError("Debe seleccionar un directorio")
        else:
            if not self.archivo_seleccionado.get():
                raise ValueError("Debe seleccionar un archivo XML")
        
        if not self.etiqueta.get():
            raise ValueError("Debe especificar una etiqueta")
        if not self.valor_actual.get():
            raise ValueError("Debe especificar el valor actual")
        if not self.valor_nuevo.get():
            raise ValueError("Debe especificar el nuevo valor")
    
    def obtener_archivos_xml(self):
        try:
            if self.modo_multiple.get():
                directorio = self.directorio_seleccionado.get()
                if not os.path.exists(directorio):
                    raise ValueError(f"El directorio {directorio} no existe")
                
                archivos_xml = [os.path.join(directorio, f) for f in os.listdir(directorio) 
                              if f.endswith('.xml')]
                
                if not archivos_xml:
                    raise ValueError(f"No se encontraron archivos XML en el directorio {directorio}")
                
                return archivos_xml
            else:
                archivo = self.archivo_seleccionado.get()
                if not os.path.exists(archivo):
                    raise ValueError(f"El archivo {archivo} no existe")
                if not archivo.endswith('.xml'):
                    raise ValueError(f"El archivo {archivo} no es un archivo XML")
                return [archivo]
                
        except Exception as e:
            self.actualizar_log(f"Error al obtener archivos XML: {str(e)}")
            raise
    
    def registrar_historial(self, archivo, cambios):
        self.historial_cambios.append({
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'archivo': os.path.basename(archivo),
            'etiqueta': self.etiqueta.get(),
            'cambios': cambios
        })
        
        # Actualizar árbol de historial
        self.historial_tree.insert('', 0, values=(
            self.historial_cambios[-1]['fecha'],
            self.historial_cambios[-1]['archivo'],
            self.historial_cambios[-1]['etiqueta'],
            self.historial_cambios[-1]['cambios']
        ))
    
    def exportar_historial(self):
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")]
        )
        if archivo:
            with open(archivo, 'w') as f:
                json.dump(self.historial_cambios, f, indent=4)
            messagebox.showinfo("Éxito", "Historial exportado correctamente")
    
    def limpiar_historial(self):
        if messagebox.askyesno("Confirmar", "¿Desea limpiar todo el historial?"):
            self.historial_cambios = []
            for item in self.historial_tree.get_children():
                self.historial_tree.delete(item)

    def mostrar_ayuda_regex(self):
        """Muestra una ventana de ayuda con información sobre expresiones regulares"""
        ventana_ayuda = tk.Toplevel(self)
        ventana_ayuda.title("Ayuda - Expresiones Regulares")
        ventana_ayuda.geometry("650x600")
        ventana_ayuda.minsize(500, 400)  # Tamaño mínimo
        
        # Hacer que la ventana sea modal pero permitir maximizar
        ventana_ayuda.transient(self)
        ventana_ayuda.grab_set()
        
        # Permitir que la ventana sea redimensionable y maximizable
        ventana_ayuda.resizable(True, True)
        
        # Configurar el comportamiento de maximización
        def toggle_maximize(event=None):
            if ventana_ayuda.state() == 'zoomed':
                ventana_ayuda.state('normal')
            else:
                ventana_ayuda.state('zoomed')
        
        # Agregar atajo de teclado para maximizar/restaurar (F11)
        ventana_ayuda.bind('<F11>', toggle_maximize)
        
        # Frame principal con padding y estilo moderno
        main_frame = ttk.Frame(ventana_ayuda, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Configurar el grid para que el contenido se expanda correctamente
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)  # La fila del texto expandible
        
        # Título con estilo moderno y botón de maximizar
        titulo_frame = ttk.Frame(main_frame)
        titulo_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
        
        ttk.Label(titulo_frame, 
                 text="Guía de Expresiones Regulares",
                 style='Title.TLabel',
                 font=(ModernoTema.FONT_FAMILY, ModernoTema.TITLE_SIZE + 2, 'bold')).pack(side=tk.LEFT)
        
        # Botón de maximizar
        ttk.Button(titulo_frame,
                  text="⛶",
                  command=toggle_maximize,
                  style='Secondary.TButton',
                  width=3).pack(side=tk.RIGHT)
        
        # Crear Text widget con scroll y estilo moderno
        texto_frame = ttk.Frame(main_frame)
        texto_frame.grid(row=2, column=0, sticky='nsew')
        
        # Configurar el grid del frame de texto
        texto_frame.grid_columnconfigure(0, weight=1)
        texto_frame.grid_rowconfigure(0, weight=1)
        
        # Estilo personalizado para el scrollbar
        scroll = ttk.Scrollbar(texto_frame)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Texto con estilo moderno
        texto = tk.Text(texto_frame, 
                       wrap=tk.WORD,
                       font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE + 1),
                       bg=ModernoTema.BG_COLOR,
                       fg=ModernoTema.TEXT_COLOR,
                       relief="flat",
                       padx=15,
                       pady=10,
                       spacing1=8,  # Espacio antes de cada línea
                       spacing2=2,  # Espacio entre líneas
                       spacing3=8,  # Espacio después de cada línea
                       yscrollcommand=scroll.set)
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.config(command=texto.yview)
        
        # Configurar tags para el formato del texto
        texto.tag_configure('titulo', 
                          font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE + 2, 'bold'),
                          foreground=ModernoTema.ACCENT_COLOR,
                          spacing1=15,
                          spacing3=10)
        
        texto.tag_configure('subtitulo',
                          font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE + 1, 'bold'),
                          spacing1=10,
                          spacing3=5)
        
        texto.tag_configure('codigo',
                          font=('Consolas', ModernoTema.FONT_SIZE),
                          background='#f8f9fa',
                          spacing1=5,
                          spacing3=5)
        
        # Insertar contenido con formato
        texto.insert('end', "¿Qué son las expresiones regulares?\n", 'titulo')
        texto.insert('end', "Las expresiones regulares son patrones de búsqueda que permiten encontrar texto de forma flexible y potente. Son especialmente útiles cuando necesitas buscar variaciones de un mismo texto o patrones específicos.\n\n")
        
        texto.insert('end', "¿Cuándo usar expresiones regulares?\n", 'titulo')
        texto.insert('end', "• Cuando necesitas buscar variaciones de un mismo texto\n")
        texto.insert('end', "• Cuando quieres encontrar patrones (como números, fechas, códigos)\n")
        texto.insert('end', "• Cuando necesitas hacer búsquedas que ignoren mayúsculas/minúsculas\n\n")
        
        texto.insert('end', "Ejemplos comunes\n", 'titulo')
        
        texto.insert('end', "1. Buscar con o sin mayúsculas:\n", 'subtitulo')
        texto.insert('end', "[Pp]recio → Encuentra \"precio\" y \"Precio\"\n", 'codigo')
        
        texto.insert('end', "\n2. Buscar números:\n", 'subtitulo')
        texto.insert('end', "precio\\d+ → Encuentra \"precio1\", \"precio2\", \"precio123\"\n", 'codigo')
        
        texto.insert('end', "\n3. Buscar texto que empiece o termine con algo:\n", 'subtitulo')
        texto.insert('end', "^precio → Encuentra texto que empiece con \"precio\"\n", 'codigo')
        texto.insert('end', "precio$ → Encuentra texto que termine con \"precio\"\n", 'codigo')
        
        texto.insert('end', "\n4. Buscar cualquier carácter:\n", 'subtitulo')
        texto.insert('end', "precio.* → Encuentra \"precio final\", \"precio base\", etc.\n", 'codigo')
        
        texto.insert('end', "\n5. Buscar opciones específicas:\n", 'subtitulo')
        texto.insert('end', "precio(base|final) → Encuentra \"preciobase\" o \"preciofinal\"\n", 'codigo')
        
        texto.insert('end', "\nConsejos útiles\n", 'titulo')
        texto.insert('end', "• El punto (.) representa cualquier carácter\n")
        texto.insert('end', "• El asterisco (*) significa \"0 o más veces\"\n")
        texto.insert('end', "• El más (+) significa \"1 o más veces\"\n")
        texto.insert('end', "• Los corchetes [] definen un conjunto de caracteres\n")
        texto.insert('end', "• El circunflejo (^) al inicio busca al comienzo del texto\n")
        texto.insert('end', "• El dólar ($) al final busca al final del texto\n\n")
        
        texto.insert('end', "Recomendación\n", 'titulo')
        texto.insert('end', "Siempre usa primero el botón de \"Vista Previa\" para verificar qué cambios se realizarán antes de ejecutar la modificación.")
        
        # Hacer el texto de solo lectura
        texto.config(state='disabled')
        
        # Frame para los botones
        botones_frame = ttk.Frame(main_frame)
        botones_frame.grid(row=3, column=0, sticky='e', pady=(20, 0))
        
        # Botón de maximizar
        ttk.Button(botones_frame, 
                  text="Maximizar",
                  command=toggle_maximize,
                  style='Secondary.TButton',
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón de cerrar con estilo moderno
        ttk.Button(botones_frame, 
                  text="Cerrar",
                  command=ventana_ayuda.destroy,
                  style='Secondary.TButton',
                  width=15).pack(side=tk.RIGHT)
        
        # Centrar la ventana
        ventana_ayuda.update_idletasks()
        width = ventana_ayuda.winfo_width()
        height = ventana_ayuda.winfo_height()
        x = (ventana_ayuda.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana_ayuda.winfo_screenheight() // 2) - (height // 2)
        ventana_ayuda.geometry(f'{width}x{height}+{x}+{y}')

    def actualizar_valores_disponibles(self, event=None):
        """Actualiza la lista de valores disponibles para la etiqueta seleccionada"""
        try:
            valores_disponibles = set()
            etiqueta = self.etiqueta.get()
            
            if not etiqueta:
                return
                
            if self.modo_multiple.get():
                directorio = self.directorio_seleccionado.get()
                if os.path.exists(directorio):
                    for archivo in os.listdir(directorio):
                        if archivo.endswith('.xml'):
                            ruta_completa = os.path.join(directorio, archivo)
                            valores = obtener_valores_etiqueta(ruta_completa, etiqueta)
                            valores_disponibles.update(valores)
            else:
                archivo = self.archivo_seleccionado.get()
                if os.path.exists(archivo) and archivo.endswith('.xml'):
                    valores_disponibles = obtener_valores_etiqueta(archivo, etiqueta)
            
            # Actualizar el combobox
            self.valor_actual_combobox['values'] = sorted(list(valores_disponibles))
            if valores_disponibles:
                self.valor_actual_combobox.set('')  # Limpiar selección actual
                
        except Exception as e:
            self.actualizar_log(f"Error al actualizar valores: {str(e)}")
            messagebox.showerror("Error", f"Error al actualizar valores: {str(e)}")

    def buscar_archivo_tabular(self):
        """Busca y carga un archivo XML para la vista tabular"""
        archivo = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")])
        if archivo:
            self.archivo_tabular.set(archivo)
            self.cargar_xml_tabular(archivo)
    
    def cargar_xml_tabular(self, archivo):
        """Carga el XML en formato tabular"""
        try:
            # Limpiar tabla existente
            for col in self.tabla_xml['columns']:
                self.tabla_xml.heading(col, text='')
            self.tabla_xml['columns'] = []
            for item in self.tabla_xml.get_children():
                self.tabla_xml.delete(item)
            
            # Parsear XML preservando espacios en blanco
            parser = ET.XMLParser(remove_blank_text=True)
            tree = ET.parse(archivo, parser)
            self.xml_original = tree
            root = tree.getroot()
            
            # Obtener todas las etiquetas únicas manteniendo el orden
            etiquetas = self.obtener_etiquetas_unicas_xml(root)
            
            # Configurar columnas
            self.tabla_xml['columns'] = etiquetas
            ancho_total = 0
            for etiqueta in etiquetas:
                self.tabla_xml.heading(etiqueta, 
                                     text=etiqueta,
                                     command=lambda c=etiqueta: self.ordenar_columna(c))
                # Configurar un ancho inicial más pequeño para forzar la aparición del scroll horizontal
                ancho_inicial = min(200, self.tabla_container.winfo_width() // len(etiquetas))
                self.tabla_xml.column(etiqueta, 
                                    width=ancho_inicial,
                                    minwidth=50,
                                    stretch=False)  # Cambiar a False para permitir scroll horizontal
                ancho_total += ancho_inicial
            
            # Llenar tabla con datos
            self.llenar_tabla_xml(root)
            
            # Guardar estado inicial en historial
            self.guardar_estado_en_historial()
            
            # Mostrar mensaje de éxito
            logging.info(f"XML cargado exitosamente: {archivo}")
            
        except Exception as e:
            logging.error(f"Error al cargar XML: {str(e)}")
            self.mostrar_error(
                "Error al Cargar XML",
                "No se pudo cargar el archivo XML.",
                f"Detalles del error:\n{str(e)}\n\nRuta del archivo:\n{archivo}"
            )

    def on_shift_mousewheel(self, event):
        """Maneja el scroll horizontal con Shift + rueda del mouse"""
        self.tabla_xml.xview_scroll(-1 * (event.delta // 120), "units")

    def on_mousewheel(self, event):
        """Maneja el scroll vertical con la rueda del mouse"""
        try:
            # Obtener el número total de items y los items visibles
            total_items = len(self.tabla_xml.get_children())
            visible_items = self.tabla_xml.winfo_height() // 25  # altura aproximada por fila
            
            if total_items > 0:
                # Calcular el tamaño del paso basado en la proporción de items
                step = max(1, total_items // 20)  # Dividir el total en 20 pasos como mínimo
                delta = -1 * (event.delta // 120) * step
                
                # Mover la vista
                self.tabla_xml.yview_scroll(delta, "units")
            
        except Exception as e:
            logging.error(f"Error en mousewheel: {str(e)}")
            # Fallback al comportamiento predeterminado
            self.tabla_xml.yview_scroll(-1 * (event.delta // 120), "units")

    def redimensionar_columna(self, event):
        """Maneja el redimensionamiento de columna durante el arrastre"""
        if hasattr(self, '_columna_redimension'):
            diferencia = event.x - self._x_inicio
            ancho_actual = self.tabla_xml.column(self._columna_redimension, "width")
            nuevo_ancho = max(50, ancho_actual + diferencia)
            self.tabla_xml.column(self._columna_redimension, width=nuevo_ancho)
            self._x_inicio = event.x

    def ordenar_columna(self, columna):
        """Ordena la tabla por la columna seleccionada"""
        # Obtener el orden actual
        orden_actual = getattr(self, '_orden_columna', None)
        reverso = False
        
        if orden_actual == columna:
            reverso = True
            self._orden_columna = None
        else:
            self._orden_columna = columna
        
        # Obtener todos los items
        items = [(self.tabla_xml.set(item, columna), item) for item in self.tabla_xml.get_children('')]
        
        # Ordenar items
        items.sort(reverse=reverso)
        
        # Reordenar tabla
        for idx, (_, item) in enumerate(items):
            self.tabla_xml.move(item, '', idx)
    
    def llenar_tabla_xml(self, elemento, ruta_padre=""):
        """Llena la tabla con los datos del XML manteniendo la jerarquía"""
        try:
            ruta_actual = f"{ruta_padre}/{elemento.tag}" if ruta_padre else elemento.tag
            
            # Crear un diccionario para almacenar los valores
            valores = {col: "" for col in self.tabla_xml['columns']}
            
            # Procesar el elemento actual
            if elemento.text and elemento.text.strip():
                valores[elemento.tag] = elemento.text.strip()
            
            # Procesar atributos
            for attr, valor in elemento.attrib.items():
                if attr in valores:
                    valores[attr] = valor
            
            # Si tenemos algún valor no vacío, agregar la fila
            if any(v.strip() for v in valores.values()):
                valores_lista = [valores.get(col, "") for col in self.tabla_xml['columns']]
                self.tabla_xml.insert('', 'end', values=valores_lista, tags=(ruta_actual,))
            
            # Procesar elementos hijos
            for hijo in elemento:
                self.llenar_tabla_xml(hijo, ruta_actual)
                
        except Exception as e:
            logging.error(f"Error al llenar tabla: {str(e)}")
            raise

    def editar_celda_tabular(self, event):
        """Permite editar una celda de la tabla"""
        item = self.tabla_xml.selection()[0]
        columna = self.tabla_xml.identify_column(event.x)
        columna = int(columna[1]) - 1  # Convertir a índice
        
        # Crear ventana de edición
        ventana_edicion = tk.Toplevel(self)
        ventana_edicion.title("Editar Valor")
        
        # Obtener valor actual
        valores = self.tabla_xml.item(item)['values']
        valor_actual = valores[columna]
        
        # Crear widget de texto con scroll
        frame = ttk.Frame(ventana_edicion)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        texto = scrolledtext.ScrolledText(frame, wrap=tk.WORD, width=50, height=10)
        texto.pack(fill=tk.BOTH, expand=True)
        texto.insert('1.0', valor_actual)
        
        def guardar_cambio():
            nuevo_valor = texto.get('1.0', 'end-1c')
            valores[columna] = nuevo_valor
            self.tabla_xml.item(item, values=valores)
            ventana_edicion.destroy()
        
        ttk.Button(ventana_edicion, text="Guardar", command=guardar_cambio,
                  style='Accent.TButton').pack(pady=10)
    
    def guardar_cambios_tabular(self):
        """Guarda los cambios realizados en la tabla al archivo XML"""
        if not self.archivo_tabular.get():
            self.mostrar_error(
                "Advertencia",
                "No hay archivo XML seleccionado",
                "Por favor, seleccione un archivo XML antes de guardar los cambios."
            )
            return
        
        try:
            # Generar nuevo árbol XML
            root = self.generar_xml_desde_tabla()
            
            # Guardar archivo con codificación y formato adecuados
            tree = ET.ElementTree(root)
            tree.write(self.archivo_tabular.get(), 
                      encoding='utf-8', 
                      xml_declaration=True, 
                      pretty_print=True)
            
            messagebox.showinfo("Éxito", "Cambios guardados correctamente")
            
        except Exception as e:
            logging.error(f"Error al guardar cambios: {str(e)}")
            self.mostrar_error(
                "Error al Guardar",
                "No se pudieron guardar los cambios en el archivo XML.",
                f"Detalles del error:\n{str(e)}\n\nRuta del archivo:\n{self.archivo_tabular.get()}"
            )

    def filtrar_tabla(self, *args):
        """Filtra la tabla según el texto de búsqueda"""
        texto_busqueda = self.busqueda_var.get().lower()
        
        for item in self.tabla_xml.get_children():
            valores = self.tabla_xml.item(item)['values']
            if any(texto_busqueda in str(valor).lower() for valor in valores):
                self.tabla_xml.reattach(item, '', 'end')
            else:
                self.tabla_xml.detach(item)
    
    def exportar_excel(self):
        """Exporta la tabla actual a un archivo Excel"""
        if not self.tabla_xml.get_children():
            self.mostrar_error(
                "Advertencia",
                "No hay datos para exportar",
                "La tabla está vacía. Por favor, cargue un archivo XML primero."
            )
            return
            
        try:
            # Obtener datos de la tabla
            datos = []
            columnas = self.tabla_xml['columns']
            
            for item in self.tabla_xml.get_children():
                valores = self.tabla_xml.item(item)['values']
                datos.append(dict(zip(columnas, valores)))
            
            # Crear DataFrame y exportar
            df = pd.DataFrame(datos)
            df.to_excel(self.archivo_tabular.get(), index=False)
            
            messagebox.showinfo("Éxito", "Datos exportados correctamente")
            
        except Exception as e:
            self.mostrar_error(
                "Error al Exportar",
                "No se pudo exportar a Excel.",
                f"Detalles del error:\n{str(e)}"
            )
    
    def mostrar_vista_previa_xml(self):
        """Muestra una vista previa del XML resultante"""
        try:
            # Crear ventana de vista previa
            ventana_previa = tk.Toplevel(self)
            ventana_previa.title("Vista Previa XML")
            ventana_previa.geometry("800x600")
            
            # Crear widget de texto con scroll
            texto = scrolledtext.ScrolledText(ventana_previa, wrap=tk.NONE)
            texto.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Generar XML temporal y convertirlo a cadena
            xml_temp = self.generar_xml_desde_tabla()
            xml_str = ET.tostring(xml_temp, encoding='unicode', pretty_print=True)
            
            # Insertar el XML formateado en el widget de texto
            texto.insert('1.0', xml_str)
            texto.config(state='disabled')
            
            # Centrar la ventana
            ventana_previa.update_idletasks()
            width = ventana_previa.winfo_width()
            height = ventana_previa.winfo_height()
            x = (ventana_previa.winfo_screenwidth() // 2) - (width // 2)
            y = (ventana_previa.winfo_screenheight() // 2) - (height // 2)
            ventana_previa.geometry(f'{width}x{height}+{x}+{y}')
            
        except Exception as e:
            logging.error(f"Error al generar vista previa: {str(e)}")
            self.mostrar_error(
                "Error en Vista Previa",
                "No se pudo generar la vista previa del XML.",
                f"Detalles del error:\n{str(e)}"
            )
    
    def deshacer_cambio(self):
        """Deshace el último cambio realizado"""
        if self.indice_actual > 0:
            self.indice_actual -= 1
            self.aplicar_estado(self.historial_cambios[self.indice_actual])
    
    def rehacer_cambio(self):
        """Rehace el último cambio deshecho"""
        if self.indice_actual < len(self.historial_cambios) - 1:
            self.indice_actual += 1
            self.aplicar_estado(self.historial_cambios[self.indice_actual])
    
    def aplicar_estado(self, estado):
        """Aplica un estado guardado en el historial"""
        # Limpiar tabla actual
        for item in self.tabla_xml.get_children():
            self.tabla_xml.delete(item)
        
        # Restaurar columnas
        self.tabla_xml['columns'] = estado['columnas']
        for col in estado['columnas']:
            self.tabla_xml.heading(col, text=col)
        
        # Restaurar datos
        for item in estado['items']:
            self.tabla_xml.insert('', 'end', values=item['valores'], tags=item.get('tags', []))
    
    def copiar_seleccion(self, event):
        """Copia el contenido de la celda seleccionada"""
        item = self.tabla_xml.selection()[0]
        columna = self.tabla_xml.identify_column(event.x)
        columna = int(columna[1]) - 1
        
        valores = self.tabla_xml.item(item)['values']
        self.clipboard_clear()
        self.clipboard_append(str(valores[columna]))
    
    def pegar_seleccion(self, event):
        """Pega el contenido en la celda seleccionada"""
        item = self.tabla_xml.selection()[0]
        columna = self.tabla_xml.identify_column(event.x)
        columna = int(columna[1]) - 1
        
        try:
            nuevo_valor = self.clipboard_get()
            valores = list(self.tabla_xml.item(item)['values'])
            valores[columna] = nuevo_valor
            
            # Guardar estado actual en historial
            self.guardar_estado_en_historial()
            
            # Actualizar celda
            self.tabla_xml.item(item, values=valores)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al pegar: {str(e)}")
    
    def guardar_estado_en_historial(self):
        """Guarda el estado actual en el historial de cambios"""
        estado = {
            'columnas': self.tabla_xml['columns'],
            'items': []
        }
        
        for item in self.tabla_xml.get_children():
            valores = self.tabla_xml.item(item)['values']
            tags = self.tabla_xml.item(item)['tags']
            estado['items'].append({
                'valores': valores,
                'tags': tags
            })
        
        # Eliminar estados futuros si estamos en medio del historial
        if self.indice_actual < len(self.historial_cambios) - 1:
            self.historial_cambios = self.historial_cambios[:self.indice_actual + 1]
        
        self.historial_cambios.append(estado)
        self.indice_actual = len(self.historial_cambios) - 1
    
    def generar_xml_desde_tabla(self) -> ET.Element:
        """Genera un árbol XML desde los datos de la tabla manteniendo la estructura jerárquica"""
        try:
            # Crear una copia del XML original para mantener la estructura
            xml_original = self.xml_original
            nuevo_xml = ET.Element(xml_original.getroot().tag)
            
            # Función recursiva para copiar la estructura
            def copiar_estructura(elemento_original, elemento_nuevo):
                # Copiar atributos si existen
                for nombre, valor in elemento_original.attrib.items():
                    elemento_nuevo.set(nombre, valor)
                
                # Procesar elementos hijos
                for hijo_original in elemento_original:
                    hijo_nuevo = ET.SubElement(elemento_nuevo, hijo_original.tag)
                    copiar_estructura(hijo_original, hijo_nuevo)
            
            # Copiar la estructura base del XML original
            copiar_estructura(xml_original.getroot(), nuevo_xml)
            
            # Actualizar los valores desde la tabla
            for item in self.tabla_xml.get_children():
                valores = self.tabla_xml.item(item)['values']
                ruta = self.tabla_xml.item(item)['tags'][0] if self.tabla_xml.item(item)['tags'] else None
                
                if ruta:
                    # Convertir valores a strings y crear diccionario
                    valores_dict = {col: str(val) if val is not None else "" 
                                 for col, val in zip(self.tabla_xml['columns'], valores)}
                    
                    # Actualizar los elementos correspondientes en el XML
                    partes_ruta = ruta.split('/')
                    elemento_actual = nuevo_xml
                    
                    # Navegar hasta el elemento correcto
                    for parte in partes_ruta[:-1]:
                        siguiente = elemento_actual.find(parte)
                        if siguiente is not None:
                            elemento_actual = siguiente
                        else:
                            elemento_actual = ET.SubElement(elemento_actual, parte)
                    
                    # Actualizar el valor del elemento final
                    elemento_final = elemento_actual.find(partes_ruta[-1])
                    if elemento_final is not None:
                        if valores_dict.get(partes_ruta[-1]):
                            elemento_final.text = valores_dict[partes_ruta[-1]]
                    
                    # Actualizar otros valores relacionados
                    for col, valor in valores_dict.items():
                        if valor and col != partes_ruta[-1]:
                            elemento_existente = elemento_actual.find(col)
                            if elemento_existente is not None:
                                elemento_existente.text = valor
                            else:
                                nuevo_elem = ET.SubElement(elemento_actual, col)
                                nuevo_elem.text = valor
            
            return nuevo_xml
            
        except Exception as e:
            logging.error(f"Error al generar XML: {str(e)}")
            raise

    def mover_siguiente_celda(self, event):
        """Mueve la selección a la siguiente celda"""
        current = self.tabla_xml.selection()[0] if self.tabla_xml.selection() else None
        if current:
            next_item = self.tabla_xml.next(current)
            if next_item:
                self.tabla_xml.selection_set(next_item)
                self.tabla_xml.see(next_item)
        return 'break'  # Prevenir comportamiento por defecto
        
    def mover_celda_anterior(self, event):
        """Mueve la selección a la celda anterior"""
        current = self.tabla_xml.selection()[0] if self.tabla_xml.selection() else None
        if current:
            prev_item = self.tabla_xml.prev(current)
            if prev_item:
                self.tabla_xml.selection_set(prev_item)
                self.tabla_xml.see(prev_item)
        return 'break'  # Prevenir comportamiento por defecto

    def mostrar_error(self, titulo, mensaje, detalles=None):
        """Muestra un diálogo de error con texto copiable"""
        ventana_error = tk.Toplevel(self)
        ventana_error.title(titulo)
        ventana_error.geometry("500x300")
        ventana_error.minsize(400, 200)
        
        # Frame principal
        frame_principal = ttk.Frame(ventana_error, padding="10")
        frame_principal.pack(fill=tk.BOTH, expand=True)
        
        # Ícono de error y mensaje principal
        frame_superior = ttk.Frame(frame_principal)
        frame_superior.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_superior, 
                 text="⚠️", 
                 font=(ModernoTema.FONT_FAMILY, 24)).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Label(frame_superior, 
                 text=mensaje,
                 wraplength=400,
                 font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE)).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Área de detalles con scroll
        if detalles:
            ttk.Label(frame_principal, 
                     text="Detalles del error:",
                     font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE, "bold")).pack(anchor=tk.W, pady=(0, 5))
            
            # Frame para el área de texto con borde
            frame_texto = ttk.Frame(frame_principal, style='Card.TFrame')
            frame_texto.pack(fill=tk.BOTH, expand=True)
            
            # Área de texto con scroll
            texto_error = tk.Text(frame_texto, 
                                wrap=tk.WORD, 
                                height=8,
                                font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE))
            texto_error.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(frame_texto, orient="vertical", command=texto_error.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            texto_error.configure(yscrollcommand=scrollbar.set)
            texto_error.insert("1.0", detalles)
            texto_error.configure(state="disabled")
        
        # Frame para botones
        frame_botones = ttk.Frame(frame_principal)
        frame_botones.pack(fill=tk.X, pady=(10, 0))
        
        # Botón copiar
        def copiar_error():
            texto_completo = f"{mensaje}\n\nDetalles:\n{detalles}" if detalles else mensaje
            self.clipboard_clear()
            self.clipboard_append(texto_completo)
            
        ttk.Button(frame_botones, 
                  text="Copiar", 
                  command=copiar_error,
                  style='Secondary.TButton').pack(side=tk.LEFT)
        
        ttk.Button(frame_botones, 
                  text="Cerrar", 
                  command=ventana_error.destroy,
                  style='Secondary.TButton').pack(side=tk.RIGHT)
        
        # Centrar la ventana
        ventana_error.transient(self)
        ventana_error.grab_set()
        ventana_error.update_idletasks()
        ancho = ventana_error.winfo_width()
        alto = ventana_error.winfo_height()
        x = (ventana_error.winfo_screenwidth() // 2) - (ancho // 2)
        y = (ventana_error.winfo_screenheight() // 2) - (alto // 2)
        ventana_error.geometry(f'{ancho}x{alto}+{x}+{y}')

    def obtener_etiquetas_unicas_xml(self, elemento, etiquetas=None, procesadas=None):
        """Obtiene todas las etiquetas únicas del XML manteniendo el orden de aparición"""
        if etiquetas is None:
            etiquetas = []
        if procesadas is None:
            procesadas = set()
            
        # Agregar la etiqueta actual si no ha sido procesada
        if elemento.tag not in procesadas:
            etiquetas.append(elemento.tag)
            procesadas.add(elemento.tag)
            
        # Procesar atributos si existen
        for attr in elemento.attrib:
            if attr not in procesadas:
                etiquetas.append(attr)
                procesadas.add(attr)
                
        # Procesar elementos hijos en orden
        for hijo in elemento:
            self.obtener_etiquetas_unicas_xml(hijo, etiquetas, procesadas)
            
        return etiquetas

    def set_scroll_y(self, *args):
        """Maneja el scroll vertical de manera proporcional"""
        try:
            # Obtener el número total de items y los items visibles
            total_items = len(self.tabla_xml.get_children())
            visible_items = self.tabla_xml.winfo_height() // self.tabla_xml.winfo_reqheight()
            
            if total_items > 0:
                # Calcular la proporción de items visibles respecto al total
                proportion = min(visible_items / total_items, 1.0)
                
                # Ajustar los argumentos del scrollbar
                first = float(args[0])
                last = float(args[1])
                
                # Ajustar el tamaño del "thumb" (la parte móvil del scrollbar)
                # para que sea proporcional a la cantidad de items visibles
                new_last = first + (proportion * (1.0 - first))
                
                # Aplicar los valores ajustados
                self.scrollbar_y.set(first, min(new_last, 1.0))
            else:
                self.scrollbar_y.set(*args)
                
        except Exception as e:
            logging.error(f"Error en scroll vertical: {str(e)}")
            self.scrollbar_y.set(*args)

if __name__ == "__main__":
    app = AplicacionXML()
    app.mainloop()