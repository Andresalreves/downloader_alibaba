import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import sys
import re
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def set_app_icon():
    icon_path = resource_path("logo.png")  # Cambia esto a la ruta de tu imagen PNG
    if os.path.exists(icon_path):
        icon = Image.open(icon_path)
        icon = icon.resize((32, 32), Image.Resampling.LANCZOS)  # Redimensiona si es necesario
        photo = ImageTk.PhotoImage(icon)
        root.wm_iconphoto(True, photo)
    else:
        print("Archivo de icono no encontrado.")

def log_message(message):
    status_area.insert(tk.END, message + "\n")
    status_area.see(tk.END)
    root.update()

def download_alibaba_content(url, save_folder):
    log_message(f"Iniciando descarga desde: {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    title = soup.title.string if soup.title else 'alibaba_product'
    product_name = re.sub(r'[^\w\-_\. ]', '_', title)
    
    product_folder = os.path.join(save_folder, product_name)
    os.makedirs(product_folder, exist_ok=True)
    log_message(f"Carpeta creada: {product_folder}")
    
    video_url = None
    for script in soup.find_all('script'):
        if 'videoUrl' in script.text:
            match = re.search(r'"videoUrl":"(.*?)"', script.text)
            if match:
                video_url = match.group(1)
                break
    
    if video_url:
        video_response = requests.get(video_url)
        video_filename = os.path.join(product_folder, f"{product_name}.mp4")
        with open(video_filename, 'wb') as f:
            f.write(video_response.content)
        log_message(f"Video descargado: {video_filename}")
    else:
        log_message("No se encontró video para descargar.")
    
    """images = soup.find_all('img', {'src': re.compile(r'.*\.jpg')})
    for i, img in enumerate(images):
        img_url = img['src']
        if not img_url.startswith('http'):
            img_url = 'https:' + img_url
        img_response = requests.get(img_url)
        img_filename = os.path.join(product_folder, f"{product_name}_image_{i+1}.jpg")
        with open(img_filename, 'wb') as f:
            f.write(img_response.content)
        log_message(f"Imagen descargada: {img_filename}")"""
    
    log_message(f"Descarga completada. Contenido guardado en: {product_folder}")
    messagebox.showinfo("Descarga completada", f"Contenido descargado en la carpeta:\n{product_folder}")


def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)

def start_download():
    url = url_entry.get()
    save_folder = folder_entry.get()
    
    if not url or not save_folder:
        messagebox.showerror("Error", "Por favor, ingrese la URL y seleccione una carpeta de destino.")
        return
    
    download_alibaba_content(url, save_folder)

# Crear la ventana principal
root = tk.Tk()
root.title("Alibaba Downloader")  # Título de la ventana

# Configurar el icono de la aplicación
set_app_icon()

root.geometry("666x400")

# Frame para entradas y botones
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

# URL
url_label = tk.Label(input_frame, text="URL del producto:")
url_label.grid(row=0, column=0, sticky="e")
url_entry = tk.Entry(input_frame, width=50)
url_entry.grid(row=0, column=1, padx=5)

# Carpeta de destino
folder_label = tk.Label(input_frame, text="Carpeta de destino:")
folder_label.grid(row=1, column=0, sticky="e")
folder_entry = tk.Entry(input_frame, width=50)
folder_entry.grid(row=1, column=1, padx=5)
folder_button = tk.Button(input_frame, text="Seleccionar", command=select_folder)
folder_button.grid(row=1, column=2)

# Botón de descarga
download_button = tk.Button(input_frame, text="Descargar", command=start_download)
download_button.grid(row=2, column=1, pady=10)

# Área de estado
status_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=15)
status_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

root.mainloop()