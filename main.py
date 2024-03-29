from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.uix.label import Label
from kivy.uix.popup import Popup

# Trida mice.
class Ball(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

# Trida palky.
class Paddle(Widget):
    velocity = NumericProperty(0)
    score = NumericProperty(0)
    is_shooting = False
    last_shot_time = 0
    min_shot_interval = 0.75

    def move_up(self):
        self.velocity = 10

    def move_down(self):
        self.velocity = -10

    def stop(self):
        self.velocity = 0

    def update(self, dt):
        """Aktualizace polohy pálky na základě aktuální rychlosti."""
        self.y += self.velocity
        self.y = max(0, min(self.parent.height - self.height, self.y))

    def shoot(self, velocity):
        """Vystreleni mice s danou rychlostí."""
        current_time = Clock.get_time()
        if current_time - self.last_shot_time >= self.min_shot_interval:
            self.last_shot_time = current_time
            ball_center = (self.center_x + 55, self.center_y + 40) if velocity > 0 else (
            self.center_x, self.center_y + 40)
            if self == self.parent.player1:
                ball_velocity = (abs(velocity), 0)
            elif self == self.parent.player2:
                ball_velocity = (-abs(velocity), 0)
            ball = Ball(center=ball_center, velocity=ball_velocity)
            self.parent.add_widget(ball)

    def bounce_ball(self, ball):
        """odstraneni mice pri kolizi s protejsi palkou a aktualizace skore."""
        if self.collide_widget(ball):
            self.score += 1
            self.parent.update_score()
            self.parent.remove_widget(ball)

# Hlavní třída hry.
class PongGame(Widget):
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    score_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PongGame, self).__init__(**kwargs)
        self.keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self.keyboard.bind(on_key_down=self._on_keyboard_down)
        self.keyboard.bind(on_key_up=self._on_keyboard_up)
        self.score_label = Label(text="0 : 0", pos=(self.center_x, self.height - 30), font_size=30)
        Clock.schedule_interval(self.update_players, 1.0 / 60.0)

    def _keyboard_closed(self):
        """Uzavření klávesnice."""
        self._keyboard_unbind(on_key_down=self._on_keyboard_down)
        self._keyboard_unbind(on_key_up=self._on_keyboard_up)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        """Obsluha stisknutí klávesy."""
        if keycode[1] == 'w':
            self.player1.move_up()
        elif keycode[1] == 's':
            self.player1.move_down()
        elif keycode[1] == 'up':
            self.player2.move_up()
        elif keycode[1] == 'down':
            self.player2.move_down()
        elif keycode[1] == 'spacebar':
            self.player1.shoot(10)
        elif keycode[1] == 'enter':
            self.player2.shoot(-10)

    def _on_keyboard_up(self, keyboard, keycode):
        """Obsluha puštění klávesy."""
        if keycode[1] in ('w', 's'):
            self.player1.stop()
        if keycode[1] in ('up', 'down'):
            self.player2.stop()
        elif keycode[1] == 'spacebar':
            self.player1.shoot(10)
        elif keycode[1] == 'enter':
            self.player2.shoot(-10)

    def update_players(self, dt):
        """Aktualizace stavu hráčů."""
        self.player1.update(dt)
        self.player2.update(dt)

    def update(self, dt):
        """Aktualizace stavu hry."""
        for ball in self.children[:]:
            if isinstance(ball, Ball):
                ball.move()
                self.player1.bounce_ball(ball)
                self.player2.bounce_ball(ball)

        if self.player1.score >= 10 or self.player2.score >= 10:
            self.show_game_over_popup()

    def show_game_over_popup(self):
        """popup okno ktere vyskoci, kdyz jeden z hracu vyhraje"""
        winner = "Pravý" if self.player1.score >= 10 else "Levý"
        content = f"{winner} vyhrává!\n"
        popup = Popup(title="Game Over", content=Label(text=content), size_hint=(None, None), size=(400, 200))
        popup.open()

    def update_score(self):
        """Aktualizace skore"""
        self.score_label.text = f"{self.player2.score} : {self.player1.score}"

class PongApp(App):
    def build(self):
        game = PongGame()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

# Spuštění aplikace.
if __name__ == '__main__':
    PongApp().run()