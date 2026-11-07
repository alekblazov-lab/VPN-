import threading
from kivy.app import App
from kivy.uix.label import Label

def run_flask():
    import vpn_app
    vpn_app.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False, threaded=True)

class VPNBuilderApp(App):
    def build(self):
        threading.Thread(target=run_flask, daemon=True).start()
        return Label(text="VPN Builder запущен\nhttp://127.0.0.1:5000", font_size='18sp')

if __name__ == '__main__':
    VPNBuilderApp().run()
