from tkinter import *
import pandas as pd 

from procesar import cargar_archivo_nokia,cargar_archivo_postfa, exportarTablaNokia, exportarTablaPostfa, periodoNokia, periodoPostfa
# Function for opening the
# file explorer window

                                                                                                  
# Create the root window
window = Tk()
  
# Set window title
window.title('Conectividad Gestionada')
  
# Set window size
window.geometry("700x500")
  
#Set window background color
window.config(background = "white")

def procesar_archivos():
    tablaNokia = exportarTablaNokia()
    tablaPostfa = exportarTablaPostfa()
    if len(periodoNokia()) > 2 :
        label_file_explorer.configure(text="Dos o mas periodo",fg = "red",width = 100, height = 15)
        raise Exception("Dos o mas Perdiodos")


    if str(periodoNokia()[0]) != str(periodoPostfa()):
        label_file_explorer.configure(text="No coinciden los periodos de Nokia con Postfa",fg = "red",width = 100, height = 15)
        raise Exception("No coinciden los periodos de Nokia con Postfa")
    
    Nokia = tablaNokia.set_index('CUIT')
    Postfa = tablaPostfa.set_index('IDENTIFICACION')


    merge = pd.merge(Nokia, Postfa, how='outer', left_index=True, right_index=True)
    conCeros = merge.fillna('0.0')
    print(conCeros)

    mergeIndex = conCeros.reset_index()
    cuit = mergeIndex['index'].tolist()
    print(mergeIndex)
    totalDeviceCharges = mergeIndex['total_device_charges'].tolist()
    valor = mergeIndex['VALOR'].tolist()

    indice = 0
    listDesvio = []

    while len(cuit) > indice :
        if cuit[indice].startswith('-'):
            listDesvio.append('CUIT INVALIDO')
        elif (float(totalDeviceCharges[indice]) == 0.0) & (float(valor[indice]) == 0.0):
            listDesvio.append('IN TESTING')    
        elif totalDeviceCharges[indice] == valor[indice]:
            listDesvio.append('OK')
        elif  float(valor[indice]) - 1 < float(totalDeviceCharges[indice]) <  float(valor[indice]) + 1:
            listDesvio.append('OK-REDONDEO')
        elif totalDeviceCharges[indice] != valor[indice]:
            listDesvio.append('ERROR EN LA FACTURACION')
        else:
            listDesvio.append('VER PROBLEMA')
        indice +=1


    tablaFinal = mergeIndex.assign(RESULTADO = listDesvio)

    tablaFinal.to_excel(f'./TablaFinal{periodoNokia()}.xlsx')
    label_file_explorer.configure(text="Tabla final lista en directorio",fg = "green",width = 100, height = 15)
  
# Create a File Explorer label
label_file_explorer = Label(window,
                            text = "Facturacion de Conectividad Gestionada",
                            width = 100, height = 4,
                            fg = "blue")
  

button_explore_nokia = Button(window,
                        text = "Cargar Archivo Nokia",
                        command = cargar_archivo_nokia)
button_explore_post = Button(window,
                        text = "Cargar Archivo Postfa",
                        command = cargar_archivo_postfa)
button_explore_procesar = Button(window,
                        text = "Procesar!!!",
                        command = procesar_archivos)

button_exit = Button(window,
                     text = "Exit",
                     command = exit)
  
# Grid method is chosen for placing
# the widgets at respective positions
# in a table like structure by
# specifying rows and columns
label_file_explorer.grid(column = 1, row = 1)
  
button_explore_nokia.grid(column = 1, row = 2)
button_explore_post.grid(column = 1, row = 3)
button_explore_procesar.grid(column = 1, row = 4)
button_exit.grid(column = 1,row = 8)
  
# Let the window wait for any events
window.mainloop()

