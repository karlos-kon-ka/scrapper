import time
import threading
from bs4 import BeautifulSoup
import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox
from docx import Document
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def scrape_paginas_amarillas(profesion):
    """Realiza el scraping en Páginas Amarillas y devuelve una lista con nombres de empresas y ubicaciones usando Selenium."""
    url = f"https://www.paginasamarillas.es/search/{profesion}/all-ma/all-pr/all-is/all-ci/all-ba/all-pu/all-nc/1?what={profesion}&qc=true"
    
    try:
        # Configura el WebDriver
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        time.sleep(3)  # Espera que cargue la página

        resultados = []
        empresas = driver.find_elements(By.CSS_SELECTOR, "h2 span[itemprop='name']")
        direcciones = driver.find_elements(By.CSS_SELECTOR, "a[data-omniclick='route'] span.location")

        for empresa, direccion in zip(empresas, direcciones):
            nombre = empresa.text.strip()

            try:
                street = direccion.find_element(By.CSS_SELECTOR, "span[itemprop='streetAddress']").text.strip()
                postal_code = direccion.find_element(By.CSS_SELECTOR, "span[itemprop='postalCode']").text.strip()
                locality = direccion.find_element(By.CSS_SELECTOR, "span[itemprop='addressLocality']").text.strip()
                region = direccion.find_element(By.CSS_SELECTOR, "span[itemprop='addressRegion']").text.strip()
                ubicacion = f"{street}, {postal_code}, {locality}, {region}"
            except:
                ubicacion = "Ubicación no disponible"

            resultados.append(f"{nombre} - {ubicacion}")

        driver.quit()

        return resultados if resultados else ["No se encontraron resultados."]
    
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
    threading.Thread(target=buscar_profesion, daemon=True).start()

def buscar_profesion():
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
root.geometry("700x600")

tk.Label(root, text="Introduce una profesión:").pack(pady=5)
entrada = tk.Entry(root, width=40)
entrada.pack(pady=5)

boton_buscar = tk.Button(root, text="Buscar", command=ejecutar_busqueda)
boton_buscar.pack(pady=5)

resultado_text = scrolledtext.ScrolledText(root, width=60, height=15, state=tk.DISABLED)
resultado_text.pack(pady=5)

root.mainloop()
