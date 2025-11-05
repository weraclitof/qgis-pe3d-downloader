# PE3D Downloader v1.0.0

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![QGIS Version](https://img.shields.io/badge/QGIS-3.16%2B-brightgreen)
![Python Version](https://img.shields.io/badge/Python-3.9%2B-blue)

**Português (Brasil)** | [English](#english-readme)

Este complemento para QGIS automatiza o download, descompactação e carregamento de dados do portal **Pernambuco Tridimensional (PE3D)**.

## 📖 Descrição

O portal PE3D é um recurso essencial para o geoprocessamento em Pernambuco. No entanto, o processo de download manual de dados (MDT, MDE, Ortoimagens) pode ser um trabalho intensivo, especialmente para municípios grandes que exigem o download de dezenas ou centenas de quadrículas.

Este plugin foi criado para resolver esse problema, automatizando todo o fluxo de trabalho:
1.  Autentica-se de forma segura no portal.
2.  Busca a lista completa de municípios de PE.
3.  Permite ao usuário selecionar um município e o tipo de dado.
4.  Baixa **todos** os arquivos `.zip` correspondentes de forma otimizada.
5.  Pergunta ao usuário e, se autorizado, **descompacta e carrega automaticamente** todas as camadas raster no QGIS.

Este projeto transforma a tarefa de um processo de muitos a poucos minutos.

## ✨ Funcionalidades Principais (v1.0.0)

* **Login Seguro:** Autenticação direta na interface (credenciais não são salvas).
* **Seleção por Município:** Menu suspenso com a lista completa dos 185 municípios de Pernambuco.
* **Download Otimizado:** Utiliza um pool de threads (`QThreadPool`) para baixar até 4 arquivos simultaneamente, acelerando drasticamente o download em municípios grandes.
* **Interface Responsiva:** O QGIS não trava! O download ocorre em segundo plano com uma barra de progresso e status em tempo real.
* **Auto-Carregamento:** Descompacta os arquivos `.zip` e carrega as camadas `.tif`/`.tiff` diretamente no painel de camadas do QGIS.

## 🚀 Instalação

1.  Baixe o arquivo `PE3D_Downloader_v1.0.0.zip` da seção [Releases](https://github.com/weraclitof/qgis-pe3d-downloader/releases/tag/1.0.0)
2.  Abra o QGIS.
3.  Vá em `Complementos > Gerenciar e Instalar Complementos...`.
4.  Selecione **"Instalar a partir de um ZIP"**.
5.  Navegue até o arquivo `.zip` baixado e clique em "Instalar Complemento".
6.  Um novo ícone aparecerá na sua barra de ferramentas.

## 🧭 Guia de Uso

1.  Clique no ícone do **PE3D Downloader**.
2.  Aguarde o carregamento da lista de municípios.
3.  Preencha seu **Email**, **Senha** e o código **CAPTCHA**.
4.  Selecione o **Tipo de arquivo** (ex: "Modelo Digital de Terreno (RASTER)").
5.  Selecione o **Município** na caixa "Localização".
6.  Clique em **"Baixar e carregar"**.
7.  Escolha uma pasta no seu computador para salvar os arquivos.
8.  Acompanhe o progresso. Ao final, o plugin perguntará se você deseja carregar as camadas.
9.  Clique em "Sim" para que os arquivos sejam descompactados e adicionados ao seu projeto.

## 👨‍💻 Autor

* **Weverton Heraclito**

---

## (English README)

# PE3D Downloader v1.0.0

This QGIS plugin automates the download, extraction, and loading of geospatial data from the **PE3D (Pernambuco Tridimensional)** platform.

## 📖 Description

The PE3D portal is an essential resource for geoprocessing in the state of Pernambuco, Brazil. However, the manual process of downloading data (DEM, DSM, Orthoimagery) can be extremely time-consuming, especially for large municipalities that require downloading hundreds of individual tiles.

This plugin was created to solve this problem by automating the entire workflow:
1.  Securely authenticates with the portal.
2.  Fetches the complete list of municipalities.
3.  Allows the user to select a municipality and data type.
4.  Downloads **all** corresponding `.zip` files using an optimized process.
5.  Upon user confirmation, **automatically extracts and loads** all raster layers into QGIS.

This project turns a task of hours into a process of minutes.

## ✨ Key Features (v1.0.0)

* **Secure Login:** Authenticate directly within the interface (credentials are not saved).
* **Municipality Selection:** A drop-down menu populated with all 185 municipalities in Pernambuco.
* **Optimized Downloading:** Uses a `QThreadPool` to download up to 4 files in parallel, dramatically speeding up downloads for large areas.
* **Responsive UI:** The QGIS interface **does not freeze**! Downloads run in the background with a real-time progress bar and status updates.
* **Auto-Load:** Automatically unzips downloaded files and loads the `.tif`/`.tiff` layers directly into the QGIS project.

## 🚀 Installation

1.  Download the `PE3D_Downloader_v1.0.0.zip` file from the [Releases](https://github.com/weraclitof/qgis-pe3d-downloader/releases/tag/1.0.0) section.
2.  Open QGIS.
3.  Go to `Plugins > Manage and Install Plugins...`.
4.  Select **"Install from ZIP"**.
5.  Browse to the downloaded `.zip` file and click "Install Plugin".
6.  A new icon will appear in your plugin toolbar.

## 🧭 How to Use

1.  Click the **PE3D Downloader** icon.
2.  Wait for the municipality list to load.
3.  Enter your **Email**, **Password**, and the **CAPTCHA** code.
4.  Select the **"Tipo de arquivo"** (File Type) you want.
5.  Select the desired **municipality** from the "Localização" (Location) box.
6.  Click **"Baixar e carregar"** (Download and Load).
7.  Choose a folder on your computer to save the files.
8.  Track the progress. When finished, the plugin will ask if you want to load the layers.
9.  Click "Yes" to have the files unzipped and added to your project.
