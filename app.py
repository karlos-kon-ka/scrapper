import time 
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import messagebox
from selenium.webdriver.common.action_chains import ActionChains
from openpyxl import Workbook

def scrape_paginas_amarillas(profesion, ubicacion):
    pagina = 1
    resultados = []

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        while True:
            url = f"https://www.paginasamarillas.es/search/{profesion}/all-ma/{ubicacion}/all-is/{ubicacion}/all-ba/all-pu/all-nc/{pagina}?what={profesion}&where={ubicacion}&qc=true"
            driver.get(url)
            time.sleep(3)

            # Cerrar cookies si aparecen
            try:
                cookie_close_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'onetrust-close-btn-handler')]"))
                )
                cookie_close_button.click()
                time.sleep(2)
            except:
                pass

            empresas = driver.find_elements(By.CSS_SELECTOR, "h2 span[itemprop='name']")
            direcciones = driver.find_elements(By.CSS_SELECTOR, "a[data-omniclick='route']")
            botones_telefono = driver.find_elements(By.XPATH, "//div[@data-omniclick='phoneShow']")

            # Si no hay empresas, no hay más páginas
            if not empresas:
                break

            for i in range(len(empresas)):
                nombre = empresas[i].text.strip()
                direccion = direcciones[i].text.strip() if i < len(direcciones) else "Dirección no encontrada"
                telefono = "Teléfono no disponible"

                if i < len(botones_telefono):
                    try:
                        ActionChains(driver).move_to_element(botones_telefono[i]).perform()
                        botones_telefono[i].click()

                        WebDriverWait(driver, 10).until(
                            EC.visibility_of_element_located((By.XPATH, "//a[@data-omniclick='phone']/span[@itemprop='telephone']"))
                        )
                        telefono_elemento = driver.find_element(By.XPATH, "//a[@data-omniclick='phone']/span[@itemprop='telephone']")
                        telefono = telefono_elemento.text.strip()
                    except:
                        pass

                resultados.append((ubicacion, direccion, nombre, telefono, "Páginas Amarillas"))  # Añadir "Páginas Amarillas" como fuente

            pagina += 1  # Pasar a la siguiente página

        driver.quit()
        return resultados if resultados else [("No se encontraron resultados.", "", "", "", "")]
    except Exception as e:
        return [("Error al obtener datos", str(e), "", "", "")]


def scrape_vulka(profesion, ubicacion):
    pagina = 1
    resultados = []

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        while True:
            url = f"https://www.vulka.es/resultados.php?qs_wha={profesion}&qs_whe={ubicacion}&pg={pagina}"
            driver.get(url)
            time.sleep(3)
            
            # Obtener los datos de cada página
            negocios = driver.find_elements(By.XPATH, "//*[@id='listado']//h3")
            localizaciones = driver.find_elements(By.XPATH, "//*[@id='listado']//span[@class='localizacion']")
            telefonos = driver.find_elements(By.XPATH, "//*[@id='listado']//div[@class='infoContacto']")
            
            # Si no hay más negocios, se detiene el bucle
            if not negocios:
                break
            
            # Procesar los resultados de la página
            for negocio, localizacion, telefono in zip(negocios, localizaciones, telefonos):
                resultados.append((ubicacion, localizacion.text, negocio.text, telefono.text.strip(), "Vulka"))  # Añadir "Vulka" como fuente

            pagina += 1  # Incrementar el número de página para la siguiente iteración
        
        driver.quit()
        return resultados if resultados else [("No se encontraron resultados.", "", "", "", "")]
    except Exception as e:
        return [("Error al obtener datos", str(e), "", "", "")]


def scrape_hotfrog(profesion, ubicacion):
    pagina = 1  # Comienza en la página 1
    resultados = []

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        while True:
            url = f"https://www.hotfrog.es/search/{ubicacion}/{profesion}/{pagina}"
            driver.get(url)
            time.sleep(3)

            empresas = driver.find_elements(By.CLASS_NAME, "hf-box")

            # Si no se encuentran empresas, se detiene el bucle (fin de las páginas)
            if not empresas:
                break

            # Procesar los resultados de la página
            for empresa in empresas:
                try:
                    nombre_empresa = empresa.find_element(By.XPATH, ".//h3/a/strong").text.strip()
                except:
                    nombre_empresa = "Nombre no disponible"

                try:
                    # Buscar el <a> con href que contiene el teléfono
                    telefono_elemento = empresa.find_element(By.XPATH, ".//a[starts-with(@href, 'tel:')]")
                    telefono = telefono_elemento.text.strip() if telefono_elemento else "Teléfono no disponible"
                except:
                    telefono = "Teléfono no disponible"

                direcciones = [d.text.strip() for d in empresa.find_elements(By.XPATH, ".//span[@class='small']") if d.text.strip()]

                if nombre_empresa and telefono and direcciones:
                    for direccion in direcciones:
                        resultados.append((ubicacion, direccion, nombre_empresa, telefono, "Hotfrog"))  # Añadir "Hotfrog" como fuente

            pagina += 1  # Incrementa el número de página para la siguiente iteración

        driver.quit()
        return resultados if resultados else [("No se encontraron resultados.", "", "", "", "")]
    except Exception as e:
        return [("Error al obtener datos", str(e), "", "", "")]


def guardar_en_excel(profesion, ubicacion, datos_paginas_amarillas, datos_vulka, datos_hotfrog):
    wb = Workbook()
    ws = wb.active
    ws.title = "Resultados"
    ws.append(["Ciudad", "Dirección", "Empresa", "Teléfono", "Fuente"])  # Añadir columna "Fuente"

    # Añadir los resultados de cada fuente a la hoja
    for datos in [datos_paginas_amarillas, datos_vulka, datos_hotfrog]:
        for ciudad, direccion, nombre, telefono, fuente in datos:
            ws.append([ciudad, direccion, nombre, telefono, fuente])  # Añadir la fuente correspondiente

    archivo_nombre = f"resultados_{profesion}_{ubicacion}.xlsx"
    wb.save(archivo_nombre)
    messagebox.showinfo("Archivo guardado", f"Los resultados se han guardado en {archivo_nombre}")


root = tk.Tk()
root.title("Scraper ")
root.geometry("700x200")

tk.Label(root, text="Introduce una profesión:").pack(pady=5)
entrada_profesion = tk.Entry(root, width=60)
entrada_profesion.pack(pady=5)

tk.Label(root, text="Introduce una localización:").pack(pady=5)
entrada_localizacion = tk.Entry(root, width=60)
entrada_localizacion.pack(pady=5)

def buscar():
    profesion = entrada_profesion.get()
    ubicacion = entrada_localizacion.get()

    if not profesion or not ubicacion:
        messagebox.showerror("Error", "Por favor, ingresa tanto la profesión como la localización.")
        return

    datos_paginas_amarillas = scrape_paginas_amarillas(profesion, ubicacion)
    datos_vulka = scrape_vulka(profesion, ubicacion)
    datos_hotfrog = scrape_hotfrog(profesion, ubicacion)

    threading.Thread(target=lambda: guardar_en_excel(profesion, ubicacion, datos_paginas_amarillas, datos_vulka, datos_hotfrog), daemon=True).start()

boton_buscar = tk.Button(root, text="Buscar", command=buscar)
boton_buscar.pack(pady=5)

root.mainloop()
