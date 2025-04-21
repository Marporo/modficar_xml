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
        
        # Agregar pestañas al notebook
        self.notebook.add(self.pestaña_principal, text="Modificar XML")
        self.notebook.add(self.pestaña_historial, text="Historial")
        
        # Configurar cada pestaña
        self.configurar_pestaña_principal()
        self.configurar_pestaña_historial()
        
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

if __name__ == "__main__":
    app = AplicacionXML()
    app.mainloop()