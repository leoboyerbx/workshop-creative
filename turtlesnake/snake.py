import random
import time
import turtle

# Settings
delay = 0.1
moveOffset = 20


def move():
    global segments
    for index in range(len(segments) - 1, 0, -1):
        x = segments[index - 1].xcor()
        y = segments[index - 1].ycor()
        segments[index].goto(x, y)
    if len(segments) > 0:
        x = head.xcor()
        y = head.ycor()
        segments[0].goto(x, y)

    if head.direction == "up":
        y = head.ycor()
        head.sety(y + moveOffset)

    if head.direction == "down":
        y = head.ycor()
        head.sety(y - moveOffset)

    if head.direction == "right":
        x = head.xcor()
        head.setx(x + moveOffset)

    if head.direction == "left":
        x = head.xcor()
        head.setx(x - moveOffset)


def compute_collisions ():
    global head
    global segments

    if head.xcor() > 290 or head.xcor() < -290 or head.ycor() > 290 or head.ycor() < -290:
        time.sleep(1)
        head.goto(0, 0)
        head.direction = "stop"
        for segment in segments:
            segment.goto(1000, 1000)

            # clear segment list
        segments = []
        defeat()

    for segment in segments:
        if segment.distance(head) < 20:
            time.sleep(1)
            head.goto(0, 0)
            head.direction = "stop"
            for segment in segments:
                segment.goto(1000, 1000)
                segment.clear()
            segments = []
            defeat()

    if head.distance(food) < 15:
        x = random.randint(-290, 290)
        y = random.randint(-290, 290)
        food.goto(x, y)
        add_segment()


def defeat ():
    global high_score
    global score
    high_score = score
    score = 0
    update_score()


def add_segment ():
    global segments
    new_segment = turtle.Turtle()
    new_segment.speed(0)
    new_segment.shape("square")
    new_segment.color("white")
    new_segment.penup()
    if len(segments) > 0:
        last_segment = segments[len(segments) - 1]
        new_segment.goto(last_segment.xcor(), last_segment.ycor())
    else:
        new_segment.goto(head.xcor(), head.ycor())
    segments.append(new_segment)

    global score
    score += 10
    update_score()


def go_up():
    if head.direction != "down":
        head.direction = "up"


def go_down():
    if head.direction != "up":
        head.direction = "down"


def go_right():
    if head.direction != "left":
        head.direction = "right"


def go_left():
    if head.direction != "right":
        head.direction = "left"


def update_score():
    global pen
    pen.clear()
    pen.write("score: {} High Score: {}".format(score, high_score), align="center", font=("Courier", 24, "normal"))


# init
win = turtle.Screen()
win.title("WebSoSnake")
win.bgcolor('#6699ff')
win.setup(width=600, height=600)
win.tracer(0)

# Snake head
head = turtle.Turtle()
head.speed(0)
head.shape('square')
head.color('black')
head.penup()
head.goto(0, 100)
head.direction = 'stop'

# Snake body
segments = []

# Snake food
food = turtle.Turtle()
food.speed(0)
food.shape("circle")
food.color("red")
food.penup()
food.shapesize(0.50, 0.50)
food.goto(0, 0)

# Scores
score = 0
high_score = 0

pen = turtle.Turtle()
pen.speed(0)
pen.shape("square")
pen.color("white")
pen.penup()
pen.hideturtle()
pen.goto(0, 260)
pen.write("Score: 0 High Score: {}".format(high_score), align="center", font=("Courier", 24, "normal"))


win.listen()
win.onkey(go_up, "z")
win.onkey(go_down, "s")
win.onkey(go_right, "d")
win.onkey(go_left, "q")

# mainLoop
while True:
    win.update()
    move()
    compute_collisions()
    time.sleep(delay)