import random
import turtle
from numpy import sign
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import os
import matplotlib.pyplot as plt
from glob import glob
import shutil
import time


# Settings
screenWidth = 1280
screenHeight = 720

racketSize = 150
# Racket speed
racketOffset = 100

# Screen refresh delay
delay = 0.01666
# Initial ball speed
ballOffset = 8
# Increase speed by 10% each 5 points for the leader, until 25
speedIncreaseFactor = 1.1
speedIncreaseStep = 5
speedIncreaseMax = 25

computerSight = 160
computerSlowness = 8


# Websocket
# ----------------------------------------------
# Needs to be global
# ----------------------------------------------

values = []
fileName = ""
folderPath = os.getcwd()

plt.ion()


class SmoothQueue():
    def __init__(self, size = 4):
        """
        Utilitary class to smooth a queue of values (sliding window)
        :param size: The length of the window
        """
        self.size = size
        self.list = []

    def push(self, val):
        """
        Adds a value in the queue
        :param val:
        """
        if len(self.list) >= self.size:
            self.list.pop(0)
        self.list.append(val)

    def average(self):
        """
        Get the average of the queue
        :return: number
        """
        return sum(self.list) / len(self.list)


sensorY = None
sensorSmoothLength = SmoothQueue(8)

class FileSharingServer(WebSocket):
    def handleMessage(self):
        global rightRacket
        if ">" in self.data:
            try:
                axes = self.data.replace(">", "")
                axesValue = axes.split(';')
                rawValue = min(float(axesValue[0]), 1000)
                rawValue = max(rawValue, -1000)
                global sensorY
                global sensorSmoothLength
                sensorSmoothLength.push(rawValue)
                sensorY = sensorSmoothLength.average()
            except Exception as err:
                print(err)

        else:
            print("Appending")
            print(self.data)
            values.append(self.data)
            print(len(values))

    def handleConnected(self):
        print(self.address, "Connected")

    def handleClose(self):
        print(self.address, "Closed")




def move_racket_up(racket, moveBy=racketOffset):
    """
    Move a racket up by a specified offset
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset
    """
    move_racket(racket, moveBy)


def move_racket_down(racket, moveBy=racketOffset):
    """
    Moves a racket down by a specified offset
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset
    """
    move_racket(racket, -moveBy)


def start_moving_up(racket, moveBy=racketOffset / 5):
    """
    Defines that a racket should be moving up by a specified offset at each tick
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset
    """
    racket.moveBy = moveBy


def start_moving_down(racket, moveBy=racketOffset / 5):
    """
    Defines that a racket should be moving down by a specified offset at each tick
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset
    """
    racket.moveBy = -moveBy


def stop_moving(racket):
    """
    Defines that a racket should not be moving anymore at each tick
    :param racket: The racket (Turtle instance) object to move
    """
    racket.moveBy = 0


def move_racket_up_anim(racket, moveBy=racketOffset / 5, moveTimes=5):
    """
    Moves a racket up with animation (will last several slides)
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset to move at each tick
    :param moveTimes: The number of ticks the animation is supposed to last
    """
    if len(racket.animQueue) == 0:
        for i in range(moveTimes):
            racket.animQueue.append(moveBy)


def move_racket_down_anim(racket, moveBy=racketOffset / 5, moveTimes=5):
    """
    Moves a racket down with animation (will last several slides)
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset to move at each tick
    :param moveTimes: The number of ticks the animation is supposed to last
    """
    if len(racket.animQueue) == 0:
        for i in range(moveTimes):
            racket.animQueue.append(-moveBy)


def move_racket(racket, moveBy):
    """
    Moves a racket by an arbitrary (relative) offset
    :param racket: The racket (Turtle instance) object to move
    :param moveBy: The offset to move
    """
    y = racket.ycor()
    if (
            (y - (racketSize / 2) > - screenHeight / 2 and moveBy < 0)
            or
            (y + (racketSize / 2) < screenHeight / 2 and moveBy > 0)
    ):
        racket.sety(y + moveBy)


def create_racket(xPos):
    """
    Creates a racket object (Turtle instance)
    :param xPos: The x position of the racket on the screen
    :return: the Turtle instance
    """
    racket = turtle.Turtle()
    racket.speed(0)
    racket.shape('square')
    racket.color('#fce14b')
    racket.turtlesize(racketSize / 20, 1)  # Divide by 20 to convert turtle scale to coords size
    racket.penup()
    racket.goto(xPos, 0)

    racket.moveBy = 0
    racket.animQueue = []
    racket.enableComputerPlay = False
    racket.computerHasPlayed = False

    return racket


def rand_ball_speed():
    """
    Sets the speed settings of the ball to random paramaters, while keeping an overall constant perceived screen
    """
    global ballXSpeed
    global ballYSpeed
    ballXSpeed = random.choice([-1, 1]) * (random.random() + 0.5)
    ballYSpeed = 2 - abs(ballXSpeed)


def move_ball():
    """
    Moves the ball by the defined per-tick offset
    """
    global ball
    x = ball.xcor()
    y = ball.ycor()
    ball.goto(
        x + ballOffset * ballXSpeed,
        y + ballOffset * ballYSpeed
    )


def compute_ball_collisions():
    """
    Checks if the ball collides a racket or a screen border, and inverts the affected axis speed value if applicable
    """
    global ballXSpeed
    global ballYSpeed
    global rightRacket
    global leftRacket
    x = ball.xcor()
    y = ball.ycor()
    if (y + 10 >= screenHeight / 2) or (y - 20 <= -screenHeight / 2):
        ballYSpeed = -ballYSpeed

    right_racket_y = rightRacket.ycor()
    left_racket_y = leftRacket.ycor()

    if (
            (x + 10) >= (rightRacket.xcor() - 5)
            and
            right_racket_y - (racketSize / 2) - 10 < y < right_racket_y + (racketSize / 2) + 10
    ) or (
            (x - 10) <= (leftRacket.xcor() + 5)
            and
            left_racket_y - (racketSize / 2) - 10 < y < left_racket_y + (racketSize / 2) + 10
    ):
        ballXSpeed = -ballXSpeed


def detect_victory():
    """
    Checks if the ball went out of the field, meaning one of the players won
    """
    x = ball.xcor()
    if x <= (-screenWidth / 2) - 10:
        victory(1)
    elif x >= (screenWidth / 2):
        victory(0)


def victory(player):
    """
    Called when a player won. Calculates the scores and resets the positions.
    :param player: The index (0 or 1) of the player who won
    """
    global scores
    global paused
    global leftRacket
    global rightRacket
    reset_ball()
    scores[player] += 1
    update_scores()
    paused = True
    leftRacket.animQueue = []
    rightRacket.animQueue = []


def unpause():
    """
    Unpauses the game
    """
    global paused
    paused = False


def update_scores():
    """
    Updates the displayed scores
    Every 5 points by the leader, increases the speed of the ball
    """
    global scoresPen
    global ballSpeedPen
    global scores
    global ballOffset
    scoresPen.clear()
    scoresPen.goto(-50, (screenHeight / 2) - 50)
    scoresPen.write(scores[0], align="center", font=("Courier", 24, "normal"))
    scoresPen.goto(50, (screenHeight / 2) - 50)
    scoresPen.write(scores[1], align="center", font=("Courier", 24, "normal"))

    # Increase speed each 5 pts
    leaderScore = max(scores)
    if leaderScore > 0 and leaderScore % speedIncreaseStep == 0:
        newBallOffset = ballOffset * speedIncreaseFactor
        ballOffset = min(newBallOffset, speedIncreaseMax)

    ballSpeedPen.clear()
    ballSpeedPen.goto(- screenWidth / 2 + 100, (-screenHeight / 2) + 30)
    ballSpeedPen.write("Ball speed: {}".format(round(ballOffset)), align="center", font=("Courier", 15, "normal"))


def reset_ball():
    ball.goto(0, 0)
    rand_ball_speed()


def next_tick(action):
    global actionsNextTick
    actionsNextTick.append(action)


def tick():
    global actionsNextTick
    global sensorY
    for action in actionsNextTick:
        action()
    actionsNextTick = []


    move_ball()
    anim_rackets()

    # Priorité au capteur
    if sensorY is not None:
        screenVal = (screenHeight / 2) * (sensorY / 800)
        screenVal = min(screenVal, screenHeight/2 - racketSize/2)
        screenVal = max(screenVal, -screenHeight/2 + racketSize/2)
        rightRacket.sety(screenVal)
        sensorY = None

    detect_victory()
    compute_ball_collisions()


def anim_rackets():
    global leftRacket
    global rightRacket

    if leftRacket.enableComputerPlay:
        computer_play(leftRacket)
    if rightRacket.enableComputerPlay:
        computer_play(rightRacket)

    move_racket(leftRacket, leftRacket.moveBy)
    move_racket(rightRacket, rightRacket.moveBy)

    if len(leftRacket.animQueue) > 0:
        move_racket(leftRacket, leftRacket.animQueue.pop(0))
    if len(rightRacket.animQueue) > 0:
        move_racket(rightRacket, rightRacket.animQueue.pop(0))


def computer_play(racket):
    xBall = ball.xcor()
    if (
            (
                racket == leftRacket
                and -(screenWidth / 2) - 50 < xBall
                and xBall < -(screenWidth / 2) + computerSight
            )
            or
            (
                racket == rightRacket
                and (screenWidth / 2) + 50 > xBall
                and xBall > (screenWidth / 2) - computerSight
            )
    ):
        diff = ball.ycor() - racket.ycor()
        move_racket(racket, sign(diff) * (ballOffset*2 - computerSlowness))

def connection():
    port = 8080
    server = SimpleWebSocketServer('', port, FileSharingServer)
    print("Running on: " + " Port: " + str(port))
    server.serveforever()


from threading import *

t = Thread(target=connection)
t.start()


# bind_key

# init
win = turtle.Screen()
win.title("Ponk")
win.bgcolor('black')
win.setup(width=screenWidth, height=screenHeight)
win.tracer(0)

# rackets
leftRacket = create_racket(-(screenWidth / 2))
rightRacket = create_racket((screenWidth / 2) - 10)
leftRacket.enableComputerPlay = True
# rightRacket.enableComputerPlay = True

# field
fieldSeparator = turtle.Turtle()
fieldSeparator.color('#fce14b')
fieldSeparator.turtlesize(screenHeight / 10, 0.1)

# ball
ball = turtle.Turtle()
ball.penup()
ball.shape('circle')
ball.color('#fce14b')
rand_ball_speed()

# Scores
scores = [0, 0]
#
scoresPen = turtle.Turtle()
scoresPen.speed(0)
scoresPen.shape("square")
scoresPen.color("#fce14b")
scoresPen.penup()
scoresPen.hideturtle()

ballSpeedPen = turtle.Turtle()
ballSpeedPen.speed(0)
ballSpeedPen.shape("square")
ballSpeedPen.color("#fce14b")
ballSpeedPen.penup()
ballSpeedPen.hideturtle()
update_scores()

paused = False

win.listen()
if not (leftRacket.enableComputerPlay):
    win.onkeypress(lambda: start_moving_up(leftRacket), "a")
    win.onkeypress(lambda: start_moving_down(leftRacket), "q")
    win.onkeyrelease(lambda: stop_moving(leftRacket), "a")
    win.onkeyrelease(lambda: stop_moving(leftRacket), "q")

if not (rightRacket.enableComputerPlay):
    win.onkeypress(lambda: start_moving_up(rightRacket), "Up")
    win.onkeypress(lambda: start_moving_down(rightRacket), "Down")
    win.onkeyrelease(lambda: stop_moving(rightRacket), "Up")
    win.onkeyrelease(lambda: stop_moving(rightRacket), "Down")

actionsNextTick = []
# mainLoop
while True:
    win.update()
    tick()

    time.sleep(delay)
