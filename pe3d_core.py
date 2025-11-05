# -*- coding: utf-8 -*-

import os
import json
import requests
import urllib.parse
import zipfile
from qgis.PyQt.QtWidgets import QDialog, QApplication, QFileDialog, QMessageBox
from qgis.PyQt.QtGui import QPixmap
from qgis.PyQt.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal
from qgis.core import Qgis, QgsMessageLog

from .pe3d_downloader_dialog_base import Ui_PE3DDownloaderDialogBase

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

BASE_URL = "https://pe3d.pe.gov.br/"
MAP_PAGE_URL = BASE_URL + "mapa.php"
LOGIN_URL = BASE_URL + "login.php"
DOWNLOAD_URL = BASE_URL + "baixararquivo.php"
CAPTCHA_URL = BASE_URL + "get_captcha.php"
MUNICIPIOS_JSON_URL = BASE_URL + "estados_pe.json"
DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0'}

class TaskSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

class DownloadTask(QRunnable):
    def __init__(self, session, url, save_path):
        super(DownloadTask, self).__init__()
        self.session = session
        self.url = url
        self.save_path = save_path
        self.signals = TaskSignals()

    def run(self):
        try:
            file_response = self.session.get(self.url, verify=False, stream=True, timeout=300)
            if file_response.status_code == 200:
                with open(self.save_path, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.signals.finished.emit(self.save_path)
            else:
                self.signals.error.emit(f"Falha ao baixar {self.url}. Status: {file_response.status_code}")
        except Exception as e:
            self.signals.error.emit(f"Erro crítico ao baixar de {self.url}: {e}")

# Classe da Janela Principal (UI)
class PE3DDownloaderDialog(QDialog, Ui_PE3DDownloaderDialogBase):
    def __init__(self, iface, parent=None):
        super(PE3DDownloaderDialog, self).__init__(parent)
        self.setupUi(self)
        self.iface = iface

        self.session = requests.Session()
        self.municipios_data = None
        self.populate_static_comboboxes()
        self.prime_session()
        self.connect_signals()
        self.fetch_initial_data()
        self.load_captcha()

        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(4)
        QgsMessageLog.logMessage(f"Pool de downloads configurado para até {self.threadpool.maxThreadCount()} tarefas paralelas.", "PE3D", Qgis.Info)

    def populate_static_comboboxes(self):
        self.fileTypeComboBox.clear();
        file_types = ['1;Ortoimagem', '2;Modelo Digital de Elevação (RASTER)','3;Modelo Digital de Elevação (XYZI)', '4;Modelo Digital de Terreno (RASTER)','5;Modelo Digital de Terreno (XYZ)', '6;Intensidade-Hipsometria']
        self.fileTypeComboBox.addItems([ft.split(';')[1] for ft in file_types]); self.file_type_data = file_types
    def fetch_initial_data(self):
        self.statusTextEdit.setText("Carregando lista de municípios..."); self.locationComboBox.setEnabled(False)
        try:
            response_mun = self.session.get(MUNICIPIOS_JSON_URL, verify=False, headers=DEFAULT_HEADERS)
            self.municipios_data = response_mun.json()
            municipality_names = sorted([feature['properties']['name'] for feature in self.municipios_data['features']])
            self.locationComboBox.clear(); self.locationComboBox.addItems(municipality_names)
            self.locationComboBox.setEnabled(True); self.statusTextEdit.setText("Aguardando credenciais.")
        except: self.statusTextEdit.setText("Erro ao carregar lista de municípios.")
    def prime_session(self):
        try: self.session.get(BASE_URL, headers=DEFAULT_HEADERS, verify=False, timeout=15)
        except: self.statusTextEdit.setText("Erro de conexão inicial.")
    def connect_signals(self):
        self.reloadCaptchaButton.clicked.connect(self.load_captcha)
        self.pushButton_2.clicked.connect(self.start_download_process)
    def load_captcha(self):
        self.statusTextEdit.setText("Carregando CAPTCHA..."); QApplication.processEvents()
        try:
            response = self.session.get(CAPTCHA_URL, headers=DEFAULT_HEADERS, verify=False, timeout=15)
            if response.status_code == 200: pixmap = QPixmap(); pixmap.loadFromData(response.content); self.captchaLabel.setPixmap(pixmap)
        except: self.statusTextEdit.setText("Erro de conexão ao carregar CAPTCHA.")
        
    def start_download_process(self):
        user_email = self.emailLineEdit.text(); user_password = self.passwordLineEdit.text(); user_captcha = self.captchaLineEdit.text()
        if not all([user_email, user_password, user_captcha]): self.statusTextEdit.setText("Erro: Preencha todos os campos."); return
        self.statusTextEdit.setText("Autenticando..."); QApplication.processEvents()
        login_payload = {'tela': 'login', 'usuario': user_email, 'senha': user_password, 'captcha': user_captcha}
        login_headers = {**DEFAULT_HEADERS, 'Referer': MAP_PAGE_URL, 'X-Requested-With': 'XMLHttpRequest', 'Origin': BASE_URL.rstrip('/')}
        try:
            response = self.session.post(LOGIN_URL, data=login_payload, headers=login_headers, verify=False, timeout=15)
            if response.status_code == 200 and response.text.strip() == 'ok':
                self.statusTextEdit.setText("Login bem-sucedido!"); QApplication.processEvents(); self.initiate_download()
            else: self.statusTextEdit.setText("Falha no login."); self.load_captcha()
        except: self.statusTextEdit.setText("Erro de conexão no login.")
        
    def initiate_download(self):
        location_name = self.locationComboBox.currentText(); file_type_code = next((ft.split(';')[0] for ft in self.file_type_data if ft.endswith(self.fileTypeComboBox.currentText())), None)
        self.statusTextEdit.setText(f"Obtendo lista de arquivos para '{location_name}'..."); QApplication.processEvents()
        
        encoded_location = urllib.parse.quote_plus(location_name)
        payload_string = f"tipo={file_type_code}&id%5B%5D={encoded_location}&id%5B%5D=&mun_quad=muni&timeout=5000"
        list_headers = {**DEFAULT_HEADERS, 'Referer': MAP_PAGE_URL,'X-Requested-With': 'XMLHttpRequest','Origin': BASE_URL.rstrip('/'),'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
        
        try:
            response_html = self.session.post(DOWNLOAD_URL, data=payload_string, headers=list_headers, verify=False, timeout=30)
            urls_to_download = []
            if response_html.status_code == 200 and '<iframe' in response_html.text:
                lines = response_html.text.split("src='");
                for line in lines[1:]: urls_to_download.append(line.split("'")[0])
            
            if not urls_to_download:
                self.statusTextEdit.setText(f"Nenhum arquivo disponível."); return

            save_dir = QFileDialog.getExistingDirectory(self, "Selecione a Pasta para Salvar os Arquivos")
            if not save_dir: self.statusTextEdit.setText("Download cancelado."); return

            # --- QThreadPool ---
            self.pushButton_2.setEnabled(False)
            self.progressBar.setValue(0)
            self.files_to_download_count = len(urls_to_download)
            self.files_downloaded_count = 0
            self.successfully_downloaded_paths = []

            for url in urls_to_download:
                filename = url.split('/')[-1]
                save_path = os.path.join(save_dir, filename)
                task = DownloadTask(self.session, url, save_path)
                task.signals.finished.connect(self.on_file_finished)
                task.signals.error.connect(lambda msg: QgsMessageLog.logMessage(msg, "PE3D", Qgis.Warning))
                self.threadpool.start(task)

        except: self.statusTextEdit.setText("Erro ao obter lista de links.")

    def on_file_finished(self, save_path):
        self.files_downloaded_count += 1
        self.successfully_downloaded_paths.append(save_path)
        
        progress_percent = int((self.files_downloaded_count / self.files_to_download_count) * 100)
        self.progressBar.setValue(progress_percent)
        self.statusTextEdit.setText(f"Baixado {self.files_downloaded_count}/{self.files_to_download_count}: {os.path.basename(save_path)}")
        
        if self.files_downloaded_count == self.files_to_download_count:
            self.on_all_downloads_finished()

    def on_all_downloads_finished(self):
        self.statusTextEdit.setText("Download concluído!")
        self.pushButton_2.setEnabled(True)
        
        reply = QMessageBox.question(self, 'Download Concluído',
                                     f"{len(self.successfully_downloaded_paths)} arquivo(s) baixado(s).\nDeseja carregar as camadas no QGIS?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            self.load_downloaded_layers(self.successfully_downloaded_paths)

    def load_downloaded_layers(self, zip_files):
        self.statusTextEdit.setText("Descompactando e carregando camadas..."); QApplication.processEvents()
        loaded_count = 0
        for zip_path in zip_files:
            try:
                extract_dir = os.path.dirname(zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                    raster_file = next((name for name in zip_ref.namelist() if name.lower().endswith(('.tif', '.tiff'))), None)
                    if raster_file:
                        raster_path = os.path.join(extract_dir, raster_file)
                        layer_name = os.path.splitext(os.path.basename(raster_file))[0]
                        self.iface.addRasterLayer(raster_path, layer_name)
                        loaded_count += 1
            except Exception as e:
                QgsMessageLog.logMessage(f"Falha ao processar {zip_path}: {e}", "PE3D", Qgis.Critical)
        self.statusTextEdit.setText(f"{loaded_count} camada(s) carregada(s) no projeto!")

    def closeEvent(self, event):
        self.threadpool.clear()
        self.threadpool.waitForDone(-1)
        event.accept()

# Classe Principal do Plugin
class PE3DDownloader:
    def __init__(self, iface):
        self.iface = iface; self.plugin_dir = os.path.dirname(__file__); self.actions = []; self.menu = u"PE3D Downloader"; self.toolbar = self.iface.addToolBar(u"PE3DDownloader"); self.toolbar.setObjectName(u"PE3DDownloader"); self.dlg = None
    def add_action(self, icon_path, text, callback, parent=None):
        from qgis.PyQt.QtGui import QIcon; from qgis.PyQt.QtWidgets import QAction
        icon = QIcon(icon_path); action = QAction(icon, text, parent); action.triggered.connect(callback); self.toolbar.addAction(action); self.iface.addPluginToMenu(self.menu, action); self.actions.append(action); return action
    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png'); self.add_action(icon_path, text=u"Executar PE3D Downloader", callback=self.run, parent=self.iface.mainWindow())
    def unload(self):
        for action in self.actions: self.iface.removePluginMenu(u"&PE3D Downloader", action); self.iface.removeToolBarIcon(action)
        del self.toolbar
    def run(self):
        if not hasattr(self, 'dlg') or not self.dlg: self.dlg = PE3DDownloaderDialog(self.iface)
        self.dlg.show(); self.dlg.activateWindow()