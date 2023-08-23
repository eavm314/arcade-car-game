import arcade as arc
import pymunk as pm
from game_objects import *

class App(arc.Window):
    def __init__(self):
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, title=SCREEN_TITLE)
        arc.set_background_color(arc.color.BLUE_GREEN)

        self.space = pm.Space()
        self.space.gravity = (0, -500)

        # Crear el terreno curvado
        self.terrain = Terrain(self.space)

        # Crear monedas
        self.coins = self.terrain.generate_coins()

        # Crear el jugador
        self.player = Player(50, 400, self.space)
        self.score = 0
        self.lives = 3
        self.max_score = 0

        self.game_over = False


    def on_key_press(self, symbol: int, modifiers: int):
        self.player.key_press(symbol)

        # Reiniciar nivel
        if symbol == arc.key.SPACE:
            if self.game_over:
                self.game_over = False
                self.lives = 3
                self.score = 0
                self.terrain.generate_terrain()
                self.coins = self.terrain.generate_coins()
                self.player = Player(50, 350, self.space)
                return
            
            self.player.destroy()
            self.lives -= 1
            if self.lives <= 0:
                self.game_over = True
            else:
                self.player = Player(50, 350, self.space)
    
    def on_key_release(self, symbol: int, modifiers: int):
        self.player.key_release(symbol)

    def on_update(self, delta_time: float):
        self.space.step(delta_time)
        self.player.update()
        
        # Recolectar monedas
        coins = arc.check_for_collision_with_list(self.player.car, self.coins)
        self.score += 10*len(coins)
        self.max_score = max(self.max_score, self.score)
        for c in coins:
            self.coins.remove(c)

        # Siguiente nivel
        if self.player.car.position[0] > WINDOW_WIDTH:
            self.player.destroy()
            self.player = Player(50, 300, self.space)
            self.terrain.generate_terrain()
            self.coins = self.terrain.generate_coins()


    def on_draw(self):
        self.clear()

        # Dibujar el auto
        if not self.game_over:
            self.player.draw()

        # Dibujar el terreno
        self.terrain.draw()

        self.coins.draw()

        self.draw_text()

    def draw_text(self):
        arc.draw_text(f"Score: {self.score}", 20, WINDOW_HEIGHT-40, font_size=16)
        arc.draw_text(f"Lives: {self.lives}", 20, WINDOW_HEIGHT-80, font_size=16)
        arc.draw_text(f"Max Score: {self.max_score}", WINDOW_WIDTH-200, WINDOW_HEIGHT-40, font_size=16)

        arc.draw_text(f"Controls:", 20, 160, font_size=24, bold=True)
        arc.draw_text(f"Accelerate: 'D'", 20, 120, font_size=16)
        arc.draw_text(f"Nitro: 'D + SHIFT'", 20, 90, font_size=16)
        arc.draw_text(f"Brake: 'A'", 20, 60, font_size=16)
        arc.draw_text(f"Rotate: 'W', 'S'", 20, 30, font_size=16)
        arc.draw_text(f"Respawn (-1 live): 'SPACE'", 400, 100, font_size=16, anchor_x="center")

        if self.game_over:
            arc.draw_text("Game Over, Press SPACE to restart", 400, 400, font_size=16, anchor_x="center")



if __name__ == "__main__":
    app = App()
    arc.run()