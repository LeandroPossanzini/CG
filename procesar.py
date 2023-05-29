import pandas as pd
import tkinter as tk
from tkinter import filedialog


def cargar_archivo_n():
    ruta_archivo = filedialog.askopenfilename(filetypes= (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    if ruta_archivo:
        df = pd.read_csv(ruta_archivo, delimiter=';')
        return df
    else:
        return None

def cargar_archivo_e():
    ruta_archivo = filedialog.askopenfilename(filetypes= (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    if ruta_archivo:
        df = pd.read_excel(ruta_archivo)
        return df
    else:
        return None
    
# Función para manejar el evento de clic del botón "Cargar archivo 1"
def cargar_archivo_nokia():
    global df1
    df1 = cargar_archivo_n()
    

# Función para manejar el evento de clic del botón "Cargar archivo 2"
def cargar_archivo_postfa():
    global df2
    df2 = cargar_archivo_e()
    

def obtenerListaLiquidacion():
    global df1
    dfNuevo = df1.groupby([('external_cost_center'),'wing_customer_name']).total_device_charges.sum()
    dfNuevoFrame = dfNuevo.to_frame().astype(str)
    dfReseteado = dfNuevoFrame.reset_index()
    dfConIndex = dfReseteado.set_index("external_cost_center")

    #CUIC QUE SI O SI TIENEN $COSTOS 
    lista = dfConIndex.index
    listaCuic = []
    for x in lista:
        converString = str(x)
        try:
            if converString.endswith('.0'):
                sinPunto = converString.split(sep='.0', maxsplit=1)
                cuitFinal = sinPunto[0]
                if( len(cuitFinal) > 10 ):
                    if cuitFinal.startswith('10'):
                            sinDiez = cuitFinal.split(sep='10', maxsplit=1)
                            listaCuic.append(sinDiez[1])
                    else:
                        listaCuic.append(cuitFinal)
                else:
                    listaCuic.append('-'+ cuitFinal)
            else:
                if( len(converString) > 10 ):
                    if converString.startswith('10'):
                            sinDiez = converString.split(sep='10', maxsplit=1)
                            listaCuic.append(sinDiez[1])
                    else:
                        listaCuic.append(converString)
                else:
                    listaCuic.append('-'+ converString)
        except:
            print("Except")      
    return listaCuic

def exportarTablaNokia ():
    dfNuevo = df1.groupby([('external_cost_center'),'wing_customer_name']).total_device_charges.sum()
    dfNuevoFrame = dfNuevo.to_frame().astype(str)
    dfReseteado = dfNuevoFrame.reset_index()
    tablaFinalNokiaF = dfReseteado.assign(CUIT = obtenerListaLiquidacion())
    tablaFinalNokiaF = tablaFinalNokiaF.set_index("CUIT")
    return tablaFinalNokiaF.reset_index()

def periodoNokia () :
    listaPeriodos = df1['bill_period'].tolist()
    return list(set(listaPeriodos))


def exportarTablaPostfa () :
    global df2
    tablaPostfa = df2

    nuevaTabla = tablaPostfa[(tablaPostfa.CONCDESC == 'Gestor SIMs IoT Datos') | (tablaPostfa.CONCDESC == 'Gestor SIMs IoT P. MÃ³vil') | (tablaPostfa.CONCDESC == 'Gestor SIMs IoT P. Datos') | (tablaPostfa.CONCDESC == 'Gestor SIMs IoT SMS')]
    lista = nuevaTabla['IDENTIFICATION'].tolist()
    listaNUeva = []
    for x in lista:
        listaNUeva.append(str(x))
    tablaPostfaIot = nuevaTabla.assign(IDENTIFICACION = listaNUeva)
    dfAgrupado = tablaPostfaIot.groupby('IDENTIFICACION').VALOR.sum()
    dfToFrame = dfAgrupado.to_frame().astype(str)
    return dfToFrame.reset_index()

def periodoPostfa () :
    global df2
    tablaPostfa = df2

    nuevaTabla = tablaPostfa[(tablaPostfa.CONCDESC == 'Gestor SIMs IoT Datos') | (tablaPostfa.CONCDESC == 'Gestor SIMs IoT P. MÃ³vil') | (tablaPostfa.CONCDESC == 'Gestor SIMs IoT P. Datos') | (tablaPostfa.CONCDESC == 'Gestor SIMs IoT SMS')]
    lista = nuevaTabla['IDENTIFICATION'].tolist()
    listaNUeva = []
    for x in lista:
        listaNUeva.append(str(x))
    tablaPostfaIot = nuevaTabla.assign(IDENTIFICACION = listaNUeva)
    listaPeriodos = tablaPostfaIot['CARGFECR'].tolist()[0]
    listaCortada = listaPeriodos.split("-",2)
    periodoFinal = listaCortada[0]+listaCortada[1]
    return (periodoFinal)


def procesar_archivos():
    tablaNokia = exportarTablaNokia()
    tablaPostfa = exportarTablaPostfa()
    if len(periodoNokia()) > 2 :
        raise Exception("Dos o mas periodos")


    if str(periodoNokia()[0]) != str(periodoPostfa()):
        raise Exception("No coinciden los periodos de Nokia con Postfa")
    
    Nokia = tablaNokia.set_index('CUIT')
    Postfa = tablaPostfa.set_index('IDENTIFICACION')


    merge = pd.merge(Nokia, Postfa, how='outer', left_index=True, right_index=True)
    conCeros = merge.fillna('0.0')


    mergeIndex = conCeros.reset_index()
    cuit = mergeIndex['index'].tolist()
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