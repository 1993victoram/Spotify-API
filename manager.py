from tkinter import *
import tkinter as tk
from tkinter import messagebox, filedialog
from ventana_spotify import VentanaSpotify
from container import Container
from inicio import Inicio
from buscar import Buscar
from playlist import Playlist
from agregar import Agregar
from canciones import Canciones
from escuchadas import Escuchadas
from perfil import Perfil
import os, sys
from PIL import Image, ImageTk 


def resource_path(relative_path):
    """Obtiene la ruta correcta cuando se ejecuta en .exe o en .py normal"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class Manager(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎧 Control de Spotify")
        self.geometry("650x550")
        self.resizable(False, False)

        # Usamos resource_path para el icono
        icono_path = resource_path("imagenes/icono.ico")

        # Fix para icono en barra de tareas en el ejecutable.exe
        if sys.platform.startswith("win"):
            try:
                import ctypes
                myappid = 'spotify.api.app'  # ID único para la app
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception as e:
                print("No se pudo aplicar AppUserModelID:", e)

        # Asignar icono (funciona tanto en ventana como en barra de tareas)
        self.iconbitmap(icono_path)

        # contenedor principal (fondo verde)
        container = tk.Frame(self, bg="#30c450")
        container.pack(fill="both", expand=True)

        # permitir que el grid del container escale
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # crear frames y apilarlos con grid
        self.frames = {}
        for F in (VentanaSpotify, Container, Inicio, Buscar, Playlist, Agregar, Canciones, Escuchadas, Perfil):
            frame = F(container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[F] = frame

        # mostrar el frame de autenticación al inicio
        self.show_frame(VentanaSpotify)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()
        self.update_idletasks()

        # Cambiar tamaño de la ventana según el frame activo
        if page.__name__ == "Container":
            w, h = 800, 600   # más grande en Container
        else:
            w, h = 650, 550   # tamaño por defecto

        # Obtener dimensiones de la pantalla
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()

        # Calcular coordenadas para centrar
        x = (sw - w) // 2
        y = (sh - h) // 2

        # Aplicar geometría
        self.geometry(f"{w}x{h}+{x}+{y}")
