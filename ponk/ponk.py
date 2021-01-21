import random
import time
import turtle

# Settings
screenWidth = 1000
screenHeight = 600

racketSize = 150
racketOffset = 40

delay = 0.005
ballOffset = 10


def move_racket_up(racket, moveBy = racketOffset):
    y = racket.ycor()
    if y + (racketSize / 2) < screenHeight / 2:
        racket.sety(y + moveBy)


def move_racket_down(racket, moveBy = racketOffset):
    y = racket.ycor()
    if y - (racketSize / 2) > - screenHeight / 2:
        racket.sety(y - moveBy)


def create_racket(xPos):
    racket = turtle.Turtle()
    racket.speed(0)
    racket.shape('square')
    racket.color('#fce14b')
    racket.turtlesize(racketSize / 20, 1)  # Divide by 20 to convert turtle scale to coords size
    racket.penup()
    racket.goto(xPos, 0)
    return racket


def rand_ball_speed():
    global ballXSpeed
    global ballYSpeed
    ballXSpeed = random.choice([-1, 1]) * (random.random() * 1.5 + 0.5)
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
    if x <= (-screenWidth / 2):
        victory(1)
    elif x >= (screenWidth / 2):
        victory(0)


def victory (player):
    global scores
    reset_ball()
    scores[player] += 1
    update_scores()
    next_tick(lambda : time.sleep(2))


def update_scores():
    global scoresPen
    scoresPen.clear()
    scoresPen.goto(-50, (screenHeight / 2) - 50)
    scoresPen.write(scores[0], align="center", font=("Courier", 24, "normal"))
    scoresPen.goto(50, (screenHeight / 2) - 50)
    scoresPen.write(scores[1], align="center", font=("Courier", 24, "normal"))


def reset_ball():
    ball.goto(0, 0)
    rand_ball_speed()


def next_tick(action):
    global actionsNextTick
    actionsNextTick.append(action)


def tick ():
    global actionsNextTick
    for action in actionsNextTick:
        action()
    actionsNextTick = []


# init
win = turtle.Screen()
win.title("Ponk")
win.bgcolor('black')
win.setup(width=screenWidth, height=screenHeight)
win.tracer(0)

# rackets
leftRacket = create_racket(-(screenWidth / 2))
rightRacket = create_racket((screenWidth / 2) - 10)

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
update_scores()


win.listen()
win.onkeypress(lambda: move_racket_up(leftRacket), "a")
win.onkeypress(lambda: move_racket_down(leftRacket), "q")

win.onkeypress(lambda: move_racket_up(rightRacket), "Up")
win.onkeypress(lambda: move_racket_down(rightRacket), "Down")

actionsNextTick = []
# mainLoop
while True:
    win.update()
    tick()

    move_ball()
    detect_victory()
    compute_ball_collisions()

    time.sleep(delay)
