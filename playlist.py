import tkinter as tk
from tkinter import messagebox


class Playlist(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.playlists = []
        self.result_uris = []

        self.widgets()

    def cargar_playlists(self):
        if not self.controller or not getattr(self.controller, "sp", None):
            messagebox.showerror("Error", "Controller o controller.sp no inicializado.")
            return

        try:
            results = self.controller.sp.current_user_playlists()
            self.playlists = []
            for playlist in results['items']:
                self.playlists.append({
                    "id": playlist["id"],
                    "nombre": playlist["name"],
                    "uri": playlist["uri"]   # 👈 ahora guardamos el URI
                })

            # actualizar OptionMenu
            values = [p['nombre'] for p in self.playlists]
            menu = self.option_menu["menu"]
            menu.delete(0, "end")
            for nombre in values:
                menu.add_command(label=nombre, command=lambda v=nombre: self.selected_playlist.set(v))

            if values:
                self.selected_playlist.set(values[0])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las playlists: {e}")

    def reproducir_playlist(self):
        seleccion = self.selected_playlist.get()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una playlist del menú.")
            return
        
        playlist = next((p for p in self.playlists if p['nombre'] == seleccion), None)
        if not playlist:
            messagebox.showerror("Error", "No se encontró la playlist seleccionada.")
            return

        try:
            self.controller.sp.start_playback(context_uri=playlist['uri'])
            messagebox.showinfo("Reproducción", f"Reproduciendo playlist: {playlist['nombre']}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir la playlist: {e}")

    def crear_playlist(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Advertencia", "El nombre de la playlist no puede estar vacío.")
            return
        
        try:
            self.playlists = []
            respuesta = self.controller.sp.current_user_playlists(limit=50)
            for p in respuesta['items']:
                self.playlists.append({
                    "nombre": p['name'],
                    "id": p['id'],
                    "uri": p['uri']
                })

            if nombre in [p['nombre'] for p in self.playlists]:
                messagebox.showwarning("Advertencia", "Ya existe una playlist con ese nombre.")
                return

            user_id = self.controller.sp.current_user()['id']
            nueva_playlist = self.controller.sp.user_playlist_create(user=user_id, name=nombre, public=False)
            if nueva_playlist:
                messagebox.showinfo("Éxito", f"Playlist '{nombre}' creada exitosamente.")
            else:
                messagebox.showerror("Error", "No se pudo crear la playlist.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la playlist: {e}")

    def widgets(self):
        frame4 = tk.Frame(self, bg="#000000")
        frame4.place(x=0, y=0, width=800, height=600)

        tk.Label(frame4, text="Cargar Playlists y reproducirlas", bg="#000000", fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).place(x=20, y=20)
        
        btn_cargar = tk.Button(frame4, text="Cargar Playlists", font=("Segoe UI", 12, "bold"), 
                               bg="#30c450", fg="#000000", command=self.cargar_playlists)
        btn_cargar.place(x=370, y=100, height=40, width=150)

        btn_reproducir = tk.Button(frame4, text="Reproducir Playlist", font=("Segoe UI", 12, "bold"), 
                                   bg="#30c450", fg="#000000", command=self.reproducir_playlist)   
        btn_reproducir.place(x=370, y=160, height=40, width=150)        

        self.selected_playlist = tk.StringVar(value="")
        self.option_menu = tk.OptionMenu(frame4, self.selected_playlist, "")
        self.option_menu.config(width=40,
                                font=("Segoe UI", 12),
                                bg="#4A4D46", fg="#FFFFFF",
                                activebackground="#30c450",
                                activeforeground="#000000",
                                highlightthickness=0,
                                relief="flat")
        self.option_menu.place(x=50, y=100, height=30, width=290)

        label_nombre = tk.Label(frame4, text=" Nombre de la nueva playlist:", 
                                bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        label_nombre.place(x=45, y=250)

        self.entry_nombre = tk.Entry(frame4, font=("Segoe UI", 12,"bold"), bg="#4A4D46", fg="#F5F5F5")
        self.entry_nombre.place(x=50, y=280, height=40, width=290)

        btn_crear = tk.Button(frame4, text="Crear Playlist", font=("Segoe UI", 12, "bold"), 
                              bg="#30c450", fg="#000000", command=self.crear_playlist)
        btn_crear.place(x=370, y=280, height=40, width=150)
