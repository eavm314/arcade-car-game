from constants import *

import math
import pymunk as pm
import pymunk.constraints as pmc
import arcade as arc
import numpy as np
from perlin_noise import PerlinNoise

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
        self.car.key_press(key)
        
    
    def key_release(self, key: int):
        self.b_wheel.key_release(key)
        self.f_wheel.key_release(key)
        self.car.key_release(key)

    def update(self):
        self.sprites.update()

    def draw(self):
        self.sprites.draw()
        # arc.draw_rectangle_outline(self.car.center_x, self.car.center_y, 60, 40, arc.color.GREEN, 2)

    def destroy(self):
        self.car.destroy()
        self.b_wheel.destroy()
        self.f_wheel.destroy()

    def move(self, x: float, y: float):
        self.car.body.position = (x, y)
        self.b_wheel.body.position = (x-self.car.width/2+10, y-self.car.height)
        self.f_wheel.body.position = (x+self.car.width/2-10, y-self.car.height)



class Car(arc.Sprite):
    def __init__(self, x: float, y: float, width: float, height: float, space: pm.Space):
        super().__init__("assets/truck/Body.png", 0.1)
        
        mass = 20

        self.angular_velocity = 0

        moment = pm.moment_for_box(mass, (width, height))
        self.body = pm.Body(mass, moment)
        self.body.position = (x, y)

        self.shape = pm.Poly.create_box(self.body, (width, height)) 

        self.space = space
        self.space.add(self.body, self.shape)

    def key_press(self, key: int):
        if key == arc.key.W:
            self.angular_velocity = 1
        if key == arc.key.S:
            self.angular_velocity = -1

    def key_release(self, key: int):
        if key in (arc.key.W, arc.key.S):
            self.angular_velocity = 0

    def update(self):
        self.center_x = self.body.position.x
        self.center_y = self.body.position.y
        self.body._set_torque(200000*self.angular_velocity)
        self.angle = math.degrees(self.shape.body.angle)

    def destroy(self):
        self.space.remove(self.body, self.shape)



class Wheel(arc.Sprite):
    def __init__(self, x: float, y: float, space: pm.Space) -> None:
        super().__init__("assets/truck/Wheel.png", 0.1)

        self.speed = 0

        mass = 4
        radius = 10
        moment = pm.moment_for_circle(mass, 0, radius)

        self.body = pm.Body(mass, moment)
        self.body.position = (x, y)

        self.shape = pm.Circle(self.body, radius)
        self.shape.elasticity = 20
        self.shape.friction = 200

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

        self.body._set_torque(-20000*self.speed)
    
    def destroy(self):
        self.space.remove(self.body, self.shape)


class Terrain:
    def __init__(self, space: pm.Space) -> None:
        self.space = space
        self.segments = []
        self.generate_terrain()

    def generate_terrain(self):
        noise = PerlinNoise()
        self.sprites = arc.SpriteList()

        for s in self.segments:
            self.space.remove(s)
        self.segments = []

        length = 20
        prev_y = 250
        frequency = 120
        amplitude = 20
        for x in range(length, WINDOW_WIDTH+1, length):
            noise_value = noise([x / frequency])
            noise_value = amplitude * noise_value

            y = int(prev_y + noise_value)

            segment = pm.Segment(self.space.static_body, (x-length, prev_y), (x, y), 8)
            segment.friction = 200
            self.segments.append(segment)

            sprite = arc.Sprite("assets/terrain/terrain-forest-surface-unit.png", 0.35)
            sprite.width += abs(y-prev_y)/2
            sprite.center_x = x-length/2
            sprite.center_y = (y+prev_y)/2
            sprite.angle = math.degrees(np.arctan((y-prev_y)/20))
            self.sprites.append(sprite)

            prev_y = y
            amplitude += 2
            # frequency += 5

        for s in self.segments:
            self.space.add(s)

    def generate_coins(self):
        coins = arc.SpriteList()
        coins_pos = self.segments[7::5]
        for cp in coins_pos:
            coins.append(Coin(cp.center_of_gravity.x, cp.center_of_gravity.y+30))
        return coins

    def draw(self):
        self.sprites.draw()


class Coin(arc.Sprite):
    def __init__(self, x: float, y: float):
        super().__init__("assets/coin.png", 0.05, center_x=x, center_y=y)
