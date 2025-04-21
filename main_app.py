# main_app.py - Archivo principal que integra todo

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import ctypes

# Importar nuestros propios módulos
from xml_modifier import modificar_xml
from ui_theme import ModernoTema

# Hacer que la aplicación sea consciente de la alta resolución (DPI-aware) en Windows
if sys.platform.startswith('win'):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

class AplicacionXML(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Modificador de XML")
        self.geometry("650x550")
        self.configure(bg=ModernoTema.BG_COLOR)
        self.resizable(True, True)
        
        # Configurar el estilo moderno
        ModernoTema.configurar_estilo()
        
        # Variables
        self.archivo_seleccionado = tk.StringVar()
        self.etiqueta = tk.StringVar()
        self.valor_actual = tk.StringVar()
        self.valor_nuevo = tk.StringVar()
        
        # Crear widgets
        self.crear_widgets()
        
        # Centrar ventana
        self.center_window()
        
    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def crear_widgets(self):
        # Frame principal con padding
        main_frame = ttk.Frame(self, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Título
        titulo = ttk.Label(main_frame, text="Modificador de XML", style='Title.TLabel')
        titulo.pack(pady=(0, 25))
        
        # Contenedor para los campos
        campos_frame = ttk.Frame(main_frame)
        campos_frame.pack(fill=tk.X, pady=10)
        
        # Selección de archivo
        archivo_frame = ttk.Frame(campos_frame)
        archivo_frame.pack(fill=tk.X, pady=10)
        
        archivo_label = ttk.Label(archivo_frame, text="Archivo XML:")
        archivo_label.pack(anchor=tk.W, pady=(0, 5))
        
        archivo_busqueda_frame = ttk.Frame(archivo_frame)
        archivo_busqueda_frame.pack(fill=tk.X)
        
        archivo_entry = ttk.Entry(archivo_busqueda_frame, textvariable=self.archivo_seleccionado, width=50)
        archivo_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        buscar_btn = ttk.Button(archivo_busqueda_frame, text="Buscar", command=self.buscar_archivo, style='Secondary.TButton', width=10)
        buscar_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=5)
        
        # Etiqueta a buscar
        etiqueta_frame = ttk.Frame(campos_frame)
        etiqueta_frame.pack(fill=tk.X, pady=10)
        
        etiqueta_label = ttk.Label(etiqueta_frame, text="Etiqueta a buscar:")
        etiqueta_label.pack(anchor=tk.W, pady=(0, 5))
        
        etiqueta_entry = ttk.Entry(etiqueta_frame, textvariable=self.etiqueta)
        etiqueta_entry.pack(fill=tk.X, ipady=5)
        
        # Valor actual
        valor_actual_frame = ttk.Frame(campos_frame)
        valor_actual_frame.pack(fill=tk.X, pady=10)
        
        valor_actual_label = ttk.Label(valor_actual_frame, text="Valor actual:")
        valor_actual_label.pack(anchor=tk.W, pady=(0, 5))
        
        valor_actual_entry = ttk.Entry(valor_actual_frame, textvariable=self.valor_actual)
        valor_actual_entry.pack(fill=tk.X, ipady=5)
        
        # Valor nuevo
        valor_nuevo_frame = ttk.Frame(campos_frame)
        valor_nuevo_frame.pack(fill=tk.X, pady=10)
        
        valor_nuevo_label = ttk.Label(valor_nuevo_frame, text="Valor nuevo:")
        valor_nuevo_label.pack(anchor=tk.W, pady=(0, 5))
        
        valor_nuevo_entry = ttk.Entry(valor_nuevo_frame, textvariable=self.valor_nuevo)
        valor_nuevo_entry.pack(fill=tk.X, ipady=5)
        
        # Botón de ejecución
        boton_frame = ttk.Frame(main_frame)
        boton_frame.pack(fill=tk.X, pady=20)
        
        ejecutar_btn = ttk.Button(
            boton_frame, 
            text="Modificar XML", 
            command=self.ejecutar_modificacion, 
            style='Accent.TButton',
            width=20
        )
        ejecutar_btn.pack(pady=5, ipady=8)
        
        # Área de estado/log con borde
        log_frame = ttk.Frame(main_frame, relief="solid", borderwidth=1)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Título del log
        log_title = ttk.Label(log_frame, text="Resultados", background="white")
        log_title.pack(anchor=tk.W, padx=10, pady=5)
        
        # Separador
        separator = ttk.Separator(log_frame, orient='horizontal')
        separator.pack(fill=tk.X)
        
        # Área de texto
        self.log_text = tk.Text(log_frame, height=5, borderwidth=0, bg="white", 
                              font=(ModernoTema.FONT_FAMILY, ModernoTema.FONT_SIZE))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.log_text.insert(tk.END, "Listo para procesar archivos XML.")
        self.log_text.config(state=tk.DISABLED)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        version_label = ttk.Label(footer_frame, text="v1.0", foreground="#999999")
        version_label.pack(side=tk.RIGHT)
    
    def buscar_archivo(self):
        archivo = filedialog.askopenfilename(filetypes=[("Archivos XML", "*.xml"), ("Todos los archivos", "*.*")])
        if archivo:
            self.archivo_seleccionado.set(archivo)
            self.actualizar_log(f"Archivo seleccionado: {os.path.basename(archivo)}")
    
    def actualizar_log(self, mensaje):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, mensaje)
        self.log_text.config(state=tk.DISABLED)
    
    def ejecutar_modificacion(self):
        archivo = self.archivo_seleccionado.get()
        etiqueta = self.etiqueta.get()
        valor_actual = self.valor_actual.get()
        valor_nuevo = self.valor_nuevo.get()
        
        # Validar campos
        if not archivo:
            messagebox.showerror("Error", "Debe seleccionar un archivo XML.")
            return
        if not etiqueta:
            messagebox.showerror("Error", "Debe ingresar una etiqueta a buscar.")
            return
        if not valor_actual:
            messagebox.showerror("Error", "Debe ingresar el valor actual a reemplazar.")
            return
        if not valor_nuevo:
            messagebox.showerror("Error", "Debe ingresar el nuevo valor.")
            return
            
        try:
            cambios = modificar_xml(archivo, etiqueta, valor_actual, valor_nuevo)
            if cambios > 0:
                mensaje = f"✅ Se realizaron {cambios} cambios en el archivo."
                self.actualizar_log(mensaje)
                messagebox.showinfo("Éxito", f"Se realizaron {cambios} cambios en el archivo.")
            else:
                mensaje = f"ℹ️ No se encontraron instancias de '{valor_actual}' en la etiqueta '{etiqueta}'."
                self.actualizar_log(mensaje)
                messagebox.showinfo("Información", f"No se encontraron instancias de '{valor_actual}' en la etiqueta '{etiqueta}'.")
        except Exception as e:
            mensaje = f"❌ Error: {str(e)}"
            self.actualizar_log(mensaje)
            messagebox.showerror("Error", f"Ha ocurrido un error: {str(e)}")

if __name__ == "__main__":
    app = AplicacionXML()
    app.mainloop()