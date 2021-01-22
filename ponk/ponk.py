import random
import time
import turtle
from numpy import sign

# Settings
screenWidth = 1280
screenHeight = 720

racketSize = 30
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


def move_racket_up(racket, moveBy=racketOffset):
    move_racket(racket, moveBy)


def move_racket_down(racket, moveBy=racketOffset):
    move_racket(racket, -moveBy)


def start_moving_up(racket, moveBy=racketOffset / 5):
    racket.moveBy = moveBy


def start_moving_down(racket, moveBy=racketOffset / 5):
    racket.moveBy = -moveBy


def stop_moving(racket):
    racket.moveBy = 0


def move_racket_up_anim(racket, moveBy=racketOffset / 5, moveTimes=5):
    if len(racket.animQueue) == 0:
        for i in range(moveTimes):
            racket.animQueue.append(moveBy)


def move_racket_down_anim(racket, moveBy=racketOffset / 5, moveTimes=5):
        if len(racket.animQueue) == 0:
            for i in range(moveTimes):
                racket.animQueue.append(-moveBy)


def move_racket(racket, moveBy):
    y = racket.ycor()
    if (
            (y - (racketSize / 2) > - screenHeight / 2 and moveBy < 0)
            or
            (y + (racketSize / 2) < screenHeight / 2 and moveBy > 0)
    ):
        racket.sety(y + moveBy)


def create_racket(xPos):
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
    global ballXSpeed
    global ballYSpeed
    ballXSpeed = random.choice([-1, 1]) * (random.random() + 0.5)
    ballYSpeed = 2 - abs(ballXSpeed)


def move_ball():
    global ball
    x = ball.xcor()
    y = ball.ycor()
    ball.goto(
        x + ballOffset * ballXSpeed,
        y + ballOffset * ballYSpeed
    )


def compute_ball_collisions():
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
    x = ball.xcor()
    if x <= (-screenWidth / 2) - 10:
        victory(1)
    elif x >= (screenWidth / 2):
        victory(0)


def victory(player):
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
    next_tick(lambda: time.sleep(2))
    next_tick(unpause)


def unpause():
    global paused
    paused = False


def update_scores():
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
    for action in actionsNextTick:
        action()
    actionsNextTick = []


    move_ball()
    anim_rackets()

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
