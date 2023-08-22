import arcade as arc
import pymunk as pm
from game_objects import *

class App(arc.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, title=SCREEN_TITLE)
        arc.set_background_color(arc.color.BLACK)

        self.space = pm.Space()
        self.space.gravity = (0, -500)

        # Crear el jugador
        self.player = Player(50, 300, self.space)

        # Crear el terreno curvado
        self.terrain = Terrain(self.space)

    def on_key_press(self, symbol: int, modifiers: int):
        self.player.key_press(symbol)
        if symbol == arc.key.SPACE:
            self.player.destroy()
            self.player = Player(50, 300, self.space)
    
    def on_key_release(self, symbol: int, modifiers: int):
        self.player.key_release(symbol)

    def on_draw(self):
        self.clear()

        # Dibujar el auto
        self.player.draw()

        # Dibujar el terreno
        self.terrain.draw()

    def on_update(self, delta_time: float):
        self.space.step(delta_time)
        self.player.update()
        if self.player.car.position[0] > WINDOW_WIDTH:
            self.player.destroy()
            self.player = Player(50, 300, self.space)
            self.terrain.generate_terrain()

if __name__ == "__main__":
    app = App()
    arc.run()