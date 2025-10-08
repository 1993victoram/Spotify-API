import tkinter as tk
from tkinter import messagebox, ttk
import unicodedata  # necesario para normalizar texto

class Agregar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.playlists = []
        self.result_uris = []
        self.widgets()

    # 🔎 Normalizar texto para mejorar búsqueda
    def normalizar_texto(self, texto: str) -> str:
        """
        Convierte texto a minúsculas, sin acentos ni caracteres especiales.
        Ejemplo: 'Corazón Loco' -> 'corazon loco'
        """
        texto = texto.lower()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join(c for c in texto if not unicodedata.combining(c))
        return texto

    def cargar_playlists(self):
        if not self.controller or not getattr(self.controller, "sp", None):
            messagebox.showerror("Error", "Controller o controller.sp no inicializado.")
            return

        results = self.controller.sp.current_user_playlists()
        self.playlists = []
        for playlist in results['items']:
            self.playlists.append({"id": playlist["id"], "nombre": playlist["name"]})

        # actualizar OptionMenu
        values = [p['nombre'] for p in self.playlists]
        menu = self.option_menu["menu"]
        menu.delete(0, "end")
        for nombre in values:
            menu.add_command(label=nombre, command=lambda v=nombre: self.selected_playlist.set(v))

        if values:
            self.selected_playlist.set(values[0])  # selecciona la primera playlist

    def buscar_canciones(self):
        texto = self.entry_nombre.get().strip()
        if not texto:
            messagebox.showwarning("Advertencia", "Escribe el nombre de la canción o artista.")
            return

        texto_normalizado = self.normalizar_texto(texto)  # ✅ mejorar búsqueda

        try:
            results = self.controller.sp.search(q=texto_normalizado, type="track", limit=10)
            tracks = results["tracks"]["items"]

            self.result_uris = [t["uri"] for t in tracks]

            self.listbox_resultados.delete(0, tk.END)  # limpiar resultados
            for t in tracks:
                nombre = t["name"]
                artistas = ", ".join([a["name"] for a in t["artists"]])
                album = t["album"]["name"]
                self.listbox_resultados.insert(tk.END, f"{nombre} - {artistas} ({album})")

            if not tracks:
                messagebox.showinfo("Sin resultados", "No se encontraron canciones.")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo buscar la canción: {e}")

    def agregar_canciones(self):
        seleccion = self.selected_playlist.get()
        if not seleccion:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una playlist del menú.")
            return

        playlist = next((p for p in self.playlists if p['nombre'] == seleccion), None)
        if not playlist:
            messagebox.showerror("Error", "No se encontró la playlist seleccionada.")
            return

        # obtener selección de la lista
        sel = self.listbox_resultados.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Selecciona una canción de la lista.")
            return

        index = sel[0]
        track_uri = self.result_uris[index]

        try:
            self.controller.sp.playlist_add_items(playlist_id=playlist['id'], items=[track_uri])
            messagebox.showinfo("Éxito", f"Se agregó la canción a la playlist: {playlist['nombre']}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo agregar la canción: {e}")

    # 🎶 Reproducir canción con doble clic
    def reproducir_cancion(self, event):
        sel = self.listbox_resultados.curselection()
        if not sel:
            return
        index = sel[0]
        track_uri = self.result_uris[index]
        try:
            self.controller.sp.start_playback(uris=[track_uri])
            messagebox.showinfo("Reproducción", "Reproduciendo canción seleccionada 🎶")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo reproducir la canción: {e}")

    def widgets(self):
        frame5 = tk.Frame(self, bg="#000000", width=800, height=600)
        frame5.place(x=0, y=0, width=800, height=600)

        tk.Label(frame5, text="Agregar Canciones a Playlist", bg="#000000", fg="#FFFFFF",
                 font=("Segoe UI", 16, "bold")).place(x=20, y=20)

        # OptionMenu para playlists
        self.selected_playlist = tk.StringVar(value="")
        self.option_menu = tk.OptionMenu(frame5, self.selected_playlist, "")
        self.option_menu.config(width=40,
                                font=("Segoe UI", 12),
                                bg="#4A4D46", fg="#FFFFFF",
                                activebackground="#30c450",
                                activeforeground="#000000",
                                highlightthickness=0,
                                relief="flat")
        self.option_menu.place(x=50, y=100, height=30, width=290)

        btn_cargar = tk.Button(frame5, text="Cargar Playlists", font=("Segoe UI", 12, "bold"),
                               bg="#30c450", fg="#000000", command=self.cargar_playlists)
        btn_cargar.place(x=370, y=100, height=40, width=150)

        # Entrada para búsqueda
        label_nombre = tk.Label(frame5, text="Canción o artista:", bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        label_nombre.place(x=45, y=170)

        self.entry_nombre = tk.Entry(frame5, font=("Segoe UI", 12, "bold"), bg="#4A4D46", fg="#F5F5F5")
        self.entry_nombre.place(x=50, y=200, height=40, width=290)

        btn_buscar = tk.Button(frame5, text="Buscar", font=("Segoe UI", 12, "bold"),
                               bg="#30c450", fg="#000000", command=self.buscar_canciones)
        btn_buscar.place(x=370, y=200, height=40, width=150)

        # Listbox para mostrar resultados
        self.listbox_resultados = tk.Listbox(frame5, font=("Segoe UI", 12), bg="#1E1E1E", fg="#FFFFFF",
                                             selectbackground="#30c450", selectforeground="#000000")
        self.listbox_resultados.place(x=50, y=280, width=470, height=100)

        # 👉 Doble clic para reproducir
        self.listbox_resultados.bind("<Double-1>", self.reproducir_cancion)

        # Botón para agregar
        btn_agregar = tk.Button(frame5, text="Agregar Canción", font=("Segoe UI", 12, "bold"),
                                bg="#30c450", fg="#000000", command=self.agregar_canciones)
        btn_agregar.place(x=370, y=410, height=40, width=150)
