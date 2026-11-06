# TP integrador - Gestion de inventario
# Fundamentos de Informatica (FAIN)
# Hecho por: Facundo Rodriguez y Diego Fernandez Escobar
#
# guardo el inventario en una matriz, cada fila es un producto:
# [codigo, nombre, categoria, precio, stock]
#    0       1        2        3       4

import json  # lo uso para exportar a json (desafio opcional)


# ===== CSV =====

# lee el csv y devuelve la matriz con los productos
def cargar_csv(nombre_archivo):
    matriz = []
    # si no encuentra el archivo no quiero que se rompa, arranca vacio
    try:
        # utf-8 para que lea bien las tildes y la ñ
        archivo = open(nombre_archivo, "r", encoding="utf-8")
    except FileNotFoundError:
        print("No se encontro el archivo", nombre_archivo, "- se empieza vacio.")
        return matriz
    lineas = archivo.readlines()  # me trae todas las lineas en una lista
    archivo.close()
    # arranco en 1 porque la linea 0 es el encabezado
    for i in range(1, len(lineas)):
        # voy armando cada dato caracter por caracter hasta que aparece una coma
        datos = []
        dato = ""
        for caracter in lineas[i]:
            if caracter == ",":
                datos.append(dato)
                dato = ""
            elif caracter != "\n":  # el enter del final no lo quiero
                dato = dato + caracter
        datos.append(dato)  # me falta el ultimo porque despues no hay coma
        # convierto porque del archivo viene todo como texto
        fila = [int(datos[0]), datos[1], datos[2], float(datos[3]), int(datos[4])]
        matriz.append(fila)
    return matriz


# escribe la matriz en el csv con el encabezado primero
def guardar_csv(matriz, nombre_archivo):
    # con "w" lo abro para escribir (pisa lo que habia), tambien en utf-8
    archivo = open(nombre_archivo, "w", encoding="utf-8")
    archivo.write("codigo,nombre,categoria,precio,stock\n")
    for fila in matriz:
        archivo.write(str(fila[0]) + "," + fila[1] + "," + fila[2] + ","
                      + str(fila[3]) + "," + str(fila[4]) + "\n")
    archivo.close()


# desafio opcional: lo mismo pero en formato json
def exportar_json(matriz, nombre_archivo):
    archivo = open(nombre_archivo, "w", encoding="utf-8")
    # ensure_ascii=False es para que guarde las tildes como son y no con codigos raros
    json.dump(matriz, archivo, indent=4, ensure_ascii=False)
    archivo.close()


# ===== ALTA, BAJA Y MODIFICACION =====

# agrega un producto nuevo
# si el codigo ya existe o algun dato esta mal devuelve False
def alta_producto(matriz, codigo, nombre, categoria, precio, stock):
    if codigo <= 0 or nombre == "" or categoria == "" or precio < 0 or stock < 0:
        return False
    pos, comparaciones = busqueda_secuencial(matriz, codigo)
    if pos != -1:  # ya existe ese codigo
        return False
    matriz.append([codigo, nombre, categoria, precio, stock])
    return True


# elimina el producto, si no lo encuentra devuelve False
def baja_producto(matriz, codigo):
    pos, comparaciones = busqueda_secuencial(matriz, codigo)
    if pos == -1:
        return False
    del matriz[pos]
    return True


# le sumo la cantidad al stock (si es negativa resta)
# si el stock queda negativo no lo dejo
def modificar_stock(matriz, codigo, cantidad):
    pos, comparaciones = busqueda_secuencial(matriz, codigo)
    if pos == -1:
        return False
    if matriz[pos][4] + cantidad < 0:
        return False
    matriz[pos][4] = matriz[pos][4] + cantidad
    return True


# ===== BUSQUEDAS =====

# busqueda secuencial: voy fila por fila hasta encontrarlo
# devuelvo la posicion (-1 si no esta) y cuantas comparaciones hice
def busqueda_secuencial(matriz, codigo):
    comparaciones = 0
    for i in range(len(matriz)):
        comparaciones = comparaciones + 1
        if matriz[i][0] == codigo:
            return i, comparaciones
    return -1, comparaciones


# busqueda binaria: la matriz tiene que estar ordenada por codigo
# miro el del medio, si el que busco es mas grande me quedo con la mitad
# de la derecha y si es mas chico con la de la izquierda
def busqueda_binaria(matriz, codigo):
    comparaciones = 0
    izq = 0
    der = len(matriz) - 1
    while izq <= der:
        medio = (izq + der) // 2
        comparaciones = comparaciones + 1
        if matriz[medio][0] == codigo:
            return medio, comparaciones
        elif matriz[medio][0] < codigo:
            izq = medio + 1
        else:
            der = medio - 1
    return -1, comparaciones


# ===== ORDENAMIENTOS (de menor a mayor segun la columna) =====

# seleccion: busco el menor de lo que queda y lo paso adelante
def ordenar_seleccion(matriz, columna):
    for i in range(len(matriz) - 1):
        menor = i
        for j in range(i + 1, len(matriz)):
            if matriz[j][columna] < matriz[menor][columna]:
                menor = j
        # lo cambio de lugar con el de la posicion i
        aux = matriz[i]
        matriz[i] = matriz[menor]
        matriz[menor] = aux
    return matriz


# burbuja: comparo cada uno con el de al lado y si estan al reves los doy vuelta
# en cada pasada el mas grande se va al fondo
def ordenar_burbuja(matriz, columna):
    for i in range(len(matriz) - 1):
        for j in range(len(matriz) - 1 - i):
            if matriz[j][columna] > matriz[j + 1][columna]:
                aux = matriz[j]
                matriz[j] = matriz[j + 1]
                matriz[j + 1] = aux
    return matriz


# ===== REPORTES =====

# devuelve los productos que tienen menos stock que el umbral
def stock_bajo(matriz, umbral):
    lista = []
    for fila in matriz:
        if fila[4] < umbral:
            lista.append(fila)
    return lista


# precio por stock de cada producto, todo sumado
def valor_total(matriz):
    total = 0
    for fila in matriz:
        total = total + fila[3] * fila[4]
    return total


# arranco con el primero como el mas caro y lo cambio si encuentro uno mayor
def producto_mas_caro(matriz):
    mas_caro = matriz[0]
    for fila in matriz:
        if fila[3] > mas_caro[3]:
            mas_caro = fila
    return mas_caro


# igual que el de arriba pero al reves
def producto_mas_barato(matriz):
    mas_barato = matriz[0]
    for fila in matriz:
        if fila[3] < mas_barato[3]:
            mas_barato = fila
    return mas_barato


# imprime los productos uno abajo del otro
def mostrar(matriz):
    if len(matriz) == 0:
        print("No hay productos.")
    for fila in matriz:
        print(fila[0], "-", fila[1], "-", fila[2], "- $", fila[3], "- stock:", fila[4])


# ===== MENU =====

def menu():
    inventario = cargar_csv("inventario.csv")
    print("Se cargaron", len(inventario), "productos.")

    opcion = -1
    while opcion != 0:
        print()
        print("1. Ver inventario")
        print("2. Agregar producto")
        print("3. Eliminar producto")
        print("4. Modificar stock")
        print("5. Buscar por codigo")
        print("6. Ordenar y listar")
        print("7. Productos con stock bajo")
        print("8. Valor total del inventario")
        print("9. Producto mas caro y mas barato")
        print("10. Exportar a JSON")
        print("0. Salir")
        opcion = int(input("Opcion: "))

        if opcion == 1:
            mostrar(inventario)

        elif opcion == 2:
            codigo = int(input("Codigo: "))
            nombre = input("Nombre: ")
            categoria = input("Categoria: ")
            precio = float(input("Precio: "))
            stock = int(input("Stock: "))
            if alta_producto(inventario, codigo, nombre, categoria, precio, stock):
                print("Producto agregado.")
            else:
                print("No se pudo agregar (codigo repetido o datos invalidos).")

        elif opcion == 3:
            codigo = int(input("Codigo a eliminar: "))
            if baja_producto(inventario, codigo):
                print("Producto eliminado.")
            else:
                print("No existe ese codigo.")

        elif opcion == 4:
            codigo = int(input("Codigo: "))
            cantidad = int(input("Cantidad a sumar (negativo para restar): "))
            if modificar_stock(inventario, codigo, cantidad):
                print("Stock actualizado.")
            else:
                print("No se pudo (no existe o el stock quedaria negativo).")

        elif opcion == 5:
            codigo = int(input("Codigo a buscar: "))
            pos, comp_sec = busqueda_secuencial(inventario, codigo)
            # para la binaria primero tengo que ordenar por codigo
            ordenar_seleccion(inventario, 0)
            pos, comp_bin = busqueda_binaria(inventario, codigo)
            if pos == -1:
                print("No existe ese codigo.")
            else:
                mostrar([inventario[pos]])
            print("Comparaciones secuencial:", comp_sec)
            print("Comparaciones binaria:", comp_bin)

        elif opcion == 6:
            criterio = int(input("Ordenar por 1. Nombre  2. Precio  3. Stock: "))
            metodo = int(input("Metodo 1. Seleccion  2. Burbuja: "))
            # paso la opcion al numero de columna
            if criterio == 1:
                columna = 1
            elif criterio == 2:
                columna = 3
            else:
                columna = 4
            if metodo == 1:
                ordenar_seleccion(inventario, columna)
            else:
                ordenar_burbuja(inventario, columna)
            mostrar(inventario)

        elif opcion == 7:
            umbral = int(input("Mostrar productos con stock menor a: "))
            mostrar(stock_bajo(inventario, umbral))

        elif opcion == 8:
            print("Valor total: $", valor_total(inventario))

        elif opcion == 9:
            if len(inventario) > 0:
                print("Mas caro:")
                mostrar([producto_mas_caro(inventario)])
                print("Mas barato:")
                mostrar([producto_mas_barato(inventario)])
            else:
                print("No hay productos.")

        elif opcion == 10:
            exportar_json(inventario, "inventario.json")
            print("Exportado a inventario.json")

        elif opcion != 0:
            print("Opcion incorrecta.")

        # guardo cada vez que se hace algo asi no se pierde nada
        guardar_csv(inventario, "inventario.csv")

    print("Chau!")


# esto es para que el menu arranque solo si ejecuto este archivo
# (cuando lo importa ventana.py no arranca)
if __name__ == "__main__":
    menu()
