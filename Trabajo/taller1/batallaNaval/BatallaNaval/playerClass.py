from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import tkinter.ttk as ttk

from tileStatesClass import TileStates

'''
Clase para los jugadores de la partida
Usa dos matrices para representar cada tablero, y dos matrices para el manejo de la interfaz
Las acciones de la partida se representan como metodos de esta clase
'''


class Player():
    '''
    Constructor de la clase Player
    Parametros:
        self: necesario para todos los metodos, hace referencia a si mismo
        oceanGrid: matriz para representar el tablero donde se pondran los barcos
        targetGrid: matriz para representar el tablero donde se dispara
        oceanLabels: matriz de Labels de Tkinter para el tablero de los barcos
        targetLabels: matriz de Labels de TKinter para el tablero de los disparos
        name: nombre del jugador, usado para las estadisiticas y los mensajes
        isMachine: booleano que representa si el jugador es una maquina o no
    '''

    def __init__(self, oceanGrid, targetGrid, oceanLabels, targetLabels, name, isMachine):
        self.oceanGrid = oceanGrid
        self.targetGrid = targetGrid
        self.oceanLabels = oceanLabels
        self.targetLabels = targetLabels
        self.name = name
        # Inicia las estadisticas en 0
        self.firedShots = 0
        self.hitShots = 0
        self.placedShips = 0
        # Listas para representar el nombre y la vida de los barcos del jugador
        self.ships = ["Portaviones", "Acorazado", "Crucero", "Submarino", "Destructor"]
        self.shipHealths = [5, 4, 3, 3, 2, ]
        self.isMachine = isMachine
        # Diccionario que guarda por barco la ubicacion y la direccion en la que esta
        self.locations = {}

    '''
    Metodo para que un jugador dispare a otro usando coordenadas
    Parametros:
        self: representa al jugador que va a hacer el disparo
        other: representa al jugador que va a recibir el disparo
        x: coordenada en x en la que se va a disparar
        y: coordenada en y en la que se va a disparar
    Salida: Un string con el resultado del disparo
    '''

    def fire(self, other, x, y):
        # Actualiza la estadistica de la cantidad de disparos 
        self.firedShots += 1
        # Guarda el valor que hay en el tablero de los barcos del otro jugador
        otherTile = other.oceanGrid[x][y]
        # Lista de todos los valores de TileStates que representan un barco
        shipTiles = [TileStates.Portaviones, TileStates.Acorazado,
                     TileStates.Crucero, TileStates.Submarino, TileStates.Destructor]

        # Revisa si las coordenadas a las que se disparo tienen un barco
        if (otherTile.value in range(5, 10)):
            # Actualiza los estados de las matrices y las estadisticas de ambos jugadores
            self.targetGrid[x][y] = TileStates.HitShot
            other.oceanGrid[x][y] = TileStates(otherTile.value + 5)
            self.hitShots += 1
            # Indice para acceder a las listas de los barcos
            shipArrIndex = otherTile.value - 5
            other.shipHealths[shipArrIndex] -= 1

            # Si el barco impactado ya no tiene vida, devuelve el mensaje de hundido
            if other.shipHealths[shipArrIndex] == 0:
                return other.ships[shipArrIndex] + " Hundido!"
            # Si aun tiene vida, devuelve el mensaje de impacto
            else:
                return "Impacto en " + other.ships[shipArrIndex]
        # Si no hay un barco, el disparo es fallido
        else:
            self.targetGrid[x][y] = TileStates.MissedShot
            other.oceanGrid[x][y] = TileStates.MissedShot
            return "Disparo fallido"

    '''
    Metodo para que el jugador ponga un barco en su tablero usando las 
    coordenadas y la direccion
    Parametros:
        self: representa al jugador que va a poner el barco
        ship: string con el nombre del barco que se va a poner
        x: coordenada en x donde se va a poner el barco
        y: coordenada en y donde se va a poner el barco
        direction: direccion hacia la cual va a apuntar el barco (N, E, S, W)
    Salida: Un valor booleano
        True: si el barco de ubico correctamente
        False: si no se pudo ubicar el barco
    '''

    def placeShip(self, ship, x, y, direction):
        # Lista de los estados de TileStates que representan un barco
        shipTiles = [TileStates.Portaviones, TileStates.Acorazado,
                     TileStates.Crucero, TileStates.Submarino, TileStates.Destructor]

        # Determina la longitud del barco y su tipo basandose en el parametro ship
        # shipType es igual al numero que representa el TileState de ese barco
        shipLength = 0
        shipType = 0
        if ship == "Portaviones":
            shipLength = 5
            shipType = 5
        if ship == "Acorazado":
            shipLength = 4
            shipType = 6
        if ship == "Crucero":
            shipLength = 3
            shipType = 7
        if ship == "Submarino":
            shipLength = 3
            shipType = 8
        if ship == "Destructor":
            shipLength = 2
            shipType = 9

        # Genera una lista con las coordenadas a cambiar usando la longitud y la direccion
        coordsToChange = []
        for i in range(shipLength):
            if direction == "N":
                coordsToChange.append((x, y - i))
            if direction == "E":
                coordsToChange.append((x + i, y))
            if direction == "S":
                coordsToChange.append((x, y + i))
            if direction == "W":
                coordsToChange.append((x - i, y))

        # Revisa todas las coordenadas a cambiar
        for coord in coordsToChange:
            currentX = coord[0]
            currentY = coord[1]
            # Si la coordenada esta por fuera del tablero, devuelve False
            if currentX not in range(10) or currentY not in range(10):
                return False

            currentTile = self.oceanGrid[currentX][currentY]
            # Si ya hay un barco en la coordenada, devuelve False
            if (currentTile in shipTiles):
                return False

        # if self.isMachine:
        #     print(coordsToChange)

        # Si llego aqui, las ubicaciones son correctas
        # Actualiza el tablero de los barcos del jugador usando el tipo y devuelve True
        for coord in coordsToChange:
            self.oceanGrid[coord[0]][coord[1]] = TileStates(shipType)

        # Guarda la ubicacion en el diccionario
        self.locations[ship] = {"x": x, "y": y, "direction": direction}
        self.placedShips += 1
        return True
