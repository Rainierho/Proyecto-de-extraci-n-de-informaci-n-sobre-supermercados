import time
import datetime
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Dataframe vacío
dataframe_global = pd.DataFrame()

# Lista de links con cada una de las subcategorias por producto
link_list = ['/es/despensa/aceites-vinagres/c/A0109', '/es/despensa/arroz-granos/c/A0103',
             '/es/despensa/azucares-endulzantes/c/A0104', '/es/despensa/cafe/c/A0107',
             '/es/despensa/cereales/c/A0115', '/es/despensa/dulces-galletas-reposteria/c/A0106', 
             '/es/despensa/enlatados-envasados-conservas/c/A0108', '/es/despensa/harinas-pastas/c/A0102', 
             '/es/despensa/lacteos/c/A0101', '/es/despensa/panaderia/c/A0111', '/es/despensa/salsas-especias/c/A0110', 
             '/es/despensa/snacks/c/A0105', '/es/despensa/sopas-bases/c/A0112', '/es/despensa/temporada-navidena/c/A0116', 
             '/es/despensa/untables/c/A0113', '/es/alimentos-frescos/carniceria/c/A0201', '/es/alimentos-frescos/charcuteria/c/A0202', 
             '/es/alimentos-frescos/comida-lista/c/A0208', '/es/alimentos-frescos/frutas/c/A0205', 
             '/es/alimentos-frescos/huevos/c/A0207', '/es/alimentos-frescos/pescaderia-mariscos/c/A0204', 
             '/es/alimentos-frescos/quesos/c/A0203', '/es/alimentos-frescos/verduras-legumbres/c/A0206', 
             '/es/congelados-refrigerados/comida-lista/c/A0302', '/es/congelados-refrigerados/frutas-congeladas/c/A0306', 
             '/es/congelados-refrigerados/hielo/c/A0301', '/es/congelados-refrigerados/masas/c/A0304', 
             '/es/congelados-refrigerados/pasapalos-congelados/c/A0303', '/es/congelados-refrigerados/postres-helados/c/A0305', 
             '/es/licores/aperitivos-digestivos/c/A0409', '/es/licores/cerveza/c/A0408', '/es/licores/espumantes/c/A0401', 
             '/es/licores/ginebra/c/A0405', '/es/licores/rones/c/A0403', '/es/licores/tequila/c/A0406', '/es/licores/vino/c/A0407', 
             '/es/licores/vodka/c/A0404', '/es/licores/whisky/c/A0402', '/es/bebidas/agua/c/A0501', 
             '/es/bebidas/bebidas-polvo/c/A0505', '/es/bebidas/bebidas-listas/c/A0506', '/es/bebidas/gaseosas/c/A0504', 
             '/es/bebidas/jugos/c/A0503', '/es/bebidas/te-e-infusiones/c/A0502', '/es/cuidado-personal-salud/cuidado-bucal/c/A0601', 
             '/es/cuidado-personal-salud/cuidado-corporal/c/A0606', '/es/cuidado-personal-salud/cuidado-del-cabello/c/A0602', 
             '/es/cuidado-personal-salud/cuidado-facial/c/A0605', '/es/cuidado-personal-salud/cuidado-bebe/c/A0607', 
             '/es/cuidado-personal-salud/cuidado-sexual/c/A0608', '/es/cuidado-personal-salud/farmacia/c/A0604', 
             '/es/cuidado-personal-salud/higiene-personal/c/A0603', '/es/mascotas/accesorios-e-higiene/c/A0804', 
             '/es/mascotas/alimentacion-aves-tortugas/c/A0803', '/es/mascotas/alimentacion-gatos/c/A0802', 
             '/es/mascotas/alimentacion-perros/c/A0801', '/es/hogar/cocina/c/A0901', '/es/hogar/consumibles/c/A0902', 
             '/es/hogar/habitacion/c/A0907', '/es/hogar/utiles-escolares-de-oficina/c/A0904']

links_format = [f'https://gamaenlinea.com'+i+'?pageSize=100' for i in link_list]

# Path a ChromeDriver
driver_path = 'chromedriver.exe'  

def get_verification(dictionary, category):
    '''Esta función verifica que todas las listas tengan la misma longitud'''
    
    length_list = [len(list_) for list_ in dictionary.values()]  # Lista con todas las longitudes
    if not all(length == length_list[0] for length in length_list):
        #print(f'En la categoría: {category} las listas no tienen la misma longitud.')
        #print(length_list)
        return False
    else:
        return True

def get_price(price):
    '''Esta función extrae el precio sin IVA de cada uno de los productos'''
    
    patron_precio = re.compile(r'Ref.\s+(\d+)(,\d+)?')
    if re.findall(patron_precio, price):
        price_without_iva = re.findall(patron_precio, price)[0]
        if len(price_without_iva) == 2:
            price_without_iva = price_without_iva[0] + '.' + price_without_iva[1].replace(',', '')
        else:
            price_without_iva = price_without_iva[0]
        return price_without_iva
    else:
        return None
  

def get_products(products, category):
    ''' Esta función se encarga de almacenar los productos con su respectivo precio, categoria, fecha y supermercado, 
    en un diccionario para que sean convertidos a Dataframe'''
    
    # Verificar si el string obtenido del scraping está vacío
    if len(products) == len('') or len(products) == len(' '):
        return None

    # Diccionario que almacenará los productos por categoría 
    add_product= {'producto': [], 'precio $': [], 'categoria': [], 'fecha': [], 'supermercado': []}

    # Limpieza en products
    products = re.sub(r'IVA Ref.\s+\d+', '', products)
    products = re.sub(r'Total Ref.\s+\d+', '', products)

    # Nombre de cada producto
    if f'\n{category}\n' in products:
        patron_product = re.compile(rf'{category}\n(.*?)\nRef.')
        for match in patron_product.finditer(products):
            add_product['producto'].append(match.group(1))
    else:
        patron_product = re.compile(rf'(?:\n(.*?)\nRef.)|(?:(.*?)\nRef.)')
        list_product = patron_product.findall(products)

        for i in range(len(list_product)):
            add_product['producto'].append(list_product[i][0])

    # Precio sin IVA de cada producto
    for line in products.splitlines():
        if re.findall(r'Ref.\s+(\d+)', line) and not re.findall(r'IVA Ref.\s+(\d+)', line) and not re.findall(r'Total Ref.\s+(\d+)', line):
            price = get_price(line)
            add_product['precio $'].append(price)

    # Categoria de cada producto 
    quantity_products = len(add_product['producto'])
    if "| Supermercado Gama en Línea" in category:
        category = category.replace(" | Supermercado Gama en Línea", "")
    repeat_category = [category] * quantity_products
    add_product['categoria'] = repeat_category

    # Fecha actual 
    today_date = datetime.datetime.now()
    date = f'{today_date.day}-{today_date.month}-{today_date.year}'  
    repeat_date = [date] * quantity_products
    add_product['fecha'] = repeat_date

    # Supermercado 
    supermarket = 'Gama'
    repeat_supermarket = [supermarket] * quantity_products
    add_product['supermercado'] = repeat_supermarket

    if get_verification(add_product, category):
        global dataframe_global
        if dataframe_global.empty:
            dataframe_global = pd.DataFrame.from_dict(add_product)
        else:
            dataframe_global = pd.concat([dataframe_global, pd.DataFrame.from_dict(add_product)], ignore_index=True)
        return dataframe_global
    else:
        return None


def scrape_link(link):
    """Obtiene el elemento 'product-results-list' del link que recibe como argumento."""
    
    # Path a ChromeDriver
    driver_path = 'chromedriver.exe'
    
    # Creando una instancia WebDriver
    driver = webdriver.Chrome(service=Service(driver_path))
    driver.set_window_size(20,10)
    driver.get(link)

    try:
        # Esperar 1 minuto hasta que haya cargado completamente la lista de productos
        product_results = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, 'product-results-list'))
        )
        
        # Obtener los productos
        product_text = product_results.text 
        time.sleep(20) 
    except:
        pass

    sub_category = driver.title
    driver.delete_all_cookies()  # Eliminar todas las cookies del driver
    driver.quit()  # Cerrar la instancia del navegador
    
    get_products(product_text, sub_category)
    time.sleep(120)  # Esperar 2 minutos antes de volver a ejecutar el siguiente link 
    

def gama_scraping():
  """Función principal que ejecuta el scraping de todas las categorías y retorna el DataFrame global."""

  # Recorre la lista y ejecuta la función
  for link in links_format:
    scrape_link(link)

  return dataframe_global 