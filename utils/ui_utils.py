from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp

def show_error(message):
    """Display a simple error popup."""
    popup = Popup(
        title='System Message',
        content=Label(text=message, halign='center', text_size=(dp(350), None)),
        size_hint=(None, None), 
        size=(dp(400), dp(250))
    )
    popup.open()
