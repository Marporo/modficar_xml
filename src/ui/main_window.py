import os
import sys
import logging
from datetime import datetime
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QLineEdit, QComboBox, 
    QFileDialog, QMessageBox, QProgressBar, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTabWidget, QGroupBox,
    QCheckBox, QFrame, QScrollArea, QTextEdit, QCompleter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSortFilterProxyModel
from PyQt6.QtGui import QIcon

# Importar lógica del core
from core.xml_modifier import (
    modificar_xml, 
    validar_xml, 
    obtener_etiquetas_unicas, 
    obtener_valores_etiqueta
)
from ui.styles import get_main_style


class FilterableComboBox(QComboBox):
    """ComboBox avanzado con capacidades de filtrado dinámico.
    
    Utiliza un QSortFilterProxyModel para permitir búsquedas instantáneas 
    sobre una lista de origen (tags o valores XML).
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        # El Proxy Model actúa como un filtro entre los datos y la vista
        self._proxy = QSortFilterProxyModel(self)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setSourceModel(self.model())
        
        # El Completer maneja el popup de resultados filtrados
        self._completer = QCompleter(self._proxy, self)
        self._completer.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setCompleter(self._completer)
        
        # Sincronización: al escribir, filtramos el proxy en tiempo real
        self.lineEdit().textEdited.connect(self._proxy.setFilterFixedString)
        self._completer.activated.connect(self._on_completer_activated)
    
    def _on_completer_activated(self, text):
        """Sincroniza el índice del ComboBox con la selección del popup filtrado."""
        if text:
            idx = self.findText(text)
            if idx >= 0:
                self.setCurrentIndex(idx)


class ProcessingThread(QThread):
    """Hilo de ejecución asincrónico para evitar bloqueos en la GUI."""
    finished = pyqtSignal(int, list)  # (total_cambios, detalles)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, archivos, etiqueta, valor_actual, valor_nuevo, usar_regex):
        super().__init__()
        self.archivos = archivos
        self.etiqueta = etiqueta
        self.valor_actual = valor_actual
        self.valor_nuevo = valor_nuevo
        self.usar_regex = usar_regex

    def run(self):
        """Ejecuta la modificación masiva en segundo plano."""
        total_cambios = 0
        detalles = []
        try:
            for i, archivo in enumerate(self.archivos):
                cambios = modificar_xml(
                    archivo, self.etiqueta, self.valor_actual, 
                    self.valor_nuevo, usar_regex=self.usar_regex
                )
                total_cambios += cambios
                detalles.append({'archivo': os.path.basename(archivo), 'cambios': cambios})
                self.progress.emit(int(((i + 1) / len(self.archivos)) * 100))
            
            self.finished.emit(total_cambios, detalles)
        except Exception as e:
            self.error.emit(str(e))


class XMLModifierApp(QMainWindow):
    """Controlador principal de la interfaz XML Modifier Pro."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("XML Modifier Pro")
        self.setMinimumSize(900, 750)
        
        # Configuración de recursos (macOS / Desarrollo)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.resources_dir = os.path.join(base_path, 'resources')
        self.setStyleSheet(get_main_style(self.resources_dir))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Inicializa el layout principal y las pestañas."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        header_label = QLabel("XML Modifier Pro")
        header_label.setObjectName("Title")
        main_layout.addWidget(header_label)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Módulos de Pestañas
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "Modificación")
        
        self.history_tab = QWidget()
        self.setup_history_tab()
        self.tabs.addTab(self.history_tab, "Historial")

        self.guide_tab = QWidget()
        self.setup_guide_tab()
        self.tabs.addTab(self.guide_tab, "Guía de Uso")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Listo.")
        self.status_label.setStyleSheet("color: #86868B; font-size: 11px;")
        main_layout.addWidget(self.status_label)

    def setup_main_tab(self):
        """Sección de configuración de la modificación XML."""
        layout = QVBoxLayout(self.main_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Grupo Origen
        src_group = QGroupBox("Origen de Datos")
        src_layout = QVBoxLayout(src_group)
        
        toggle_layout = QHBoxLayout()
        self.single_mode_radio = QPushButton("Archivo Único")
        self.single_mode_radio.setCheckable(True)
        self.single_mode_radio.setChecked(True)
        self.multi_mode_radio = QPushButton("Múltiples Archivos")
        self.multi_mode_radio.setCheckable(True)
        
        self.single_mode_radio.clicked.connect(self.toggle_mode)
        self.multi_mode_radio.clicked.connect(self.toggle_mode)
        
        toggle_layout.addWidget(self.single_mode_radio)
        toggle_layout.addWidget(self.multi_mode_radio)
        src_layout.addLayout(toggle_layout)
        
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Seleccione archivo o carpeta...")
        self.btn_browse = QPushButton("Buscar")
        self.btn_browse.clicked.connect(self.browse_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.btn_browse)
        src_layout.addLayout(path_layout)
        layout.addWidget(src_group)
        
        # Grupo Modificación
        mod_group = QGroupBox("Configuración de Modificación")
        mod_layout = QVBoxLayout(mod_group)
        
        mod_layout.addWidget(QLabel("Etiqueta XML:"))
        self.tag_combo = FilterableComboBox()
        self.tag_combo.currentTextChanged.connect(self.update_values_list)
        mod_layout.addWidget(self.tag_combo)
        
        help_row = QHBoxLayout()
        help_row.addWidget(QLabel("Valor Actual:"))
        self.btn_help = QPushButton("?")
        self.btn_help.setObjectName("HelpButton")
        self.btn_help.clicked.connect(self.show_todos_help)
        help_row.addWidget(self.btn_help)
        self.regex_check = QCheckBox("Modo Regex")
        help_row.addWidget(self.regex_check)
        help_row.addStretch()
        mod_layout.addLayout(help_row)
        
        self.value_old_combo = FilterableComboBox()
        mod_layout.addWidget(self.value_old_combo)
        
        mod_layout.addWidget(QLabel("Nuevo Valor:"))
        self.value_new_input = QLineEdit()
        mod_layout.addWidget(self.value_new_input)
        layout.addWidget(mod_group)
        
        actions = QHBoxLayout()
        self.btn_preview = QPushButton("Vista Previa")
        self.btn_preview.clicked.connect(self.show_preview)
        self.btn_execute = QPushButton("Procesar y Guardar")
        self.btn_execute.setObjectName("AccentButton")
        self.btn_execute.clicked.connect(self.start_processing)
        actions.addWidget(self.btn_preview)
        actions.addWidget(self.btn_execute)
        layout.addLayout(actions)
        
        self.preview_panel = QTextEdit()
        self.preview_panel.setObjectName("PreviewPanel")
        self.preview_panel.setReadOnly(True)
        self.preview_panel.setMaximumHeight(140)
        layout.addWidget(self.preview_panel)

    def setup_history_tab(self):
        """Panel de historial de cambios."""
        layout = QVBoxLayout(self.history_tab)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(["FECHA", "ARCHIVO", "ETIQUETA", "RESUMEN"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.verticalHeader().setVisible(False)
        self.history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.history_table.setShowGrid(True)
        layout.addWidget(self.history_table)

    def setup_guide_tab(self):
        """Construye el manual de usuario interactivo con CSS inline."""
        layout = QVBoxLayout(self.guide_tab)
        self.guide_text = QTextEdit()
        self.guide_text.setObjectName("GuideText")
        self.guide_text.setReadOnly(True)
        
        ts = "border-collapse: separate; border-spacing: 0; width: 100%; border: 1px solid #E0E0E0; border-radius: 8px; margin: 10px 0 20px 0;"
        ths = "text-align: left; color: #86868B; font-size: 11px; text-transform: uppercase; padding: 10px 14px; border-bottom: 1px solid #E0E0E0;"
        tds = "padding: 10px 14px; border-bottom: 1px solid #F0F0F0; font-size: 13px; color: #1D1D1F;"
        cs = "padding: 2px 4px; font-family: Menlo, monospace; font-size: 12px; color: #0071E3;"
        
        def c(text): return f'<code style="{cs}">{text}</code>'
        def row(cells, alt=False):
            bg = "#FAFAFA" if alt else "white"
            return f'<tr style="background-color: {bg};">' + "".join([f'<td style="{tds}">{x}</td>' for x in cells]) + '</tr>'
        def h(cells): return '<tr>' + "".join([f'<th style="{ths}">{x}</th>' for x in cells]) + '</tr>'
        
        html = [
            '<div style="padding: 15px; font-family: Helvetica Neue; line-height: 1.6; background-color: white;">',
            '<h1 style="color: #0071E3; font-size: 24px;">Manual de Usuario XML Modifier Pro</h1>',
            '<h3 style="color: #1D1D1F;">1. Uso de [TODOS]</h3>',
            '<p>Esta opción permite sobreescribir el valor de la etiqueta seleccionada en todos los casos encontrados, sin importar el contenido previo.</p>',
            '<h3 style="color: #1D1D1F;">2. Referencia de Expresiones Regulares (Regex)</h3>',
            f'<table style="{ts}">',
            h(["Patrón", "Descripción", "Ejemplo"]),
            row([c("."), "Cualquier carácter", "c.t (cat, cot)"]),
            row([c("\\\\d"), "Dígito numérico", "123"], True),
            row([c("+"), "Una o más repeticiones", "abc+"], False),
            row([c("^ / $"), "Inicio / Fin de texto", "^INV"], True),
            '</table>',
            '<p>Utilice estas expresiones activando la casilla <b>Modo Regex</b> para búsquedas inteligentes.</p>',
            '</div>'
        ]
        self.guide_text.setHtml("".join(html))
        layout.addWidget(self.guide_text)

    # -- Handlers de Eventos --

    def browse_path(self):
        """Selector de archivos/carpetas nativo."""
        if self.single_mode_radio.isChecked():
            path, _ = QFileDialog.getOpenFileName(self, "Seleccionar XML", "", "XML files (*.xml)")
        else:
            path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        
        if path:
            self.path_input.setText(path)
            self.update_tags_list()

    def update_tags_list(self):
        """Carga los tags disponibles desde el origen seleccionado."""
        path = self.path_input.text()
        if not path: return
        try:
            etiquetas = set()
            if os.path.isfile(path):
                etiquetas = obtener_etiquetas_unicas(path)
            else:
                for f in os.listdir(path):
                    if f.endswith('.xml'):
                        etiquetas.update(obtener_etiquetas_unicas(os.path.join(path, f)))
            self.tag_combo.clear()
            self.tag_combo.addItems(sorted(list(etiquetas)))
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))

    def update_values_list(self, tag):
        """Carga los valores actuales para el tag seleccionado."""
        path = self.path_input.text()
        if not path or not tag: return
        try:
            valores = set()
            if os.path.isfile(path):
                valores = obtener_valores_etiqueta(path, tag)
            else:
                for f in os.listdir(path):
                    if f.endswith('.xml'):
                        valores.update(obtener_valores_etiqueta(os.path.join(path, f), tag))
            
            lista = sorted(list(valores))
            lista.insert(0, "[TODOS]")
            self.value_old_combo.clear()
            self.value_old_combo.addItems(lista)
        except Exception: pass

    def show_preview(self):
        """Muestra resumen de la operación sin aplicar cambios."""
        tag, v_old, v_new = self.tag_combo.currentText(), self.value_old_combo.currentText(), self.value_new_input.text()
        if not all([tag, v_old, v_new]): return
        
        path = self.path_input.text()
        archivos = [path] if os.path.isfile(path) else [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.xml')]
        
        total = sum([modificar_xml(a, tag, v_old, v_new, preview=True, usar_regex=self.regex_check.isChecked()) for a in archivos])
        self.preview_panel.setHtml(f"<b>Vista Previa:</b> Se detectaron {total} coincidencias en {len(archivos)} archivos.")

    def start_processing(self):
        """Ejecuta la modificación masiva."""
        tag, v_old, v_new = self.tag_combo.currentText(), self.value_old_combo.currentText(), self.value_new_input.text()
        path = self.path_input.text()
        if not all([tag, v_old, v_new, path]): return
        
        archivos = [path] if os.path.isfile(path) else [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.xml')]
        
        self.btn_execute.setEnabled(False)
        self.progress_bar.setVisible(True)
        
        self.thread = ProcessingThread(archivos, tag, v_old, v_new, self.regex_check.isChecked())
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.finished.connect(self.on_processing_finished)
        self.thread.error.connect(self.on_processing_error)
        self.thread.start()

    def on_processing_finished(self, total, detalles):
        """Callback de éxito."""
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.information(self, "Éxito", f"Procesamiento finalizado con {total} cambios.")
        
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        for d in detalles:
            row_idx = self.history_table.rowCount()
            self.history_table.insertRow(row_idx)
            self.history_table.setItem(row_idx, 0, QTableWidgetItem(fecha))
            self.history_table.setItem(row_idx, 1, QTableWidgetItem(d['archivo']))
            self.history_table.setItem(row_idx, 2, QTableWidgetItem(self.tag_combo.currentText()))
            self.history_table.setItem(row_idx, 3, QTableWidgetItem(f"{d['cambios']} cambios"))

    def on_processing_error(self, err):
        """Callback de error."""
        self.btn_execute.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Error", err)

    def show_todos_help(self):
        """Muestra ayuda sobre la función [TODOS]."""
        QMessageBox.information(self, "Ayuda: [TODOS]", 
            "Al seleccionar [TODOS], el programa reemplazará CUALQUIER valor de la etiqueta seleccionada por el nuevo valor.")

    def toggle_mode(self):
        """Intercambia entre modo Archivo Único y Carpeta."""
        is_single = (self.sender() == self.single_mode_radio)
        self.single_mode_radio.setChecked(is_single)
        self.multi_mode_radio.setChecked(not is_single)
        self.path_input.clear()
        self.path_input.setPlaceholderText("Seleccione archivo XML..." if is_single else "Seleccione carpeta...")
