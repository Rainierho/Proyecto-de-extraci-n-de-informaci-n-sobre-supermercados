import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
from datetime import datetime


def licores_mundiales_scrappy():
    #############################################################################################################

    links = [['https://www.licoresmundiales.com/whisky.html?p=1&product_list_limit=200','whisky'],
    ['https://www.licoresmundiales.com/vinos.html?p=1&product_list_limit=200','vinos'],
    ['https://www.licoresmundiales.com/vinos.html?p=2&product_list_limit=200','vinos'],
    ['https://www.licoresmundiales.com/vinos.html?p=3&product_list_limit=200','vinos'],
    ['https://www.licoresmundiales.com/vinos.html?p=4&product_list_limit=200','vinos'],
    ['https://www.licoresmundiales.com/burbujas.html?p=1&product_list_limit=200','burbujas'],
    ['https://www.licoresmundiales.com/ron.html?p=1&product_list_limit=200','ron'],
    ['https://www.licoresmundiales.com/destilados.html?p=1&product_list_limit=200','destilados'],
    ['https://www.licoresmundiales.com/destilados.html?p=2&product_list_limit=200','destilados'],
    ['https://www.licoresmundiales.com/licores.html?p=1&product_list_limit=200','licores'],
    ['https://www.licoresmundiales.com/otros.html?p=1&product_list_limit=200','otros'],
    ['https://www.licoresmundiales.com/gastronomia.html?p=1&product_list_limit=200','gastronomia'],
    ['https://www.licoresmundiales.com/accesorios.html?p=1&product_list_limit=200','accesorios']]
        
    nombres = list()
    apellidos = list()
    precio = list()
    categoria = list()
    
    for link in links:
        driver_path = 'chromedriver.exe'
        driver = webdriver.Chrome(service=Service(driver_path))
        driver.set_window_size(20,10)
        try:
            driver.get(link[0])
            r = WebDriverWait(driver, 12).until(
                    EC.presence_of_element_located((By.XPATH,'//*[@id="layer-product-list"]/div[2]/ol'))
                )

            lineas = r.text.split("\n")
            grupos_de_3_lineas = [lineas[i:i + 3] for i in range(0, len(lineas), 3)]
            
            for grupo in grupos_de_3_lineas:
                if 0 < len(grupo):
                    nombres.append(grupo[0])
                else:
                    nombres.append(None)
                    
                if 1 < len(grupo):
                    apellidos.append(grupo[1])
                else:
                    apellidos.append(None)
                    
                if 2 < len(grupo):
                    precio.append(grupo[2])
                else:
                    precio.append(None)
                    
                if nombres[len(nombres)-1] == None and apellidos[len(apellidos)-1] == None and precio[len(precio)-1] == None:
                    categoria.append(None)
                else:
                    categoria.append(link[1])
        finally:
            print(link[0])
            driver.delete_all_cookies()
            driver.quit()
            time.sleep(5)
    global df
    dia = datetime.now()
    dia_df = f'{dia.day}/{dia.month}/{dia.year}'
    df = pd.DataFrame()

    df['producto'] = nombres
    df['precio $'] = precio
    df['categoria'] = categoria
    df['fecha'] = dia_df
    df['supermercado'] = 'Licores Mundiales'
    df['apellidos'] = apellidos


    df.drop_duplicates(inplace=True)
    df['precio $'] = df['precio $'].str.replace('$','').str.replace('.','').str.strip().str.replace(',','.')

    df['nombres'] = df['nombres'] + ' - ' + df['apellidos']
    df.drop(columns='apellidos',inplace=True)
    df = df[~df['nombres'].str.contains('[$]')]
    return df


##############################################################################################################