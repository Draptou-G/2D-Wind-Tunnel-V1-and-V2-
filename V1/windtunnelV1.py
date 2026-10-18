# Torricelli's law simulation of air flow over a wing causing lift
# Dimitri Raptou
 

import turtle
import random
import math

 

screen = turtle.Screen()
screen.title("Simulation of air flow over a wing causing lift - Torricelli's law")
screen.bgcolor("Blue")
screen.tracer(0)

 

pressure_total = 24    # pressure where air is not moving (24,48,72,96)
static_pressure = 2   # free stream of moving air (range 5,10,15,20)
air_density = 1       # density of the air (1, 2, 3)

 

air_speed = int(math.sqrt(2 * (pressure_total - static_pressure))/air_density)


 

def drawWing():
    # Draw the wing
    wing = turtle.Turtle()
    wing.hideturtle()
    wing.fillcolor("gray")
    wing.penup()
    
    wing.goto(-100, 0)
    wing.pendown()
    wing.begin_fill()
    wing.goto(-130,10)
    wing.goto(-50, 20)
    
    wing.goto(100, 0)
    wing.goto(-100, 0)
    wing.end_fill()

 

# list of air particles which will be circles
particles = []

 

for i in range(40):
    p = turtle.Turtle()
    p.shape("circle")
    p.shapesize(0.2)
    
    p.penup()

 
# choose a random y position for the particle, either above or below the wing
    y = random.choice([30,50, 60, 70, 80, 90, -30,-50,-60, -70,-80, -90])
    p.goto(random.randint(-300, 300), y)
    if y > 0 :
        p.color("red")
    else:
        p.color("yellow")
    
    particles.append(p)

 

# Torricelli's law
text = turtle.Turtle()
text.hideturtle()
text.penup()
text.goto(0, 300)
text.color("white")
text.write("Torricelli's Law Simulation: v = sqrt(2(Po - P)/rho)    ",
           align="center", font=("Arial", 15, "bold"))
text.goto(-600, 220)
text.write("Po = total pressure (pressure where air is not moving)   [24]  [48]  [72]  [96]",
           align="left", font=("Arial", 13, "normal"))
text.goto(-600, 180)
text.write("P = free stream of moving air                                       [05]  [10]  [15]  [20]",
           align="left", font=("Arial", 13, "normal"))
text.goto(-600, 140)
text.write("rho = density of air (colder air is better for lift)                [01]  [02]  [03]",
           align="left", font=("Arial", 13, "normal"))


 

def check_air_density():
    global air_density
    for p in particles:
        if air_density == 1:
            p.shapesize(0.2)    
        elif air_density == 2:
            
            p.shapesize(0.4)
        elif air_density == 3:
            p.shapesize(0.6)
    

 

# checks to see where you click on the screen for changing the variables
def screen_click(x,y):
    print(f"{x}")
    global pressure_total, static_pressure, air_density

 

    # change the total air pressure based on clicking the right box
    if y >200 and y<220:
        if x >180 and x<220:
            pressure_total = 24
        if x > 220 and x<250:
            pressure_total = 48
        if x > 250 and x<280:
            pressure_total = 72
        if x > 285 and x<315:
            pressure_total = 96
    #change the static pressure
    if y > 180 and y<200:
        if x >180 and x<220:
            static_pressure = 4
        if x > 220 and x<250:
            static_pressure = 8
        if x > 250 and x<280:
            static_pressure = 10
        if x > 285 and x<315:
            static_pressure = 12
    # change the air_density
    if y > 160 and y<180:
        if x >180 and x<220:
            air_density = 1
        if x > 220 and x<250:
            air_density = 2
        if x > 250 and x<280:
            air_density = 3
        

 

# Animate the particles
def move():
    drawWing()
    global air_speed
    # you can change these values
    screen.onscreenclick(screen_click)    

 

    # calculation of the air speed  
    air_speed = int(math.sqrt(2 * (pressure_total - static_pressure))/air_density)

 

    check_air_density()
   #for testing
   # print(air_speed)
    for p in particles:

 

        # set the air speed based on the relativ position on the screen
        if p.ycor() > 0 and p.xcor()>-100:
            speed = air_speed
        else:
            speed = 4    # default the air speed

 

        # have the particles above the wing move down to show lift
        if p.ycor() > 0 and p.xcor()>20:
            p.sety(p.ycor()-1)

 

        # move the particles based on the air speed calculation
        p.setx(p.xcor() + speed)

 

        # have particles that are about to hit the wing (at position 30) move up a bit to position 50
        if p.xcor() > -100 and p.xcor()<-50:
            if p.ycor()<=50 and p.ycor()>0:
                p.sety(p.ycor()+1)

 

        #reset the air to the left once it's gone off the screen back to the start
        if p.xcor() > 300 :
            reset_red_y = random.choice([-30,-50,-60, -70,-80, -90])
            reset_yellow_y = random.choice([30,50, 60, 70, 80, 90])
            if p.ycor() < 0:
                p.sety(reset_red_y)
            if  p.ycor() >= 0:
                p.sety(reset_yellow_y)

 

            p.setx(-300)

 

    screen.update()
    screen.ontimer(move, 30)

 

move()
turtle.done()
