import math
from arcade import TextureAtlas
from constants import *
import pymunk as pm
import pymunk.constraints as pmc
import arcade as arc
import numpy as np

class Player():
    def __init__(self, x: float, y: float, space: pm.Space):
        self.sprites = arc.SpriteList()
        self.space = space

        width = 60
        height = 20
        self.car = Car(x, y, width, height, space)
        self.sprites.append(self.car)

        self.b_wheel = Wheel(x-width/2+10, y-height, self.space)
        self.f_wheel = Wheel(x+width/2-10, y-height, self.space)

        self.sprites.append(self.b_wheel)
        self.sprites.append(self.f_wheel)

        back_spring = pmc.PinJoint(self.car.body, self.b_wheel.body, (-width / 2+10, -height), (0, 0))
        front_spring = pmc.PinJoint(self.car.body, self.f_wheel.body, (width / 2-10, -height), (0, 0))
        self.space.add(front_spring, back_spring)

    def key_press(self, key: int):
        self.b_wheel.key_press(key)
        self.f_wheel.key_press(key)
    
    def key_release(self, key: int):
        self.b_wheel.key_release(key)
        self.f_wheel.key_release(key)

    def update(self):
        self.sprites.update()

    def draw(self):
        self.sprites.draw()
        # arc.draw_rectangle_outline(self.car.center_x, self.car.center_y, 60, 40, arc.color.GREEN, 2)

class Car(arc.Sprite):
    def __init__(self, x: float, y: float, width: float, height: float, space: pm.Space):
        super().__init__("assets/truck/Body.png", 0.1)
        
        mass = 10

        moment = pm.moment_for_box(mass, (width, height))
        self.body = pm.Body(mass, moment)
        self.body.position = (x, y)

        self.shape = pm.Poly.create_box(self.body, (width, height))   

        self.space = space
        self.space.add(self.body, self.shape)

    def update(self):
        self.center_x = self.body.position.x
        self.center_y = self.body.position.y
        self.angle = math.degrees(self.shape.body.angle)

class Wheel(arc.Sprite):
    def __init__(self, x: float, y: float, space: pm.Space) -> None:
        super().__init__("assets/truck/Wheel.png", 0.1)

        self.speed = 0

        mass = 2
        radius = 10
        moment = pm.moment_for_circle(mass, 0, radius)

        self.body = pm.Body(mass, moment)
        self.body.position = (x, y)

        self.shape = pm.Circle(self.body, radius)
        # self.shape.elasticity = 10
        self.shape.friction = 100

        self.space = space
        self.space.add(self.body, self.shape)

    def key_press(self, key: int):
        match key:
            case arc.key.D:
                self.speed = 1
            case arc.key.A:
                self.speed = -1
            case arc.key.LSHIFT:
                if self.speed > 0:
                    self.speed *= 2

    def key_release(self, key: int):
        if key in (arc.key.D, arc.key.A):
            self.speed = 0

    def update(self):
        self.center_x = self.body.position.x
        self.center_y = self.body.position.y
        self.angle = math.degrees(self.shape.body.angle)

        self.body.torque = -10000*self.speed
    



class Terrain:
    def __init__(self, space: pm.Space) -> None:
        self.space = space

        length = 20
        prev_y = 300
        for x in range(length, WINDOW_WIDTH+1, length):
            # y = 100 * (1 + 0.2 * (x / 50) ** 2)  # Ejemplo de ecuación de curva
            y = 300 + 50*np.sin(x/50)
            segment = pm.Segment(self.space.static_body, (x-length, prev_y), (x, y), 10)
            prev_y = y
            segment.friction = 100
            self.space.add(segment)

    def draw(self):
        for shape in self.space.shapes:
            if isinstance(shape, pm.Segment):
                p1 = shape.a
                p2 = shape.b
                arc.draw_line(p1[0], p1[1], p2[0], p2[1], arc.color.DARK_GREEN, 10)
