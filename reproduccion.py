import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import spotipy
from spotipy.oauth2 import SpotifyOAuth

class Reproduccion(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.ultimo_track_id = None  # en vez de global
        self.widgets()
        self.refrescar_cancion_actual()  # iniciar refresco automático

    def obtener_cancion_actual(self):
        """Usa Spotipy para obtener la canción en reproducción"""
        try:
            playback = self.controller.sp.current_playback()
            if playback and playback["is_playing"]:
                track = playback["item"]
                return {
                    "id": track["id"],
                    "nombre": track["name"],
                    "artistas": ", ".join([a["name"] for a in track["artists"]]),
                    "album": track["album"]["name"],
                    "is_playing": True
                }
            return {"is_playing": False}
        except Exception as e:
            return None

    def guardar_reproduccion(self, track_id, nombre, artistas, album):
        """Ejemplo: aquí podrías guardar en la BD"""
        print(f"Guardado en DB: {nombre} - {artistas} ({album})")

    def refrescar_cancion_actual(self):
        """Actualiza UI cada 3s y registra en DB si cambió la canción."""
        info = self.obtener_cancion_actual()

        if info and info["is_playing"]:
            self.label_track.config(text=f"🎵 {info['nombre']}")
            self.label_artist.config(text=f"👤 {info['artistas']}")
            self.label_album.config(text=f"💿 {info['album']}")

            # Guardar si cambió el track
            if info["id"] and info["id"] != self.ultimo_track_id:
                self.ultimo_track_id = info["id"]
                try:
                    self.guardar_reproduccion(info["id"], info["nombre"], info["artistas"], info["album"])
                except Exception:
                    pass
        else:
            self.label_track.config(text="⏸ No hay música reproduciéndose")
            self.label_artist.config(text="")
            self.label_album.config(text="")

        # programar próxima actualización
        self.after(3000, self.refrescar_cancion_actual)
    
    def anterior(self):
        try:
            self.controller.sp.previous_track()
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo ir a la canción anterior:\n{e}")

    def play_pause(self):
        try:
            playback = self.controller.sp.current_playback()
            if playback and playback["is_playing"]:
                self.controller.sp.pause_playback()
            else:
                self.controller.sp.start_playback()
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo reproducir/pausar:\n{e}")
    
    def siguiente(self):
        try:
            self.controller.sp.next_track()
        except Exception as e:
            tk.messagebox.showerror("Error", f"No se pudo ir a la canción siguiente:\n{e}")

    

    def widgets(self):
        
        frame3 = tk.Frame(self, bg="#000000")
        frame3.place(x=0, y=0, width=800, height=600)

        tk.Label(frame3, text="Reproducción Spotify", bg="#000000", fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).place(x=20, y=20)

        # Labels dinámicos
        self.label_track = tk.Label(frame3, text="🎵 ---", bg="#000000", fg="#30c450", font=("Segoe UI", 14, "bold"))
        self.label_track.place(x=20, y=80)

        self.label_artist = tk.Label(frame3, text="👤 ---", bg="#000000", fg="#30c450", font=("Segoe UI", 12))
        self.label_artist.place(x=20, y=130)

        self.label_album = tk.Label(frame3, text="💿 ---", bg="#000000", fg="#30c450", font=("Segoe UI", 12))
        self.label_album.place(x=20, y=170)

        btn_anterior = tk.Button(frame3, text="⏮ Anterior", bg="#003cff", fg="#000000",
                                 font=("Segoe UI", 12, "bold"), command=self.anterior)
        btn_anterior.place(x=20, y=220, width=120, height=40)
       
        btn_play = tk.Button(frame3, text="▶ Play/Pause", bg="#003cff", fg="#000000",
                             font=("Segoe UI", 12, "bold"),command=self.play_pause)
        btn_play.place(x=150, y=220, width=120, height=40)
        
        btn_siguiente = tk.Button(frame3, text="⏭ Siguiente", bg="#003cff", fg="#000000",
                                  font=("Segoe UI", 12, "bold"),command=self.siguiente)
        btn_siguiente.place(x=280, y=220, width=120, height=40)

              

        
        
     
