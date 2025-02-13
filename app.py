import time
import random
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from docx import Document
import requests
from bs4 import BeautifulSoup

def scrape_paginas_amarillas(profesion):
    """Realiza el scraping en Páginas Amarillas y devuelve una lista de resultados."""
    url = f"https://www.paginasamarillas.es/search/{profesion}/all-ma/madrid/all-is/espa%C3%B1a/all-ba/all-pu/all-nc/1?what={profesion}&where=espa%C3%B1a&qc=true"
    
    try:
        # Hacer la solicitud HTTP
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        if response.status_code != 200:
            return [f"Error al obtener datos: Código de estado {response.status_code}"]

        # Usar BeautifulSoup para parsear el HTML
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Buscar todos los elementos <h2> que contienen <span itemprop="name">
        h2_elements = soup.find_all("h2", string=True)
        h2_textos = [h2.get_text(strip=True) for h2 in h2_elements if h2.find("span", itemprop="name")]
        
        return h2_textos if h2_textos else ["No se encontraron resultados."]
    
    except Exception as e:
        return [f"Error al obtener datos: {e}"]

def guardar_en_word(profesion, datos_paginas_amarillas):
    """Guarda los datos extraídos en un archivo Word."""
    doc = Document()
    doc.add_heading(f"Resultados de búsqueda para {profesion}", level=1)

    doc.add_heading("Páginas Amarillas:", level=2)
    for anuncio in datos_paginas_amarillas:
        doc.add_paragraph(anuncio)

    archivo_nombre = f"resultados_{profesion}.docx"
    doc.save(archivo_nombre)
    messagebox.showinfo("Archivo guardado", f"Los resultados se han guardado en {archivo_nombre}")

def ejecutar_busqueda():
    """Ejecuta la búsqueda en un hilo separado para no bloquear la interfaz."""
    threading.Thread(target=buscar_profesion, daemon=True).start()

def buscar_profesion():
    """Función que obtiene la profesión, realiza el scraping y actualiza la interfaz."""
    profesion = entrada.get().strip()
    if not profesion:
        messagebox.showwarning("Error", "Introduce una profesión válida.")
        return

    boton_buscar.config(state=tk.DISABLED)
    resultado_text.config(state=tk.NORMAL)
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, f"Buscando '{profesion}' en Páginas Amarillas...\n")
    resultado_text.config(state=tk.DISABLED)
    root.update()

    datos_paginas_amarillas = scrape_paginas_amarillas(profesion)

    resultado_text.config(state=tk.NORMAL)
    resultado_text.delete(1.0, tk.END)
    resultado_text.insert(tk.END, "Páginas Amarillas:\n" + "\n".join(datos_paginas_amarillas) + "\n")
    resultado_text.config(state=tk.DISABLED)

    guardar_en_word(profesion, datos_paginas_amarillas)
    boton_buscar.config(state=tk.NORMAL)

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Scraper de Páginas Amarillas")
root.geometry("500x400")

tk.Label(root, text="Introduce una profesión:").pack(pady=5)
entrada = tk.Entry(root, width=40)
entrada.pack(pady=5)

boton_buscar = tk.Button(root, text="Buscar", command=ejecutar_busqueda)
boton_buscar.pack(pady=5)

resultado_text = scrolledtext.ScrolledText(root, width=60, height=15, state=tk.DISABLED)
resultado_text.pack(pady=5)

root.mainloop()
