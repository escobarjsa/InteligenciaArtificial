from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import tkinter.ttk as ttk
from random import randint
from functools import partial
import json
from datetime import datetime
import os
import sys
import matplotlib.pyplot as plt
import numpy as np

import matplotlib.animation as animation
import animatplot as amp
import opc as opc
import self as self

from playerClass import Player
from tileStatesClass import TileStates

'''
Funcion para generar una matriz de 10x10 donde todos los elementos
son TileStates.Empty para representar los tableros al inicio de la partida
Salida: la matriz generada
'''


def generateGrid():
    # grid representa toda la matriz
    grid = []
    for i in range(10):
        # column representa una columna en la matriz
        column = []
        for j in range(10):
            # Se añade el estado de Empty a la columna
            column.append(TileStates.Empty)
        # Se añade la columna a la matriz completa
        grid.append(column)

    # Despues de construirla toda, devuelve la matriz
    return grid


'''
Funcion para generar una matriz de 10x10 donde todos los elementos son botones
para representar la interfaz
Salida: la matriz generada
'''


def generateButtonGrid():
    # Funciona de igual manera que la funcion generateGrid, pero con buttons
    grid = []
    for i in range(10):
        column = []
        for j in range(10):
            # El button esta asociado a window, que es la ventana de Tkinter definida en global
            button = Button(window, width=1, height=1)
            button.configure(activebackground=button.cget('background'))
            column.append(button)
        grid.append(column)

    return grid


'''
Funcion para ubicar en la pantalla los labels de un jugador
Parametros:
    player: representa al jugador cuyos labels sera ubicados
'''


def placeLabels(player):
    # Recorre la matriz de los labels usando las coordenadas
    for xCoord in range(10):
        for yCoord in range(10):
            # Usa las coordenadas de la matriz para hallar las de la pantalla
            player.oceanLabels[xCoord][yCoord].place(x=((xCoord * 30) + 30),
                                                     y=((yCoord * 30) + 30))
            player.targetLabels[xCoord][yCoord].place(x=((xCoord * 30) + 360),
                                                      y=((yCoord * 30) + 30))


'''
Convierte una letra a un numero que puede ser usado como coordenada de las matrices
Parametros:
    letter: la letra a convertir
Salida: un numero que esta en un rango de 0 a 9, cuyo valor se usa para las coordenadas
'''


def letterToNum(letter):
    # Convierte la letra a mayusculas para evitar errores
    letter = letter.upper()
    # Devuelve el valor deseado basandose en la letra
    if letter == "A":
        return 0
    if letter == "B":
        return 1
    if letter == "C":
        return 2
    if letter == "D":
        return 3
    if letter == "E":
        return 4
    if letter == "F":
        return 5
    if letter == "G":
        return 6
    if letter == "H":
        return 7
    if letter == "I":
        return 8
    if letter == "J":
        return 9


'''
Funcion para generar de manera aleatoria unas coordenadas para la maquina
Salida: un tuple con las coordendas generadas de la forma (x, y)
'''


def genMachineCoords():
    xCoord = randint(0, 9)
    yCoord = randint(0, 9)

    return (xCoord, yCoord)


'''
Funcion para generar las coordenadas necesarias para los eventos de la partida
Parametros:
    player: representa el jugador para el que se generaran las coordendas
Salida: un tuple con las coordendas generadas de la forma (x, y)
'''


def getCoords(player):
    xCoord = 0
    yCoord = 0
    # Revisa si el jugador es una maquina o no
    if not (player.isMachine):
        # Si no lo es, halla las coordenadas usando los valores de los campos de la interfaz
        coordLetter = letterField.get()
        coordNum = int(numField.get())

        # Convierte la letra al numero para la coordenada usando la funcion definida antes
        xCoord = letterToNum(coordLetter)
        # Le resta uno a la coordenada ya que las listas inician en 0 y el tablero en 1
        yCoord = coordNum - 1
    else:
        # Si es una maquina, usa la funcion definida antes para hallar las coordendas
        xCoord, yCoord = genMachineCoords()

    # Devuelve el tuple con las coordenadas
    return (xCoord, yCoord)


'''
Funcion para actualizar el color de los labels de un jugador
Parametros:
    player: representa el jugador cuyos labels seran actualizados
'''


def renderGrid(player):
    # Recorrre las matrices usando coordenadas
    for x in range(10):
        for y in range(10):
            # Guarda y revisa el estado de la casilla de los barcos
            oceanTile = player.oceanGrid[x][y]
            # Si hay un barco, pinta el label de naranja
            if oceanTile.value in range(5, 10):
                player.oceanLabels[x][y].configure(background="orange")
            # Si hay un barco impactado, pinta el label de verde
            elif oceanTile.value in range(10, 15):
                player.oceanLabels[x][y].configure(background="green")
            # Si hay un disparo fallido, pinta el label de negro
            elif oceanTile == TileStates.MissedShot:
                player.oceanLabels[x][y].configure(background="black")
            # Si no hay nada, pinta el label de blanco
            else:
                player.oceanLabels[x][y].configure(background="white")

            # Guarda y revisa el estado de la casilla de los disparos
            targetTile = player.targetGrid[x][y]
            # Si hay un disparo fallido, pinta el label de negro
            if targetTile == TileStates.MissedShot:
                player.targetLabels[x][y].configure(background="black")
            # Si hay un disparo acertado, pinta el label de amarillo
            elif targetTile == TileStates.HitShot:
                player.targetLabels[x][y].configure(background="yellow")
            # Si no se ha disparado ahi, pinta el label de blanco
            elif targetTile == TileStates.Empty:
                player.targetLabels[x][y].configure(background="white")


'''
Funcion para revisar si un jugador ya gano la partida y guardar las estadisticas de esta
Parametros:
    player1: representa el jugador a revisar
    player2: representa el jugador que puede haber perdido la partida
Salida: Un valor booleando
    True: Si player ya gano la partida
    False: Si player no ha ganado la partida
'''


def checkWin(player1, player2):
    # Revisa si ya se acertaron todos los disparos
    # 17 es la suma de las vidas de todos los barcos
    if player1.hitShots == 17:
        # Si ya se hizo, guarda las estadisticas de la partida en data.json
        data = None
        try:
            with open("data.json", "r") as f:
                # Lee los datos del json y los guarda como un diccionario
                data = f.read()
        # Si el archivo no existe, lo crea
        except IOError:
            file = open("data.json", "w")

        with open("data.json", "w+") as f:
            try:
                obj = json.loads(data)
            except:
                obj = {}

            # Revisa si ya existen los datos del ganador en el json
            if player1.name in obj:
                # Si lo hacen, los actualiza
                obj[player1.name]["wins"] += 1
                # Revisa si los disparos de esta partida eran menores que los anteriores
                if player1.firedShots < obj[player1.name]["minShots"]:
                    obj[player1.name]["minShots"] = player1.firedShots
            else:
                # Si no, los crea con los datos de la partida
                obj[player1.name] = {"wins": 1, "losses": 0, "minShots": player1.firedShots}

            # Revisa si los datos del perdedor ya existian en el json
            if player2.name in obj:
                # Si lo hacian, los actualiza
                obj[player2.name]["losses"] += 1
            else:
                # Si no, los crea
                # Se pone minShots en 101, ya que el maximo numero de disparos es 100
                # Esto se debe a que las matrices son de 10x10
                # Por lo tanto, si se disparara en todas las casillas, llegaria a 100
                obj[player2.name] = {"wins": 0, "losses": 1, "minShots": 101}
            f.write(json.dumps(obj, indent=4))

        # Devuelve verdadero
        return True
    else:
        # Si no, devuelve falso
        return False


'''
Funcion para la animacion 1
'''


def animation1(self):
    x = np.linspace(0, 1, 50)
    t = np.linspace(0, 1, 20)

    X, T = np.meshgrid(x, t)
    Y = np.tan(3 * np.pi * (X + T))

    block = amp.blocks.Line(x, Y, marker="", linestyle="-", color="r")
    anim = amp.Animation([block])
    animation.show()


'''
Funcion para la animacion 2
'''


def animation2(self):
    x = np.linspace(0, 1, 50)
    t = np.linspace(0, 1, 20)

    X, T = np.meshgrid(x, t)
    Y = np.tan(3 * np.pi * (X + T))

    block = amp.blocks.Line(x, Y, marker="", linestyle="-", color="r")
    anim = amp.Animation([block])
    animation.show()


'''
Funcion para manejar el evento de disparar, se usara en un boton de la interfaz
Parametros:
    player1: representa el primer jugador de la partida (el jugador local)
    player2: representa el segundo jugador de la partida
'''


def fireEventButtons(player1, player2, x, y):
    # Crea una tupla con las coordenadas del evento
    coords = (x, y)
    # Revisa si las coordenadas estan dentro del tablero y no se ha disparado ahi antes
    if ((coords[0] in range(10)) and (coords[1] in range(10))
            and (player1.targetGrid[coords[0]][coords[1]] == TileStates.Empty)):
        # Si las coordenadas son validas, realiza el disparo
        shotText = player1.fire(player2, coords[0], coords[1])
        # Actualiza un label con el mensaje que devuelve el metodo fire
        shotsLabel.configure(text=shotText)
        # Actualiza la pantalla
        renderGrid(player1)

        # Revisa si el jugador player1 gano la partida
        # Falta agregar foto de cuando gane el jugador 1
        if checkWin(player1, player2):
            messagebox.showinfo("Resultados", "El ganador es " + player1.name + "!")
            animation1(self)
            # Luego de cerrar el mensaje, vuelve al menu de inicio
            restartGame(player1, player2)

        # Recibe las coordenadas para el jugador player2
        # Falta agregar foto de cuando gane el jugador 2
        coords = getCoords(player2)
        # Las seguira generando mientras estas no sean validas
        while not ((coords[0] in range(10)) and (coords[1] in range(10))
                   and (player2.targetGrid[coords[0]][coords[1]] == TileStates.Empty)):
            coords = getCoords(player2)

        # Realiza el disparo
        player2.fire(player1, coords[0], coords[1])
        # Actualiza la pantalla
        renderGrid(player1)
        # Revisa si el jugador player2 gano la partida
        if checkWin(player2, player1):
            messagebox.showinfo("Resultados", "El ganador es " + player2.name + "!")
            animation2(self)
            # Luego de cerrar el mensaje, vuelve al menu de inicio
            restartGame(player1, player2)
    else:
        # Si las coordenadas son incorrectas, muestra un mensaje de rror
        messagebox.showerror("Error", "Coordenadas incorrectas")
'''

if opc == 1:
    animation1(self)
else:
    animation2(self)
'''
'''
Funcion que no hace nada
'''


def nothing():
    pass


'''
Funcion para pasar de la fase de ubicacion a la fase de disparos
Parametros:
    player1: representa el primer jugador de la partida (el jugador local)
    player2: representa el segundo jugador de la partida
'''


def prepareNextPhase(player1, player2):
    # Revisa si ya estan ubicados todos los barcos de ambos jugadores
    if player1.placedShips == 5 and player2.placedShips == 5:
        # Si lo estan, actualiza los componentes de la interfaz
        infoLabel.configure(text="¡A jugar!, Dispárale a tu contrincante")
        jsonLoadButton.configure(text="Guardar ubicaciones",
                                 command=partial(saveJson, player1))
        changeDirButton.place_forget()

        for x in range(10):
            for y in range(10):
                # Hace que los botones de ubicar no hagan nada
                player1.oceanLabels[x][y].configure(command=nothing)
                # Configura los botones de disparar usando los iteradores para las coordenadas
                player1.targetLabels[x][y].configure(command=partial(fireEventButtons, player1,
                                                                     player2, x, y))


'''
Funcion para leer un archivo JSON con las ubicaciones de los barcos
Entradas:
    player1: representa al jugador para el cual se pondran los barcos
    player2: representa al otro jugador de la partida
'''


def placeJson(player1, player2):
    # Reinicia a los jugadores por si ya se habian puesto barcos antes
    player1 = restartPlayer(player1)
    player2 = restartPlayer(player2)

    # Usa una ventana para leer la ruta al archivo a leer
    coordsFile = filedialog.askopenfilename(initialdir="./locations",
                                            title="Select file",
                                            filetypes=(("JSON files", "*.json"), ("all files", "*.*")))

    # Abre el archivo seleccionado
    with open(coordsFile, "r") as f:
        try:
            # Lee los datos
            data = f.read()
            obj = json.loads(data)
            # Recorre los datos encontrados
            for key, value in obj.items():
                # Usando los datos del json trata de ubicar el barco
                currentShip = key
                # Revisa si el barco de ubico correctamente
                if player1.placeShip(currentShip, value["x"], value["y"], value["direction"]):
                    # Si lo hizo, actualiza la pantalla
                    renderGrid(player1)
                    # Recibe las coordenadas y la direccion para el jugador player2
                    coords = getCoords(player2)
                    if (player2.isMachine):
                        directionArr = ["N", "E", "S", "W"]
                        direction = directionArr[randint(0, 3)]
                    # Ubica el barco para el jugador 2
                    placed = player2.placeShip(currentShip, coords[0], coords[1], direction)
                    # Mientras no se haya ubicado correctamente, repite el proceso
                    while not (placed):
                        coords = getCoords(player2)
                        if (player2.isMachine):
                            directionArr = ["N", "E", "S", "W"]
                            direction = directionArr[randint(0, 3)]
                        placed = player2.placeShip(currentShip, coords[0], coords[1], direction)
                else:
                    # Si no lo hizo, muestra un mensaje de error
                    messagebox.showerror("Error", "Coordenadas incorrectas")
                    # Deshace los cambios que se pueden haber hecho en la ubicacion
                    player1 = restartPlayer(player1)
                    player2 = restartPlayer(player2)
                    renderGrid(player1)
                    # Detiene la funcion
                    return
        except:
            # Si se encontro una excepcion, muestra un error
            messagebox.showerror("Error", "Archivo no valido")

    # Continua a la fase de disparos
    prepareNextPhase(player1, player2)


'''
Funcion para guardar un archivo JSON con las ubicaciones de los barcos del jugador dado
Entradas:
    player: el jugador cuyas ubicaciones seran guardadas
'''


def saveJson(player):
    # Lee la fecha y hora actual para crear el nombre del archivo
    now = datetime.now()
    fileName = player.name + now.strftime("%d%m%y%H%M") + ".json"

    # Si el directorio donde se guardan los archivos no existe, lo crea
    if not os.path.exists("./locations/"):
        os.makedirs("./locations/")

    # Guarda los datos del diccionario de ubicaciones del jugador en la carpeta locations
    f = open("./locations/" + fileName, "w+")
    f.write(json.dumps(player.locations, indent=4))


'''
Funcion para cambiar la direccion en la que se ponen los barcos en la fase de ubicar
'''


def changeDir():
    # Carga la variable que esta en el ambito global
    global myDir

    # Alterna entre las direcciones (derecha y abajo)
    if myDir == "E":
        # Actualiza la variable y el texto del boton
        myDir = "S"
        changeDirButton.configure(text="Direccion: Vertical")
    else:
        # Actualiza la variable y el texto del boton
        myDir = "E"
        changeDirButton.configure(text="Direccion: Horizontal")


'''
Funcion para manejar el evento de ubicar, se usara en un boton de la interfaz
Parametros:
    player1: representa el primer jugador de la partida (el jugador local)
    player2: representa el segundo jugador de la partida
    x: primera coordenada
    y: segunda coordenada
'''


def placeEventButtons(player1, player2, x, y):
    # Crea una tupla con las coordenadas que se le pasan al evento
    coords = (x, y)
    # Recibe la direccion usando la variable global y la almacena
    global myDir
    direction = myDir

    # Recibe cual es el barco a ubicar usando el numero de barcos ubicados
    currentShip = player1.ships[player1.placedShips]
    # Revisa si el barco de ubico correctamente
    if player1.placeShip(currentShip, coords[0], coords[1], direction):
        # Si lo hizo, actualiza la pantalla
        renderGrid(player1)
        # Recibe las coordenadas y la direccion para el jugador player2
        coords = getCoords(player2)
        if (player2.isMachine):
            directionArr = ["N", "E", "S", "W"]
            direction = directionArr[randint(0, 3)]
        # Ubica el barco para el jugador 2
        placed = player2.placeShip(currentShip, coords[0], coords[1], direction)
        # Mientras no se haya ubicado correctamente, repite el proceso
        while not (placed):
            coords = getCoords(player2)
            if (player2.isMachine):
                directionArr = ["N", "E", "S", "W"]
                direction = directionArr[randint(0, 3)]
            placed = player2.placeShip(currentShip, coords[0], coords[1], direction)

        # Si aun quedan barcos por ubicar, actualiza un label de la interfaz
        if player1.placedShips != 5:
            infoLabel.configure(text="Fase de ubicacion: " +
                                     player1.ships[player1.placedShips])
    else:
        # Si no lo hizo, muestra un mensaje de error
        messagebox.showerror("Error", "Coordenadas incorrectas")

    # Trata de seguir a la siguiente fase de la partida
    # Si aun no se han puesto todos los barcos, esta funcion no hara nada
    prepareNextPhase(player1, player2)


'''
Funcion para borrar los componentes de la pantalla
'''


def clearWindow():
    titleLabel.place_forget()
    nameLabel.place_forget()
    player.name = nameField.get()
    nameField.place_forget()
    startButton.place_forget()
    statsButton.place_forget()


'''
Funcion para poner los componentes que se muestran al iniciar el juego
'''


def windowInit():
    titleLabel.place(x=330, y=0)
    nameLabel.place(x=300, y=40)
    nameField.place(x=360, y=40)
    startButton.place(x=400, y=65)
    statsButton.place(x=750, y=330)


'''
Funcion para actualizar la pantalla cuando inicie la partida
'''


def gameInit():
    # Reinicia los jugadores
    restartGame(player, machine)

    # Elimina de la pantalla todos los componenetes que habia al inicio
    clearWindow()

    # Ubica todos los nuevos componentes
    infoLabel.configure(text="Fase de ubicacion: Portaviones")
    infoLabel.place(x=670, y=0)

    oceanLabelA.place(x=40, y=5)
    oceanLabelB.place(x=70, y=5)
    oceanLabelC.place(x=100, y=5)
    oceanLabelD.place(x=130, y=5)
    oceanLabelE.place(x=160, y=5)
    oceanLabelF.place(x=190, y=5)
    oceanLabelG.place(x=220, y=5)
    oceanLabelH.place(x=250, y=5)
    oceanLabelI.place(x=282, y=5)
    oceanLabelJ.place(x=315, y=4)

    oceanLabel1.place(x=7, y=34)
    oceanLabel2.place(x=7, y=64)
    oceanLabel3.place(x=7, y=94)
    oceanLabel4.place(x=7, y=124)
    oceanLabel5.place(x=7, y=154)
    oceanLabel6.place(x=7, y=184)
    oceanLabel7.place(x=7, y=214)
    oceanLabel8.place(x=7, y=244)
    oceanLabel9.place(x=7, y=274)
    oceanLabel10.place(x=5, y=304)

    targetLabelA.place(x=370, y=5)
    targetLabelB.place(x=400, y=5)
    targetLabelC.place(x=430, y=5)
    targetLabelD.place(x=460, y=5)
    targetLabelE.place(x=490, y=5)
    targetLabelF.place(x=520, y=5)
    targetLabelG.place(x=550, y=5)
    targetLabelH.place(x=580, y=5)
    targetLabelI.place(x=613, y=5)
    targetLabelJ.place(x=644, y=4)

    targetLabel1.place(x=340, y=34)
    targetLabel2.place(x=340, y=64)
    targetLabel3.place(x=340, y=94)
    targetLabel4.place(x=340, y=124)
    targetLabel5.place(x=340, y=154)
    targetLabel6.place(x=340, y=184)
    targetLabel7.place(x=340, y=214)
    targetLabel8.place(x=340, y=244)
    targetLabel9.place(x=340, y=274)
    targetLabel10.place(x=337, y=304)

    shotsLabel.place(x=670, y=150)

    jsonLoadButton.place(x=0, y=330)
    changeDirButton.place(x=145, y=330)

    backButton.configure(command=partial(restartGame, player, machine))
    backButton.place(x=769, y=330)

    # Usa las funciones para generar los tableros en la pantalla
    placeLabels(player)
    renderGrid(player)

    for x in range(10):
        for y in range(10):
            player.oceanLabels[x][y].configure(command=partial(placeEventButtons, player,
                                                               machine, x, y))
            player.targetLabels[x][y].configure(command=nothing)


'''
Funcion para cargar las estadisticas del juego
Salida: un diccionario que contiene las estadisticas
'''


def loadStats():
    # Lee los datos del archivo
    data = None
    with open("data.json", "r") as f:
        data = f.read()

    # Intenta cargar los datos como un diccionario
    try:
        obj = json.loads(data)
    except:
        # Si hay un error, deja el diccionario vacio
        obj = {}

    # Devuelve los datos
    return obj


'''
Funcion para generar la pantalla de estadisiticas
'''


def readyStatWindow():
    # Recibe los datos del archivo json para las estadisticas
    obj = loadStats()
    # Crea una lista con los nombres de los jugadores en las estidisticas
    vals = []
    for key, value in obj.items():
        vals.append(key)

    # Hace que los values del Combobox sean los nombres
    playerSelector["values"] = vals

    # Actualiza la pantalla
    clearWindow()

    playerLabel.place(x=10, y=10)
    playerSelector.place(x=10, y=40)
    selectButton.place(x=10, y=70)
    backButton.place(x=769, y=330)

    showRanking()


'''
Funcion para mostrar en pantalla las estadisticas del jugador seleccionado
'''


def showStats():
    # Carga las estadisticas del jugador seleccionado
    obj = loadStats()
    chosenPlayer = obj[playerSelector.get()]

    # Actualiza la pantalla con los datos del jugador
    chosenNameLabel.place(x=250, y=30)
    winsLabel.place(x=250, y=50)
    lossesLabel.place(x=250, y=70)
    bestGameLabel.place(x=250, y=90)

    chosenNameLabel.configure(text=playerSelector.get())
    winsLabel.configure(text="Partidas Ganadas: " + str(chosenPlayer["wins"]))
    lossesLabel.configure(text="Partidas Perdidas: " + str(chosenPlayer["losses"]))
    # Verifica si existe una partida ganada o no
    if chosenPlayer["minShots"] == 101:
        bestGameLabel.configure(text="Mejor Partida: -")
    else:
        bestGameLabel.configure(text="Mejor Partida: " + str(chosenPlayer["minShots"]) +
                                     " Disparos")


'''
Funcion para ocultar los componentes de la pantalla de estadisticas
'''


def hideStats():
    # Elimina los componentes de la pantalla
    playerLabel.place_forget()
    playerSelector.place_forget()
    selectButton.place_forget()
    chosenNameLabel.place_forget()
    winsLabel.place_forget()
    lossesLabel.place_forget()
    bestGameLabel.place_forget()
    backButton.place_forget()

    rankingMessage.place_forget()
    for label in rankingLabels:
        label.place_forget()

    # Cargala pantalla de inicio
    windowInit()


'''
Funcion para reiniciar el estado de un jugador
Entrada:
    player: el jugador a reiniciar

Salida: el jugador reiniciado
'''


def restartPlayer(player):
    # Pone los atributos en su valor por defecto
    player.oceanGrid = generateGrid()
    player.targetGrid = generateGrid()
    player.firedShots = 0
    player.hitShots = 0
    player.placedShips = 0
    player.shipHealths = [5, 4, 3, 3, 2, ]

    # Devuelve el jugador actualizado
    return player


'''
Funcion para reiniciar la partida una vez haya empezado
'''


def restartGame(player1, player2):
    # Elimina de la pantalla los componentes
    infoLabel.place_forget()

    oceanLabelA.place_forget()
    oceanLabelB.place_forget()
    oceanLabelC.place_forget()
    oceanLabelD.place_forget()
    oceanLabelE.place_forget()
    oceanLabelF.place_forget()
    oceanLabelG.place_forget()
    oceanLabelH.place_forget()
    oceanLabelI.place_forget()
    oceanLabelJ.place_forget()

    oceanLabel1.place_forget()
    oceanLabel2.place_forget()
    oceanLabel3.place_forget()
    oceanLabel4.place_forget()
    oceanLabel5.place_forget()
    oceanLabel6.place_forget()
    oceanLabel7.place_forget()
    oceanLabel8.place_forget()
    oceanLabel9.place_forget()
    oceanLabel10.place_forget()

    targetLabelA.place_forget()
    targetLabelB.place_forget()
    targetLabelC.place_forget()
    targetLabelD.place_forget()
    targetLabelE.place_forget()
    targetLabelF.place_forget()
    targetLabelG.place_forget()
    targetLabelH.place_forget()
    targetLabelI.place_forget()
    targetLabelJ.place_forget()

    targetLabel1.place_forget()
    targetLabel2.place_forget()
    targetLabel3.place_forget()
    targetLabel4.place_forget()
    targetLabel5.place_forget()
    targetLabel6.place_forget()
    targetLabel7.place_forget()
    targetLabel8.place_forget()
    targetLabel9.place_forget()
    targetLabel10.place_forget()

    shotsLabel.configure(text="")
    shotsLabel.place_forget()

    jsonLoadButton.configure(text="Cargar ubicaciones",
                             command=partial(placeJson, player, machine))
    jsonLoadButton.place_forget()

    changeDirButton.place_forget()

    backButton.configure(command=hideStats)
    backButton.place_forget()

    # Recorre la matriz de los labels usando las coordenadas
    for xCoord in range(10):
        for yCoord in range(10):
            # Elimina de la pantalla los labels
            player1.oceanLabels[xCoord][yCoord].place_forget()
            player1.targetLabels[xCoord][yCoord].place_forget()

    # Reinicia a los jugadores
    player1 = restartPlayer(player1)
    player2 = restartPlayer(player2)

    # Carga la pantalla de incio
    windowInit()


'''
Funcion que retorna el segundo elemento de una lista
Salida: el elemento tomado
'''


def secondElement(list):
    return list[1]


'''
Funcion para mostrar los 5 mejores jugadores segun el numero de victorias
'''


def showRanking():
    # Carga los datos y crea un diccionario con el numero de victorias por jugador
    obj = loadStats()

    winList = []
    for key, value in obj.items():
        winList.append([key, value["wins"]])

    # Ordena la lista de acuerdo al numero de victorias y la pone al reves
    winList.sort(key=secondElement)
    winList = winList[::-1]

    # Toma los 5 primeros jugadores
    top5 = winList[:5]

    # Actualiza la pantalla con el raking
    rankingMessage.place(x=450, y=30)
    for i in range(5):
        # Si hay menos de 5 jugadores en las estadisticas, para al pasarse del rango
        if i > len(top5) - 1:
            break
        rankingLabels[i].place(x=450, y=(20 * i + 50))
        string = str(i + 1) + ". " + top5[i][0] + " - " + str(top5[i][1]) + " Victorias"
        rankingLabels[i].configure(text=string)


# Variable para guardar la ubicacion en la que se pondran los barcos
myDir = "E"

# Ventana de Tkinter para la aplicacion
window = Tk()
window.title("Batalla Naval")
window.geometry("850x360")

# Label para la informacion de la partida
infoLabel = Label(window)

# Labels para las letras y los numeros en los bordes del tablero

# Un set para el tablero de los barcos
oceanLabelA = Label(window, text="A")
oceanLabelB = Label(window, text="B")
oceanLabelC = Label(window, text="C")
oceanLabelD = Label(window, text="D")
oceanLabelE = Label(window, text="E")
oceanLabelF = Label(window, text="F")
oceanLabelG = Label(window, text="G")
oceanLabelH = Label(window, text="H")
oceanLabelI = Label(window, text="I")
oceanLabelJ = Label(window, text="J")

oceanLabel1 = Label(window, text="1")
oceanLabel2 = Label(window, text="2")
oceanLabel3 = Label(window, text="3")
oceanLabel4 = Label(window, text="4")
oceanLabel5 = Label(window, text="5")
oceanLabel6 = Label(window, text="6")
oceanLabel7 = Label(window, text="7")
oceanLabel8 = Label(window, text="8")
oceanLabel9 = Label(window, text="9")
oceanLabel10 = Label(window, text="10")

# Un set para el tablero de los disparos
targetLabelA = Label(window, text="A")
targetLabelB = Label(window, text="B")
targetLabelC = Label(window, text="C")
targetLabelD = Label(window, text="D")
targetLabelE = Label(window, text="E")
targetLabelF = Label(window, text="F")
targetLabelG = Label(window, text="G")
targetLabelH = Label(window, text="H")
targetLabelI = Label(window, text="I")
targetLabelJ = Label(window, text="J")

targetLabel1 = Label(window, text="1")
targetLabel2 = Label(window, text="2")
targetLabel3 = Label(window, text="3")
targetLabel4 = Label(window, text="4")
targetLabel5 = Label(window, text="5")
targetLabel6 = Label(window, text="6")
targetLabel7 = Label(window, text="7")
targetLabel8 = Label(window, text="8")
targetLabel9 = Label(window, text="9")
targetLabel10 = Label(window, text="10")

# Se crean objetos de tipo Player para los jugadores de la partida
player = Player(generateGrid(), generateGrid(), generateButtonGrid(),
                generateButtonGrid(), "Jugador", False)
machine = Player(generateGrid(), generateGrid(), generateButtonGrid(),
                 generateButtonGrid(), "Maquina", True)

# Boton para cambiar la direccion en la que se ponen los barcos
changeDirButton = Button(window, text="Direccion: Horizontal", command=changeDir)

# Label que se usara para mostrar la informacion sobre los disparos
shotsLabel = Label(window, text="")

# Label para el titulo del juego en el menu inicial
titleLabel = Label(window, text="BATALLA NAVAL", font=("Comic Sans MS", 20))

# Componentes para el campo donde el jugador digitara su nombre
nameLabel = Label(window, text="Nombre: ")
nameField = Entry(window)

# Boton para iniciar la partida
startButton = Button(window, text="Comenzar", command=gameInit)

# Boton para mostrar el menu de estadisticas
statsButton = Button(window, text="Estadisticas", command=readyStatWindow)

# Componentes para seleccionar al jugador en la pantalla de estadisticas
playerLabel = Label(window, text="Seleccionar Jugador: ")
playerSelector = ttk.Combobox(window, state="readonly")
selectButton = Button(window, text="Ver estadisticas", command=showStats)

# Componentes para mostrar las estadisticas de un jugador
chosenNameLabel = Label(window)
winsLabel = Label(window)
lossesLabel = Label(window)
bestGameLabel = Label(window)

# Boton para regresar a la pantalla de inicio
backButton = Button(window, text="Regresar", command=hideStats)

# Boton para cargar la ubicacion de los barcos con un archivo JSON
jsonLoadButton = Button(window, text="Cargar ubicaciones",
                        command=partial(placeJson, player, machine))

# Componentes para mostrar el ranking
rankingMessage = Label(window, text="Los 5 mejores jugadores")
rankingLabels = [Label(window), Label(window), Label(window), Label(window), Label(window)]

# Muestra la pantalla de inicio
windowInit()

window.mainloop()
