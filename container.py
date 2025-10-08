import tkinter as tk
from inicio import Inicio
from reproduccion import Reproduccion
from buscar import Buscar
from playlist import Playlist
from agregar import Agregar
from canciones import Canciones
from escuchadas import Escuchadas
from perfil import Perfil  
from PIL import Image, ImageTk 
import os

BASE_DIR = os.path.dirname(__file__)  
imagen_path = os.path.join(BASE_DIR, "imagenes", "logo.png")

imagen = Image.open(imagen_path)


class Container(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.frames = {}
        self.buttons = []
        self.widgets()

    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

    def inicio(self):
        if Inicio not in self.frames:
            frame_inicio = Inicio(self, self.controller)
            frame_inicio.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Inicio] = frame_inicio
        # Ahora sí mostramos el frame
        self.show_frame(Inicio)

    def reproduccion(self):
        
    
        if Reproduccion not in self.frames:
            frame_reproduccion = Reproduccion(self, self.controller)
            frame_reproduccion.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Reproduccion] = frame_reproduccion
    
        self.show_frame(Reproduccion)

    def buscar(self):
        
        if Buscar not in self.frames:
            frame_buscar = Buscar(self, self.controller)
            frame_buscar.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Buscar] = frame_buscar
        
        self.show_frame(Buscar)

    def playlist(self):
        if Playlist not in self.frames:
            frame_nueva_playlist = Playlist(self, self.controller)
            frame_nueva_playlist.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Playlist] = frame_nueva_playlist
        
        self.show_frame(Playlist)

    def agregar(self):
        if Agregar not in self.frames:
            frame_agregar = Agregar(self, self.controller)
            frame_agregar.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Agregar] = frame_agregar
        
        self.show_frame(Agregar)   
    
    def canciones(self):
        if Canciones not in self.frames:
            frame_canciones = Canciones(self, self.controller)
            frame_canciones.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Canciones] = frame_canciones
        
        self.show_frame(Canciones)

    def escuchadas(self):
        if Escuchadas not in self.frames:
            frame_escuchadas = Escuchadas(self, self.controller)
            frame_escuchadas.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Escuchadas] = frame_escuchadas
        
        self.show_frame(Escuchadas)

    def perfil(self):
        if Perfil not in self.frames:
            frame_perfil = Perfil(self, self.controller)
            frame_perfil.place(x=200, y=80, relwidth=0.7, relheight=0.8)
            self.frames[Perfil] = frame_perfil
        
        self.show_frame(Perfil)

    def widgets(self):
        

        frame2 = tk.Frame(self, bg="#000000", width=150, height=450)
        frame2.place(x=0, y=0, width=195, height=600)

        label = tk.Label(self, text="🎧 Control de Spotify", bg="#30c450", fg="#000000", font=("Segoe UI", 16, "bold"))
        label.place(x=200, y=20)

        self.imagen = Image.open(imagen_path)
        self.imagen = self.imagen.resize((300, 300)) 
        self.photo = ImageTk.PhotoImage(self.imagen)

        frame_imagen = tk.Frame(self, bg="white", width=400, height=300)
        frame_imagen.place(x=300, y=150)

        
        label_imagen = tk.Label(frame_imagen, image=self.photo, bg="white")
        label_imagen.pack(padx=10, pady=10)

        
        

        label = tk.Label(frame2, text=" Menu principal", bg="#000000", fg="#FFFFFF", font=("Segoe UI", 18, "bold"))
        label.place(x=0, y=20)

        label = tk.Label(frame2, text=" Opciones", bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12, "bold"))
        label.place(x=5, y=80)

        btn_inicio = tk.Button(frame2, text="Inicio", font=("Segoe UI", 12, "bold"), bg="#1DB954", fg="#000000", command=self.inicio)
        btn_inicio.place(x=20, y=130, height=40, width=150)

        btn_reproduccion = tk.Button(frame2, text="Reproducción", font=("Segoe UI", 12, "bold"),bg="#30c450", fg="#000000", command=self.reproduccion)
        btn_reproduccion.place(x=20, y=190, height=40, width=150)

        btn_buscar = tk.Button(frame2, text="Buscar", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.buscar)
        btn_buscar.place(x=20, y=250, height=40, width=150)

        btn_playlist = tk.Button(frame2, text="Playlist", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.playlist)
        btn_playlist.place(x=20, y=310, height=40, width=150)

        btn_agregar = tk.Button(frame2, text="Agregar", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.agregar)
        btn_agregar.place(x=20, y=370, height=40, width=150)

        btn_canciones = tk.Button(frame2, text="Canciones", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.canciones)
        btn_canciones.place(x=20, y=430, height=40, width=150)

        btn_canciones_escuchadas = tk.Button(frame2, text="Escuchadas", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.escuchadas)
        btn_canciones_escuchadas.place(x=20, y=490, height=40, width=150)
        
        btn_perfil = tk.Button(frame2, text="Perfil", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000",command=self.perfil)
        btn_perfil.place(x=20, y=550, height=40, width=150)   

        self.buttons = [
            btn_reproduccion,
            btn_buscar,
            btn_playlist,
            btn_agregar,
            btn_canciones,
            btn_canciones_escuchadas,
            btn_perfil
        ]
