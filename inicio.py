import tkinter as tk

class Inicio(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.widgets()

    def widgets(self):
        label = tk.Label(self, text="Bienvenido a la aplicación de Spotify", font=("Segoe UI", 16, "bold"), bg="#30c450", fg="#FFFFFF")
        label.pack(pady=20)
        label2 = tk.Label(self, text="Esta es una API de Spotify, la cual funciona como un control\n"
                                    "  remoto para administrar tu cuenta, aquí podras utilizar\t\n"
                                     "            las funciones pricipales que tiene Spotify como reproducir playlist,\n"
                                     "           crear playlis, cargar las playlist, agregar canciones, ver un historial\n"
                                     "             de las canciones que han ido sonando y ademas contiene la opción\n"
                                     "             de exportar todas las canciones a un excel tanto de las playlist como\n"
                                     "           de las canciones que han sonado para que puedas tener un mejor\n"
                                     "            control de las canciones que escuchas frecuentemente.\t\t\n\n"
                                     "        Te invito a explorar la API para utilizar Spotify de una forma diferente.", font=("Segoe UI", 12), bg="#30c450", fg="#000000")
        label2.pack(pady=10)
        