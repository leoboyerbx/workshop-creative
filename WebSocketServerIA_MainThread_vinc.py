from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import socket
import numpy as np
import os
import matplotlib.pyplot as plt
from glob import glob
import shutil
from time import sleep, strftime, time
import turtle

from random import randint
import threading

turtle.penup()
turtle.goto(-200, -200)
turtle.setheading(45)
turtle.pendown()

# ----------------------------------------------
# Needs to be global
# ----------------------------------------------

values = []
fileName = ""
folderPath = os.getcwd()

plt.ion()
x = []
y = []
previous = 0

angle = 0
speed = 0


def graph(acc):
    y.append(acc[0])
    x.append(time())
    if len(y) % 6 == 0:
        plt.clf()
        plt.scatter(x, y)
        plt.plot(x, y)
        plt.pause(0.00001)


# previous = len(y)

def saveFile(fname, val):
    print(fname)
    with open(fname, 'w+') as f:
        for item in val:
            f.write("%s\n" % item)
        values.clear()


def transferDidFinish(classNames):
    values.clear()
    fileName = ""
    tpName = ""
    print("C'est ici que tu vas regarder...")


# ----------------------------------------------

class FileSharingServer(WebSocket):
    global angle
    global speed

    def handleMessage(self):
        if "#" in self.data:
            print("End of file " + self.data)
            fileName = self.data
            fileNameTarget = fileName.replace("#", "")
            saveFile(fileNameTarget, values)
            self.sendMessage("Fs")

        elif "|" in self.data:
            cNames = self.data.replace("|", "")
            classes = cNames.split(';')
            tpName = classes.pop()
            print(classes)
            print(folderPath)
            print(tpName)
            filesPath = []
            tpFolderPath = folderPath + "/" + tpName
            print(tpFolderPath)
            try:
                os.mkdir(tpFolderPath)
            except OSError:
                print("Creation of the directory %s failed" % tpFolderPath)
            else:
                print("Successfully created the directory %s " % tpFolderPath)
            print("After path")
            for name in classes:
                fileList = glob(name + '*.txt')
                print(fileList)
                path = tpFolderPath + "/" + name
                print(path)
                try:
                    os.mkdir(path)
                except OSError:
                    print("Creation of the directory %s failed" % path)
                else:
                    print("Successfully created the directory %s " % path)

                for file in fileList:
                    newPath = path + "/" + file
                    shutil.move("./" + file, newPath)
                    filesPath.append(newPath)

            self.sendMessage("Tf")
            transferDidFinish(classes)

        elif "$" in self.data:
            tpName = self.data.replace("$", "")
            print(tpName)

        elif ">" in self.data:
            axes = self.data.replace(">", "")
            axesValue = axes.split(';')
            print(axesValue[0])
            global angle
            global speed
            if float(axesValue[1]) > 100:
                speed = 3
            elif float(axesValue[1]) < -100:
                speed = -3
            else:
                angle = 0

        else:
            print("Appending")
            print(self.data)
            values.append(self.data)
            print(len(values))

    def handleConnected(self):
        print(self.address, "Connected")

    def handleClose(self):
        print(self.address, "Closed")


from threading import Timer


class perpetualTimer():

    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def tickUpdate(msg="foo"):
    turtle.left(angle)
    turtle.forward(speed)


def connection():
    port = 8080
    server = SimpleWebSocketServer('', port, FileSharingServer)
    print("Running on: " + " Port: " + str(port))
    server.serveforever()


from threading import *

t = Thread(target=connection)
t.start()

while True:
    tickUpdate()
    sleep(0.01)

# hostname = socket.gethostname()
# IPAddr = socket.gethostbyname(hostname)




