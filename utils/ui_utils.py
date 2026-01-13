from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock

def show_error(message):
    """Display a simple error popup safely from any thread."""
    def _open_popup(dt):
        popup = Popup(
            title='System Message',
            content=Label(text=message, halign='center', text_size=(dp(350), None)),
            size_hint=(None, None), 
            size=(dp(400), dp(250))
        )
        popup.open()
    
    Clock.schedule_once(_open_popup, 0)
