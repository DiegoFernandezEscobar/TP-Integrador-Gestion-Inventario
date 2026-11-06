# ============================================================
# Desafio opcional: interfaz grafica con tkinter.
#
# ACLARACION: esta interfaz la hicimos a proposito con ayuda de
# Claude (IA), y quisimos que se note. El diseño copia el estilo
# del programa Rufus: secciones con titulo y linea, campos con la
# etiqueta arriba, una barra de estado y el boton Cerrar abajo.
#
# La ventana usa las funciones de inventario.py. La unica excepcion
# es el ordenamiento en vivo: repite seleccion y burbuja paso a paso
# para poder pintar cada comparacion en la tabla.
# Cada cambio se guarda en inventario.csv al momento.
# ============================================================

import time
import tkinter
from tkinter import ttk, messagebox
import inventario

productos = inventario.cargar_csv("inventario.csv")

# colores
GRIS = "#e6e6e6"
VERDE = "#bdeac4"
ROJO = "#f2c4c4"
AMARILLO = "#fff3a6"   # filas que se estan comparando
NARANJA = "#ffc58a"    # filas que se intercambian
ORDENADO = "#d7f0dc"   # filas que ya quedaron en su lugar

# opciones de los desplegables (la posicion de cada lista coincide)
CRITERIOS = ["Nombre", "Precio", "Stock", "Codigo"]
COLUMNAS = [1, 3, 4, 0]
METODOS = ["Seleccion", "Burbuja"]
EXPLICACIONES = [
    "Seleccion: busca el menor de lo que falta ordenar y lo pone adelante.",
    "Burbuja: compara cada fila con la siguiente y las da vuelta si estan al reves.",
]
VELOCIDADES = ["Lenta", "Normal", "Rapida"]
ESPERAS = [0.35, 0.08, 0.015]  # segundos entre paso y paso


# ---------- FUNCIONES DE PANTALLA ----------

# Arma el texto de un producto para los mensajes.
def texto_producto(fila):
    return (str(fila[0]) + " - " + fila[1] + " - " + fila[2]
            + " - $" + str(fila[3]) + " - stock: " + str(fila[4]))


# Borra la tabla y la vuelve a llenar. Las filas alternan color (par / impar).
def actualizar_tabla():
    for item in tabla.get_children():
        tabla.delete(item)
    for i in range(len(productos)):
        if i % 2 == 0:
            tabla.insert("", tkinter.END, values=productos[i], tags=("par",))
        else:
            tabla.insert("", tkinter.END, values=productos[i], tags=("impar",))
    contador.config(text=str(len(productos)) + " productos")


# Muestra un mensaje en la barra de estado (verde si salio bien, rojo si no).
def estado(texto, salio_bien):
    if salio_bien:
        barra.config(text=texto, bg=VERDE)
    else:
        barra.config(text=texto, bg=ROJO)


# Guarda en el csv y refresca la tabla. Se llama despues de cada cambio.
def guardar(texto):
    inventario.guardar_csv(productos, "inventario.csv")
    actualizar_tabla()
    estado(texto + " - guardado en inventario.csv", True)


# Al hacer clic en una fila de la tabla, copia sus datos a las casillas.
def al_elegir_fila(evento):
    seleccion = tabla.selection()
    if len(seleccion) > 0:
        datos = tabla.item(seleccion[0])["values"]
        casillas = [entrada_codigo, entrada_nombre, entrada_categoria,
                    entrada_precio, entrada_stock]
        for i in range(5):
            casillas[i].delete(0, tkinter.END)
            casillas[i].insert(0, datos[i])


# Cambia la explicacion cuando se elige otro metodo en el desplegable.
def al_elegir_metodo(evento):
    explicacion.config(text=EXPLICACIONES[combo_metodo.current()])


# ---------- ACCIONES DE LOS BOTONES ----------
# try/except: si en una casilla de numero escriben letras, int() o float()
# dan ValueError. En vez de cortarse, el programa avisa en la barra.

def agregar():
    try:
        codigo = int(entrada_codigo.get())
        precio = float(entrada_precio.get())
        stock = int(entrada_stock.get())
        if inventario.alta_producto(productos, codigo, entrada_nombre.get(),
                                    entrada_categoria.get(), precio, stock):
            guardar("Producto " + str(codigo) + " agregado")
        else:
            estado("No se pudo agregar: codigo repetido o datos invalidos", False)
    except ValueError:
        estado("Codigo, precio y stock tienen que ser numeros", False)


def eliminar():
    try:
        codigo = int(entrada_codigo.get())
        if inventario.baja_producto(productos, codigo):
            guardar("Producto " + str(codigo) + " eliminado")
        else:
            estado("No existe el codigo " + str(codigo), False)
    except ValueError:
        estado("El codigo tiene que ser un numero", False)


def cambiar_stock():
    try:
        codigo = int(entrada_codigo.get())
        cantidad = int(entrada_cantidad.get())
        if inventario.modificar_stock(productos, codigo, cantidad):
            guardar("Stock del producto " + str(codigo) + " actualizado")
        else:
            estado("No existe o el stock quedaria negativo", False)
    except ValueError:
        estado("Codigo y cantidad tienen que ser numeros", False)


def buscar():
    try:
        codigo = int(entrada_codigo.get())
        pos, comp_sec = inventario.busqueda_secuencial(productos, codigo)
        # la binaria necesita la matriz ordenada por codigo
        inventario.ordenar_seleccion(productos, 0)
        pos, comp_bin = inventario.busqueda_binaria(productos, codigo)
        resumen = ("Busqueda secuencial: " + str(comp_sec) + " comparaciones | "
                   + "binaria (tras ordenar por codigo con seleccion): "
                   + str(comp_bin))
        guardar(resumen)
        if pos == -1:
            estado("No existe el codigo " + str(codigo) + ". " + resumen, False)
        else:
            barra.config(text=resumen)
            # marco en la tabla la fila encontrada
            fila_tabla = tabla.get_children()[pos]
            tabla.selection_set(fila_tabla)
            tabla.see(fila_tabla)
    except ValueError:
        estado("El codigo tiene que ser un numero", False)


def ver_stock_bajo():
    try:
        umbral = int(entrada_cantidad.get())
        texto = ""
        for fila in inventario.stock_bajo(productos, umbral):
            texto = texto + texto_producto(fila) + "\n"
        if texto == "":
            texto = "Ningun producto tiene stock menor a " + str(umbral)
        messagebox.showinfo("Stock bajo", texto)
    except ValueError:
        estado("Para Stock bajo, escriba el limite en la casilla Sumar o restar al stock", False)


def ver_valor_total():
    estado("Valor total del inventario: $ " + str(inventario.valor_total(productos)), True)


def ver_caro_barato():
    if len(productos) == 0:
        estado("No hay productos", False)
    else:
        messagebox.showinfo("Precios",
                            "Mas caro:\n" + texto_producto(inventario.producto_mas_caro(productos))
                            + "\n\nMas barato:\n" + texto_producto(inventario.producto_mas_barato(productos)))


def exportar():
    inventario.exportar_json(productos, "inventario.json")
    estado("Exportado a inventario.json", True)


# ---------- ORDENAMIENTO EN VIVO ----------

# Repinta la tabla: las filas a y b con el color del paso,
# y las que estan entre desde y hasta (sin incluir hasta) como ya ordenadas.
def dibujar(a, b, color, desde, hasta):
    filas = tabla.get_children()
    for i in range(len(productos)):
        if i == a or i == b:
            marca = color
        elif i >= desde and i < hasta:
            marca = "ordenado"
        elif i % 2 == 0:
            marca = "par"
        else:
            marca = "impar"
        tabla.item(filas[i], values=productos[i], tags=(marca,))


# Muestra los contadores y espera un poco para que se vea el paso.
def pausa(comparaciones, intercambios):
    contadores.config(text="Comparaciones: " + str(comparaciones)
                      + "     Intercambios: " + str(intercambios))
    ventana.update()  # redibuja la ventana
    time.sleep(ESPERAS[combo_velocidad.current()])


# Misma logica que ordenar_seleccion de inventario.py, pero pintando cada paso.
def seleccion_en_vivo(columna):
    comparaciones = 0
    intercambios = 0
    n = len(productos)
    for i in range(n - 1):
        menor = i
        for j in range(i + 1, n):
            comparaciones = comparaciones + 1
            dibujar(j, menor, "comparando", 0, i)
            pausa(comparaciones, intercambios)
            if productos[j][columna] < productos[menor][columna]:
                menor = j
        if menor != i:
            aux = productos[i]
            productos[i] = productos[menor]
            productos[menor] = aux
            intercambios = intercambios + 1
            dibujar(i, menor, "intercambio", 0, i)
            pausa(comparaciones, intercambios)
    dibujar(-1, -1, "", 0, n)
    pausa(comparaciones, intercambios)
    return comparaciones, intercambios


# Misma logica que ordenar_burbuja de inventario.py, pero pintando cada paso.
# En burbuja las filas ordenadas se van juntando al final.
def burbuja_en_vivo(columna):
    comparaciones = 0
    intercambios = 0
    n = len(productos)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            comparaciones = comparaciones + 1
            dibujar(j, j + 1, "comparando", n - i, n)
            pausa(comparaciones, intercambios)
            if productos[j][columna] > productos[j + 1][columna]:
                aux = productos[j]
                productos[j] = productos[j + 1]
                productos[j + 1] = aux
                intercambios = intercambios + 1
                dibujar(j, j + 1, "intercambio", n - i, n)
                pausa(comparaciones, intercambios)
    dibujar(-1, -1, "", 0, n)
    pausa(comparaciones, intercambios)
    return comparaciones, intercambios


# Activa o desactiva los botones (mientras se anima no se puede tocar nada).
def botones_activos(activos):
    for boton in todos_los_botones:
        if activos:
            boton.state(["!disabled"])
        else:
            boton.state(["disabled"])


def ordenar_en_vivo():
    if len(productos) < 2:
        estado("Hacen falta al menos 2 productos para ordenar", False)
        return
    criterio = CRITERIOS[combo_criterio.current()]
    columna = COLUMNAS[combo_criterio.current()]
    metodo = METODOS[combo_metodo.current()]
    botones_activos(False)
    tabla.selection_remove(tabla.selection())
    barra.config(text="Ordenando por " + criterio + " con " + metodo + "...", bg=AMARILLO)
    # try/except: si cierran la ventana en medio de la animacion, termino sin error
    try:
        if metodo == "Seleccion":
            comparaciones, intercambios = seleccion_en_vivo(columna)
        else:
            comparaciones, intercambios = burbuja_en_vivo(columna)
    except tkinter.TclError:
        return
    botones_activos(True)
    guardar("Ordenado por " + criterio + " con " + metodo + ": "
            + str(comparaciones) + " comparaciones, "
            + str(intercambios) + " intercambios")


# ---------- ARMADO DE LA VENTANA ----------

ventana = tkinter.Tk()
ventana.title("Gestion de Inventario")
ventana.resizable(False, False)

estilo = ttk.Style()
if "vista" in estilo.theme_names():
    estilo.theme_use("vista")  # el aspecto normal de Windows, como Rufus
estilo.configure("Treeview", rowheight=22)
estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

marco = ttk.Frame(ventana, padding=(18, 14, 18, 16))
marco.pack()


# Titulo de seccion al estilo Rufus: texto grande y una linea al costado.
def titulo_seccion(contenedor, texto, fila):
    caja = ttk.Frame(contenedor)
    caja.grid(row=fila, column=0, sticky="we", pady=(14, 6))
    ttk.Label(caja, text=texto, font=("Segoe UI", 13)).pack(side="left")
    ttk.Separator(caja).pack(side="left", fill="x", expand=True, padx=(10, 0))


# Etiqueta arriba y casilla abajo, como los campos de Rufus.
def campo(contenedor, texto, fila, columna):
    ttk.Label(contenedor, text=texto).grid(row=fila, column=columna,
                                           sticky="w", padx=6)
    entrada = ttk.Entry(contenedor, width=30)
    entrada.grid(row=fila + 1, column=columna, sticky="we", padx=6, pady=(2, 8))
    return entrada


# Etiqueta arriba y desplegable abajo (para el ordenamiento).
def desplegable(contenedor, texto, opciones, elegida, columna):
    ttk.Label(contenedor, text=texto).grid(row=0, column=columna, sticky="w", padx=6)
    combo = ttk.Combobox(contenedor, values=opciones, state="readonly", width=14)
    combo.current(elegida)
    combo.grid(row=1, column=columna, sticky="we", padx=6, pady=(2, 4))
    return combo


# --- encabezado (ocupa las dos columnas) ---
ttk.Label(marco, text="Gestion de Inventario", font=("Segoe UI", 18)).grid(
    row=0, column=0, columnspan=2, sticky="w")
ttk.Label(marco, text="Algoritmos: busqueda secuencial y binaria  ·  "
          "ordenamiento por seleccion y burbuja",
          foreground="#666666").grid(row=1, column=0, columnspan=2, sticky="w")

# la ventana tiene dos columnas: controles a la izquierda, tabla a la derecha
izquierda = ttk.Frame(marco)
izquierda.grid(row=2, column=0, sticky="n", padx=(0, 12))
derecha = ttk.Frame(marco)
derecha.grid(row=2, column=1, sticky="n", padx=(12, 0))

# --- izquierda, seccion 1: datos del producto ---
titulo_seccion(izquierda, "Datos del producto", 0)
datos = ttk.Frame(izquierda)
datos.grid(row=1, column=0, sticky="we")
entrada_codigo = campo(datos, "Codigo", 0, 0)
entrada_nombre = campo(datos, "Nombre", 0, 1)
entrada_categoria = campo(datos, "Categoria", 2, 0)
entrada_precio = campo(datos, "Precio", 2, 1)
entrada_stock = campo(datos, "Stock", 4, 0)
entrada_cantidad = campo(datos, "Sumar o restar al stock (ej: 10 o -5)", 4, 1)
# las dos columnas de casillas ocupan todo el ancho, en partes iguales
datos.columnconfigure(0, weight=1, uniform="campos")
datos.columnconfigure(1, weight=1, uniform="campos")

# --- izquierda, seccion 2: acciones ---
titulo_seccion(izquierda, "Acciones", 2)
acciones = ttk.Frame(izquierda)
acciones.grid(row=3, column=0, sticky="we")
botones = [
    ["Agregar", agregar], ["Eliminar", eliminar],
    ["Sumar / restar stock", cambiar_stock], ["Buscar por codigo", buscar],
    ["Stock bajo", ver_stock_bajo], ["Valor total", ver_valor_total],
    ["Mas caro y barato", ver_caro_barato], ["Exportar JSON", exportar],
]
todos_los_botones = []
# los botones van de a 4 por renglon; command es la funcion del clic
for i in range(len(botones)):
    boton = ttk.Button(acciones, text=botones[i][0], command=botones[i][1])
    boton.grid(row=i // 4, column=i % 4, sticky="we", padx=6, pady=4, ipady=3)
    todos_los_botones.append(boton)
for columna in range(4):
    acciones.columnconfigure(columna, weight=1, uniform="botones")

# --- izquierda, seccion 3: ordenamiento en vivo ---
titulo_seccion(izquierda, "Ordenamiento en vivo", 4)
orden = ttk.Frame(izquierda)
orden.grid(row=5, column=0, sticky="we")
combo_criterio = desplegable(orden, "Ordenar por", CRITERIOS, 0, 0)
combo_metodo = desplegable(orden, "Metodo", METODOS, 0, 1)
combo_velocidad = desplegable(orden, "Velocidad", VELOCIDADES, 1, 2)
combo_metodo.bind("<<ComboboxSelected>>", al_elegir_metodo)
boton_ordenar = ttk.Button(orden, text="Ordenar en vivo", command=ordenar_en_vivo)
boton_ordenar.grid(row=1, column=3, sticky="we", padx=6, pady=(2, 4), ipady=2)
todos_los_botones.append(boton_ordenar)
for columna in range(4):
    orden.columnconfigure(columna, weight=1, uniform="orden")

explicacion = ttk.Label(orden, text=EXPLICACIONES[0], foreground="#444444")
explicacion.grid(row=2, column=0, columnspan=4, sticky="w", padx=6, pady=(8, 0))

# leyenda de colores y contadores
leyenda = ttk.Frame(orden)
leyenda.grid(row=3, column=0, columnspan=4, sticky="we", padx=6, pady=(8, 0))
colores = [[AMARILLO, "Comparando"], [NARANJA, "Intercambio"], [ORDENADO, "Ya ordenado"]]
for i in range(3):
    tkinter.Label(leyenda, bg=colores[i][0], width=2, relief="solid", bd=1).pack(side="left")
    ttk.Label(leyenda, text=colores[i][1]).pack(side="left", padx=(4, 14))
contadores = ttk.Label(orden, text="Comparaciones: 0     Intercambios: 0",
                       font=("Segoe UI", 10, "bold"))
contadores.grid(row=4, column=0, columnspan=4, sticky="w", padx=6, pady=(8, 0))

# --- derecha: inventario ---
titulo_seccion(derecha, "Inventario", 0)
columnas = ["Codigo", "Nombre", "Categoria", "Precio", "Stock"]
anchos = [70, 190, 110, 90, 70]
caja_tabla = ttk.Frame(derecha)
caja_tabla.grid(row=1, column=0, sticky="we")
tabla = ttk.Treeview(caja_tabla, columns=columnas, show="headings", height=15)
for i in range(5):
    tabla.heading(columnas[i], text=columnas[i])
    tabla.column(columnas[i], width=anchos[i])
# barra para desplazarse cuando hay mas productos de los que entran
desplazar = ttk.Scrollbar(caja_tabla, command=tabla.yview)
tabla.config(yscrollcommand=desplazar.set)
tabla.pack(side="left", fill="x", expand=True)
desplazar.pack(side="right", fill="y")
tabla.bind("<<TreeviewSelect>>", al_elegir_fila)
# colores de las filas segun su marca
tabla.tag_configure("par", background="#ffffff")
tabla.tag_configure("impar", background="#f4f6f8")
tabla.tag_configure("comparando", background=AMARILLO)
tabla.tag_configure("intercambio", background=NARANJA)
tabla.tag_configure("ordenado", background=ORDENADO)

# --- abajo, ocupando las dos columnas: estado ---
abajo = ttk.Frame(marco)
abajo.grid(row=3, column=0, columnspan=2, sticky="we")
abajo.columnconfigure(0, weight=1)
titulo_seccion(abajo, "Estado", 0)
barra = tkinter.Label(abajo, text="LISTO", bg=GRIS, relief="solid", bd=1,
                      height=2, font=("Segoe UI", 9))
barra.grid(row=1, column=0, sticky="we")

# --- pie: cantidad de productos a la izquierda, Cerrar a la derecha ---
pie = ttk.Frame(abajo)
pie.grid(row=2, column=0, sticky="we", pady=(12, 0))
contador = ttk.Label(pie, text="")
contador.pack(side="left")
boton_cerrar = ttk.Button(pie, text="Cerrar", command=ventana.destroy)
boton_cerrar.pack(side="right", ipady=3)
todos_los_botones.append(boton_cerrar)

actualizar_tabla()
ventana.mainloop()  # deja la ventana abierta esperando clics
