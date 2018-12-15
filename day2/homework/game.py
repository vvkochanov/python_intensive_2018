import math
import os
import random
import turtle
import re


BASE_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

window = turtle.Screen()
window.setup(1200 + 3, 800 + 3)
window.bgpic(os.path.join(BASE_PATH, "images", "background.png"))
window.screensize(1200, 800)
window.tracer(n=2)

ENEMY_COUNT = 5

BASE_X, BASE_Y = 0, -300


class Missile:

    def __init__(self, x, y, color, x2, y2):
        self.color = color

        pen = turtle.Turtle(visible=False)
        pen.speed(0)
        pen.color(color)
        pen.penup()
        pen.setpos(x=x, y=y)
        pen.pendown()
        heading = pen.towards(x2, y2)
        pen.setheading(heading)
        pen.showturtle()
        self.pen = pen

        self.state = 'launched'
        self.target = x2, y2
        self.radius = 0

    def step(self):
        if self.state == 'launched':
            self.pen.forward(4)
            if self.pen.distance(x=self.target[0], y=self.target[1]) < 20:
                self.state = 'explode'
                self.pen.shape('circle')
        elif self.state == 'explode':
            self.radius += 1
            if self.radius > 5:
                self.pen.clear()
                self.pen.hideturtle()
                self.state = 'dead'
            else:
                self.pen.shapesize(self.radius)
        elif self.state == 'dead':
            self.pen.clear()
            self.pen.hideturtle()

    def distance(self, x, y):
        return self.pen.distance(x=x, y=y)

    @property
    def x(self):
        return self.pen.xcor()

    @property
    def y(self):
        return self.pen.ycor()


class Building:
    def __init__(self, name, x, y, image, health):
        self.name = name
        self.x = x
        self.y = y
        self.health = health
        self.full_health = health
        # self.image = image
        self.images = []
        path = os.path.join(BASE_PATH, "images")
        for cur_img in os.scandir(path):
            retxt = re.search(r"(.*_?)\..{3}", cur_img.name)
            if retxt is not None and retxt.group(1)[:4] == image[:4]:
                self.images.append(retxt.group(0))
        print(self.images)
        self.pic_path = os.path.join(BASE_PATH, "images", self.images[0])
        self.building = turtle.Turtle()
        self.draw_building(self.images[0])
        # self.building.hideturtle()
        # self.building.speed(0)
        # self.building.penup()
        # self.building.setpos(x=x, y=y)
        # window.register_shape(self.pic_path)
        # self.building.shape(self.pic_path)
        # self.building.showturtle()

    def draw_building(self, img):
        self.pic_path = os.path.join(BASE_PATH, "images", img)
        # self.building = turtle.Turtle()
        self.building.hideturtle()
        self.building.speed(0)
        self.building.penup()
        self.building.setpos(x=self.x, y=self.y)
        window.register_shape(self.pic_path)
        self.building.shape(self.pic_path)
        self.building.showturtle()

    def missiles_attack(self, attacking_missiles):
        for attacking_missile in attacking_missiles:
            if attacking_missile.state != 'explode':
                continue
            if attacking_missile.distance(self.x, self.y) < attacking_missile.radius * 20:
                self.health -= 100
                destroy_percent = 1. - self.health / self.full_health
                if self.name == 'base':
                    continue
                if 0.25 < destroy_percent <= 0.75:
                    print(self.name, ': ', self.health, ', 0.5 < destroy_percent <= 0.75,', destroy_percent)
                    self.draw_building(self.images[1])
                if 0. < destroy_percent <= 0.25:
                    print(self.name, ': ', self.health, ', 0. < destroy_percent <= 0.25,', destroy_percent)
                    self.draw_building(self.images[2])

    def is_dead(self):
        return self.health <= 0

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_health(self):
        return self.health


def fire_missile(x, y):
    info = Missile(color='white', x=BASE_X, y=BASE_Y, x2=x, y2=y)
    our_missiles.append(info)


def fire_enemy_missile():
    x = random.randint(-600, 600)
    y = 400
    x2 = random.randint(-400, 400)
    info = Missile(color='red', x=x, y=y, x2=x2, y2=BASE_Y)
    enemy_missiles.append(info)


def move_missiles(missiles):
    for missile in missiles:
        missile.step()

    dead_missiles = [missile for missile in missiles if missile.state == 'dead']
    for dead in dead_missiles:
        missiles.remove(dead)


def check_enemy_count():
    if len(enemy_missiles) < ENEMY_COUNT:
        fire_enemy_missile()


def check_interceptions():
    for our_missile in our_missiles:
        if our_missile.state != 'explode':
            continue
        for enemy_missile in enemy_missiles:
            if enemy_missile.distance(our_missile.x, our_missile.y) < our_missile.radius * 10:
                enemy_missile.state = 'dead'


window.onclick(fire_missile)

our_missiles = []
enemy_missiles = []

buildings = [Building(name='base', x=BASE_X, y=BASE_Y, image="base.gif", health=2000),
             Building(name='house', x=BASE_X + 200, y=BASE_Y, image="house_1.gif", health=200),
             Building(name='kremlin', x=BASE_X - 200, y=BASE_Y, image="kremlin_1.gif", health=200),
             Building(name='nuclear', x=BASE_X + 400, y=BASE_Y, image="nuclear_1.gif", health=200),
             Building(name='skyscraper', x=BASE_X - 400, y=BASE_Y, image="skyscraper_1.gif", health=200)]

base_is_dead = False
while True:
    window.update()
    # check_impact()
    for cur_building in buildings:
        # print(cur_building.name, cur_building.health)
        if cur_building.name == "base":
            base_is_dead = cur_building.health <= 0
        cur_building.missiles_attack(attacking_missiles=enemy_missiles)

    # print(base_is_dead)
    if base_is_dead:
        continue

    check_enemy_count()
    check_interceptions()
    move_missiles(missiles=our_missiles)
    move_missiles(missiles=enemy_missiles)
