import random
import csv
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

# Set a mobile-like window size for testing on desktop
Window.size = (400, 700)
Window.clearcolor = get_color_from_hex('#121212') 

# Base Puzzle Database
PUZZLES = {
    "TV Shows": [],
    "Food & Drink": [],
    "Leisure": [],
    "Famous People": [],
    "Movies": [],
    "Music & Bands": [],
    "Geography & Places": [],
    "Animals": []
}

def load_csv_puzzles():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    csv_mapping = {
        "TV Shows": "UK_TV_Shows_Puzzles.csv",
        "Food & Drink": "UK_Food_Drink_Puzzles.csv",
        "Leisure": "UK_Leisure_Puzzles.csv",
        "Famous People": "UK_Famous_People_Puzzles.csv",
        "Movies": "UK_Movies_Puzzles.csv",
        "Music & Bands": "UK_Music_Bands_Puzzles.csv",
        "Geography & Places": "UK_Geography_Places_Puzzles.csv",
        "Animals": "UK_Animals_Puzzles.csv"
    }
    
    for category, filename in csv_mapping.items():
        file_path = os.path.join(base_dir, "PUZZLES", filename)
        
        if os.path.exists(file_path):
            with open(file_path, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    PUZZLES[category].append({
                        "phonetic": row["Phonetic"],
                        "answer": row["Answer"]
                    })
        else:
            print(f"Warning: Could not find {filename}")

load_csv_puzzles()

def get_all_puzzles():
    all_puzzles = []
    for puzzles in PUZZLES.values():
        all_puzzles.extend(puzzles)
    return all_puzzles

class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        branding = Label(
            text="Brought to you by\n\nAJ Entertainments", 
            font_size='26sp', 
            bold=True, 
            color=get_color_from_hex('#34C759'),
            halign='center'
        )
        layout.add_widget(branding)
        self.add_widget(layout)
        
    def on_enter(self, *args):
        Clock.schedule_once(self.switch_to_menu, 2.5)
        
    def switch_to_menu(self, dt):
        self.manager.current = 'menu'

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        title = Label(
            text="CRACK THE CODE", 
            font_size='32sp', 
            bold=True, 
            color=get_color_from_hex('#FF3B30'),
            size_hint=(1, 0.2)
        )
        layout.add_widget(title)

        subtitle = Label(
            text="Select a Category", 
            font_size='18sp', 
            color=get_color_from_hex('#FFFFFF'),
            size_hint=(1, 0.1)
        )
        layout.add_widget(subtitle)

        grid = GridLayout(cols=1, spacing=15, size_hint=(1, 0.7))
        
        categories = list(PUZZLES.keys()) + ["Random"]
        for cat in categories:
            btn = Button(
                text=cat,
                font_size='20sp',
                background_normal='',
                background_color=get_color_from_hex('#333333'),
                color=get_color_from_hex('#FFFFFF')
            )
            btn.bind(on_release=lambda instance, c=cat: self.start_game(c))
            grid.add_widget(btn)

        layout.add_widget(grid)
        self.add_widget(layout)

    def start_game(self, category):
        app = App.get_running_app()
        app.play_click_sound()
        app.game_screen.set_category(category)
        app.screen_manager.current = 'game'

class GameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_category = ""
        self.current_puzzle = None
        self.unplayed_pools = {} 
        
        self.layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        header = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        back_btn = Button(
            text="< Back", 
            size_hint=(0.3, 1),
            background_normal='',
            background_color=get_color_from_hex('#555555')
        )
        back_btn.bind(on_release=self.go_back)
        
        self.category_label = Label(text="", font_size='18sp', bold=True)
        
        header.add_widget(back_btn)
        header.add_widget(self.category_label)
        self.layout.add_widget(header)

        self.layout.add_widget(Label(
            text="Read aloud three times:", 
            font_size='16sp', 
            size_hint=(1, 0.1)
        ))

        self.phonetic_label = Label(
            text="", 
            font_size='28sp', 
            bold=True, 
            color=get_color_from_hex('#FF3B30'),
            size_hint=(1, 0.3),
            text_size=(300, None),
            halign='center'
        )
        self.layout.add_widget(self.phonetic_label)

        self.reveal_btn = Button(
            text="Reveal Answer", 
            font_size='20sp', 
            size_hint=(1, 0.15),
            background_normal='',
            background_color=get_color_from_hex('#007AFF')
        )
        self.reveal_btn.bind(on_release=self.reveal_answer)
        self.layout.add_widget(self.reveal_btn)

        self.answer_label = Label(
            text="", 
            font_size='24sp', 
            bold=True, 
            color=get_color_from_hex('#34C759'),
            size_hint=(1, 0.2)
        )
        self.layout.add_widget(self.answer_label)

        self.next_btn = Button(
            text="Next Puzzle", 
            font_size='20sp', 
            size_hint=(1, 0.15),
            background_normal='',
            background_color=get_color_from_hex('#FF9500'),
            disabled=True,
            opacity=0
        )
        self.next_btn.bind(on_release=self.load_puzzle)
        self.layout.add_widget(self.next_btn)

        self.add_widget(self.layout)

    def set_category(self, category):
        self.current_category = category
        self.category_label.text = category
        self.load_puzzle()

    def load_puzzle(self, *args):
        if args:
            App.get_running_app().play_click_sound()

        cat = self.current_category
        
        if cat not in self.unplayed_pools or not self.unplayed_pools[cat]:
            if cat == "Random":
                pool = get_all_puzzles()
            else:
                pool = list(PUZZLES[cat]) 
            
            random.shuffle(pool) 
            self.unplayed_pools[cat] = pool
            
        if not self.unplayed_pools[cat]: 
             self.phonetic_label.text = "No puzzles found!"
             self.reveal_btn.disabled = True
             return

        self.current_puzzle = self.unplayed_pools[cat].pop()
        self.phonetic_label.text = f'"{self.current_puzzle["phonetic"]}"'
        
        self.answer_label.text = ""
        self.reveal_btn.disabled = False
        self.reveal_btn.opacity = 1
        self.next_btn.disabled = True
        self.next_btn.opacity = 0

    def reveal_answer(self, *args):
        if self.current_puzzle:
            App.get_running_app().play_reveal_sound()
            self.answer_label.text = self.current_puzzle["answer"]
            self.reveal_btn.disabled = True
            self.reveal_btn.opacity = 0
            self.next_btn.disabled = False
            self.next_btn.opacity = 1

    def go_back(self, *args):
        App.get_running_app().play_click_sound()
        App.get_running_app().screen_manager.current = 'menu'

class PhoneticGameApp(App):
    def build(self):
        # Changed from .wav to .mp3 here!
        base_dir = os.path.dirname(os.path.abspath(__file__))
        audio_dir = os.path.join(base_dir, "AUDIO")
        
        self.sound_click = SoundLoader.load(os.path.join(audio_dir, 'click.mp3'))
        self.sound_reveal = SoundLoader.load(os.path.join(audio_dir, 'reveal.mp3'))

        self.screen_manager = ScreenManager(transition=FadeTransition())
        
        self.splash_screen = SplashScreen(name='splash')
        self.menu_screen = MenuScreen(name='menu')
        self.game_screen = GameScreen(name='game')
        
        self.screen_manager.add_widget(self.splash_screen)
        self.screen_manager.add_widget(self.menu_screen)
        self.screen_manager.add_widget(self.game_screen)
        
        return self.screen_manager

    def play_click_sound(self):
        if self.sound_click:
            if self.sound_click.state == 'play':
                self.sound_click.stop()
            self.sound_click.play()

    def play_reveal_sound(self):
        if self.sound_reveal:
            if self.sound_reveal.state == 'play':
                self.sound_reveal.stop()
            self.sound_reveal.play()

if __name__ == '__main__':
    PhoneticGameApp().run()