import time
import threading
from docx import Document
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import scrolledtext, messagebox
from selenium.webdriver.common.action_chains import ActionChains

def scrape_paginas_amarillas(profesion):
    url = f"https://www.paginasamarillas.es/search/{profesion}/all-ma/all-pr/all-is/all-ci/all-ba/all-pu/all-nc/1?what={profesion}&qc=true"

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        time.sleep(3)  # Asegúrate de dar tiempo a la página para cargar

        # Intentar cerrar la ventana de cookies si está presente
        try:
            cookie_close_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'onetrust-close-btn-handler')]"))
            )
            cookie_close_button.click()
            time.sleep(2)  # Esperamos un poco para asegurarnos de que se cerró
        except:
            pass  # Si no se encuentra el botón de cookies, continuamos

        resultados = []
        empresas = driver.find_elements(By.CSS_SELECTOR, "h2 span[itemprop='name']")
        direcciones = driver.find_elements(By.CSS_SELECTOR, "a[data-omniclick='route']")
        botones_telefono = driver.find_elements(By.XPATH, "//div[@data-omniclick='phoneShow']")

        for i in range(len(empresas)):
            nombre = empresas[i].text.strip()
            direccion = direcciones[i].text.strip() if i < len(direcciones) else "Dirección no encontrada"
            telefono = "Teléfono no disponible"

            if i < len(botones_telefono):
                try:
                    # Desplazarse hasta el botón y hacer clic
                    ActionChains(driver).move_to_element(botones_telefono[i]).perform()
                    botones_telefono[i].click()

                    # Aumentar el tiempo de espera para que el teléfono se haga visible
                    WebDriverWait(driver, 10).until(
                        EC.visibility_of_element_located((By.XPATH, "//a[@data-omniclick='phone']/span[@itemprop='telephone']"))
                    )

                    # Extraer el teléfono del span
                    telefono_elemento = driver.find_element(By.XPATH, "//a[@data-omniclick='phone']/span[@itemprop='telephone']")
                    telefono = telefono_elemento.text.strip()
                except Exception as e:
                    print(f"No se pudo obtener el teléfono de {nombre}: {e}")

            resultados.append(f"{nombre} - {direccion} - {telefono}")

        driver.quit()
        return resultados if resultados else ["No se encontraron resultados."]
    
    except Exception as e:
        return [f"Error al obtener datos: {e}"]

def scrape_vulka(profesion):
    url = f"https://www.vulka.es/resultados.php?qs_wha={profesion}&qs_whe="
    
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        time.sleep(3)  # Dar tiempo para cargar
        
        resultados = []
        
        # Encontrar todos los <h3> dentro del componente con id="listado"
        negocios = driver.find_elements(By.XPATH, "//*[@id='listado']//h3")
        
        # Encontrar las localizaciones correspondientes a cada negocio
        localizaciones = driver.find_elements(By.XPATH, "//*[@id='listado']//span[@class='localizacion']")
        
        # Encontrar los números de teléfono dentro de <div class="infoContacto">
        telefonos = driver.find_elements(By.XPATH, "//*[@id='listado']//div[@class='infoContacto']")
        
        for negocio, localizacion, telefono in zip(negocios, localizaciones, telefonos):
            # Añadir nombre del negocio, localización y teléfono
            resultados.append(f"{negocio.text} - {localizacion.text} - {telefono.text.strip()}")
        
        driver.quit()
        return resultados if resultados else ["No se encontraron resultados."]
    
    except Exception as e:
        return [f"Error al obtener datos: {e}"]

def guardar_en_word(profesion, datos_paginas_amarillas, datos_vulka):
    doc = Document()
    doc.add_heading(f"Resultados de búsqueda para {profesion}", level=1)
    
    # Resultados de Páginas Amarillas
    doc.add_heading("Páginas Amarillas:", level=2)
    for anuncio in datos_paginas_amarillas:
        parrafo = doc.add_paragraph()
        partes = anuncio.split(" - ")
        if len(partes) >= 3:
            nombre, direccion, telefono = partes[0], partes[1], partes[2]
        else:
            nombre = partes[0]
            direccion = "Dirección no disponible"
            telefono = "Teléfono no disponible"
        
        parrafo.add_run(f"- {nombre}: ").bold = True
        parrafo.add_run(f"{direccion}").italic = True
        parrafo.add_run(f" - Teléfono: ").bold = True
        parrafo.add_run(f"{telefono}").italic = True

    # Resultados de Vulka
    doc.add_heading("Vulka:", level=2)
    for anuncio in datos_vulka:
        doc.add_paragraph(f"- {anuncio}")
    
    archivo_nombre = f"resultados_{profesion}.docx"
    doc.save(archivo_nombre)
    messagebox.showinfo("Archivo guardado", f"Los resultados se han guardado en {archivo_nombre}")

# Interfaz gráfica con Tkinter
root = tk.Tk()
root.title("Páginas Amarillas y Vulka")
root.geometry("700x600")

tk.Label(root, text="Introduce una profesión:").pack(pady=5)
entrada = tk.Entry(root, width=60)
entrada.pack(pady=5)

def buscar():
    profesion = entrada.get()
    datos_paginas_amarillas = scrape_paginas_amarillas(profesion)
    datos_vulka = scrape_vulka(profesion)
    threading.Thread(target=lambda: guardar_en_word(profesion, datos_paginas_amarillas, datos_vulka), daemon=True).start()

boton_buscar = tk.Button(root, text="Buscar", command=buscar)
boton_buscar.pack(pady=5)

resultado_text = scrolledtext.ScrolledText(root, width=80, height=15, state=tk.DISABLED)
resultado_text.pack(pady=5)

root.mainloop()
