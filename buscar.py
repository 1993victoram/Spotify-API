import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as tb
import unicodedata
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def normalizar_texto(texto: str) -> str:
        """
        Convierte texto a minúsculas, sin acentos ni caracteres especiales.
        Ejemplo: 'Corazón Loco' -> 'corazon loco'
        """
        texto = texto.lower()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join(c for c in texto if not unicodedata.combining(c))
        return texto

class Buscar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#30c450")
        self.controller = controller
        self.playlists = []
        self.result_uris = []
        self.cache_canciones = {}  # caché simple por playlist_id
        self.indices_busqueda = {}  # índices de búsqueda por playlist_id
        self.widgets()

        
        
    def cargar_playlists(self):
        if not self.controller or not getattr(self.controller, "sp", None):
            messagebox.showerror("Error", "Controller o controller.sp no inicializado.")
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

            # Actualizar Listbox de playlists
            self.listbox_playlist.delete(0, tk.END)
            for p in self.playlists:
                self.listbox_playlist.insert(tk.END, p['nombre'])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las playlists: {e}")

    def obtener_canciones_playlist(self, playlist_id):
        # ⚡ Revisa si ya está en caché
        if playlist_id in self.cache_canciones:
            return self.cache_canciones[playlist_id]

        canciones = []
        try:
            offset = 0
            while True:
                res = self.controller.sp.playlist_items(
                    playlist_id,
                    limit=100,
                    offset=offset
                )
                items = res.get('items', [])
                if not items:
                    break

                for item in items:
                    track = item.get('track')
                    if not track:  # puede ser None si la canción fue eliminada
                        continue
                    nombre = track.get('name', '')
                    artistas = ", ".join([a.get('name', '') for a in track.get('artists', [])])
                    uri = track.get('uri', '')
                    canciones.append({
                        "nombre": nombre,
                        "artistas": artistas,
                        "uri": uri
                    })

                if not res.get('next'):
                    break
                offset += len(items)

            # ⚡ Guardar en caché
            self.cache_canciones[playlist_id] = canciones

            # ⚡ Crear índice de búsqueda normalizado
            indice = {}
            for c in canciones:
                texto = normalizar_texto(c['nombre'] + " " + c['artistas'])
                for palabra in texto.split():
                    if palabra not in indice:
                        indice[palabra] = []
                    indice[palabra].append(c)

            self.indices_busqueda[playlist_id] = indice

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener canciones: {e}")

        return canciones

    def buscar_cancion(self):
        sel = self.listbox_playlist.curselection()
        if not sel:
            messagebox.showwarning("Advertencia", "Selecciona una playlist primero.")
            return

        playlist_idx = sel[0]
        playlist_id = self.playlists[playlist_idx]['id']
        texto = self.entry_buscar.get().strip()
        if not texto:
            messagebox.showwarning("Advertencia", "Ingresa nombre de canción o artista.")
            return

        # ⚡ Normalizar texto de búsqueda
        texto = normalizar_texto(texto)
        palabras = texto.split()

        # ⚡ Asegurarnos que la playlist esté cargada
        canciones = self.obtener_canciones_playlist(playlist_id)

        indice = self.indices_busqueda.get(playlist_id, {})
        
        # ⚡ Buscar canciones que tengan TODAS las palabras
        resultados_sets = []
        for palabra in palabras:
            if palabra in indice:
                resultados_sets.append(set([c['uri'] for c in indice[palabra]]))
            else:
                resultados_sets.append(set())  # palabra que no existe en ninguna canción

        if not resultados_sets:
            resultados = []
        else:
            # Intersección: solo canciones que tengan todas las palabras
            uris_finales = set.intersection(*resultados_sets)
            resultados = [c for c in canciones if c['uri'] in uris_finales]

        # Mostrar resultados
        self.listbox_resultados.delete(0, tk.END)
        self.result_uris = []

        if resultados:
            for c in resultados:
                display = f"{c['nombre']} - {c['artistas']}"
                self.listbox_resultados.insert(tk.END, display)
                self.result_uris.append(c['uri'])
        else:
            self.listbox_resultados.insert(tk.END, "No se encontraron resultados.")


    def on_result_double_click(self, event):
        seleccion = self.listbox_resultados.curselection()
        if not seleccion:
            return

        idx = seleccion[0]
        texto = self.listbox_resultados.get(idx)

        # 👉 Evitar reproducir el mensaje de error
        if texto == "No se encontraron resultados.":
            return

        # ⚡ Tomar el URI desde los resultados filtrados
        if idx < len(self.result_uris):
            uri = self.result_uris[idx]
            try:
                self.controller.sp.start_playback(uris=[uri])
                messagebox.showinfo("Reproducción", f"▶ Reproduciendo: {texto}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo reproducir: {e}")


    def widgets(self):

        frame4 = tk.Frame(self, bg="#000000")
        frame4.place(x=0, y=0, width=800, height=600)

        self.listbox_playlist = tk.Listbox(self, font=("Segoe UI", 12), bg="#4A4D46", fg="#FFFFFF", width=50, height=15)
        self.listbox_playlist.place(x=50, y=30, height=100, width=290)

        btn_cargar = tk.Button(self, text="Cargar Playlists", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.cargar_playlists)
        btn_cargar.place(x=370, y=60, height=40, width=150)

        label2 = tk.Label(frame4, text=" Ingresa el nombre de la canción o artista:", bg="#000000", fg="#FFFFFF", font=("Segoe UI", 12))
        label2.place(x=45, y=170)
        

        self.entry_buscar = tk.Entry(self, font=("Segoe UI", 12,"bold"), bg="#4A4D46", fg="#F5F5F5")
        self.entry_buscar.place(x=50, y=200, height=40, width=290)

        btn_buscar = tk.Button(self, text="Buscar", font=("Segoe UI", 12, "bold"), bg="#30c450", fg="#000000", command=self.buscar_cancion)
        btn_buscar.place(x=370, y=200, height=40, width=150)

        self.listbox_resultados = tk.Listbox(frame4, font=("Segoe UI", 12), bg="#4A4D46", fg="#FFFFFF")
        self.listbox_resultados.place(x=50, y=250, width=290, height=200)
        self.listbox_resultados.bind("<Double-1>", self.on_result_double_click)

        label3 = tk.Label(frame4, text=" Nota:", bg="#000000", fg="#FFFFFF", font=("Segoe UI", 13, "bold"))
        label3.place(x=370, y=250)

        frame_nota = tk.Frame(frame4, bg="#4A4D46", width=150, height=130)
        frame_nota.place(x=370, y=280)
        nota_texto = ("Las canciones pueden \ntardar en cargar en la\nbusqueda al momento\nde seleccionar una\nplaylist por primera vez."
                      )
        label_nota = tk.Label(frame_nota, text=nota_texto, bg="#4A4D46", fg="#FFFFFF", font=("Segoe UI", 10), justify="left")
        label_nota.place(x=5, y=5)