import tkinter as tk
from tkinter import messagebox
import platform
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from container import Container
import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

class VentanaSpotify(tk.Frame):
    def __init__(self, parent, controller):
        # IMPORTANT: padre es el container de Manager
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.sp = None
        self.widgets()

    def autenticar(self):
            client_id = self.client_id_entry.get().strip()
            client_secret = self.client_secret_entry.get().strip()
            redirect_uri = self.redirect_uri_entry.get().strip()
            # Define los scopes necesarios para la aplicación(Permisos que va a necesitar)
            scope = " ".join([
                "user-library-read",
                "user-library-modify",
                "playlist-read-private",
                "playlist-read-collaborative",
                "playlist-modify-public",
                "playlist-modify-private",
                "user-read-playback-state",
                "user-modify-playback-state",
                "user-read-currently-playing",
                "user-read-recently-played",
                "user-top-read",
                "app-remote-control",
                "user-read-private",
                "user-follow-read",
                "user-follow-modify",
                "streaming",
                "ugc-image-upload",
                "user-read-playback-position"
            ])

             # Eliminar caché de autenticación previo
            if os.path.exists(".cache"):
                os.remove(".cache")

            if not client_id or not client_secret or not redirect_uri and scope:
                tk.messagebox.showerror("Error", "Por favor, completa todos los campos.")
                return

            try:
                
                self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                    client_id=client_id,
                    client_secret=client_secret,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    cache_path=None,
                    open_browser=True
                ))
                # Probar que realmente haya conexión solicitando info del usuario
                self.sp.current_user()
                messagebox.showinfo("Éxito", "Autenticación exitosa.")
                # Deshabilitar campos y botón
                self.client_id_entry.config(state='disabled')
                self.client_secret_entry.config(state='disabled')
                self.redirect_uri_entry.config(state='disabled')
                self.btn.config(state='disabled')
                self.controller.sp = self.sp #Guardar el objeto sp en el controller y se utiliza en reproduccion.py
                self.entrada()

                
            except Exception as e:
        # Si hay un error en la autenticación
                if "redirect_uri" in str(e).lower():
                    messagebox.showerror("Error de autenticación", "La dirección de redirección no existe o es incorrecta.")
                    return
                else:
                    messagebox.showerror("Error de autenticación", f"No se pudo autenticar:\n{e}")
                    return
            # Si la autenticación es exitosa, deshabilitar campos y botón
            self.client_id_entry.config(state='disabled')       
            return
              # Deshabilitar campos y botón después de la autenticación

        # Elementos de la interfaz
    def instrucciones(self):
        try:
            # 👉 Cambia esta ruta por la de tu archivo real
            archivo_pdf = r"C:\Users\Usuario\Desktop\Descargas\instrucciones.pdf"

            if not os.path.exists(archivo_pdf):
                messagebox.showerror("Error", f"No se encontró el archivo:\n{archivo_pdf}")
                return

            if platform.system() == "Windows":
                os.startfile(archivo_pdf)
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open '{archivo_pdf}'")
            else:  # Linux
                os.system(f"xdg-open '{archivo_pdf}'")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el PDF: {e}")
    
    def entrada(self):
        self.controller.show_frame(Container)


    def widgets(self):

            self.frame_spotify = tk.Frame(self, bg="#000000", width=550, height=400)
            self.frame_spotify.place(x=50, y=100)

            self.autenticacion = tk.Label(self, text="CONFIGURACIÓN DE AUTENTICACIÓN", bg="#30c450", fg="#000000", font=("Segoe UI", 14, "bold"))
            self.autenticacion.place(x=150, y=50)

            self.client_id_label = tk.Label(self, text="Client ID:", bg="#000000", fg="#ffffff", font=("Segoe UI", 12, "bold" ))
            self.client_id_label.place(x=100, y=180)

            self.client_id_entry = tk.Entry(self, font="Arial 13 bold",show="*" )
            self.client_id_entry.place(x=250, y=180, width=300)

            self.client_secret_label = tk.Label(self, text="Client secret:", bg="#000000", fg="#ffffff", font=("Segoe UI", 12, "bold" ))
            self.client_secret_label.place(x=100, y=240)

            self.client_secret_entry = tk.Entry(self, font="Arial 13 bold",show="*" )
            self.client_secret_entry.place(x=250, y=240, width=300)

            self.redirect_uri_label = tk.Label(self, text="Redirect uri:", bg="#000000", fg="#ffffff", font=("Segoe UI", 12, "bold" ))
            self.redirect_uri_label.place(x=100, y=300)

            self.redirect_uri_entry = tk.Entry(self, font="Arial 12 bold" )
            self.redirect_uri_entry.place(x=250, y=300, width=300)

            self.btn = tk.Button(self, text="Ingresar", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.autenticar)
            self.btn.place(x=250, y=350, height=40, width=150)

            self.btn_instrucciones = tk.Button(self, text="Instrucciones", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.instrucciones)
            self.btn_instrucciones.place(x=250, y=410, height=40, width=150)
        