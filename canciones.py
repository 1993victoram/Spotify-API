import tkinter as tk
from tkinter import messagebox
import openpyxl
import os, sys

def resource_path(relative_path):
    """Obtiene la ruta correcta cuando se ejecuta en .exe o en .py normal"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

COLOR_FONDO = "#000000"
COLOR_FONDO_OSCURO = "#1E1E1E"
COLOR_PRIMARIO = "#30c450"
COLOR_TEXTO = "#FFFFFF"
COLOR_SECUNDARIO = "#4A4D46"


class Canciones(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_FONDO)
        self.controller = controller
        self.playlists = []
        self.widgets()

    def cargar_playlists(self):
        if not self.controller or not getattr(self.controller, "sp", None):
            messagebox.showerror("Error", "Controller o controller.sp no inicializado.")
            return

        try:
            results = self.controller.sp.current_user_playlists()
            self.playlists = []
            self.lb_playlists.delete(0, tk.END)

            for playlist in results['items']:
                self.playlists.append({
                    "id": playlist["id"],
                    "nombre": playlist["name"],
                })
                self.lb_playlists.insert(tk.END, playlist["name"])

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las playlists: {e}")

    def abrir_canciones_en_ventana(self, event=None):
        seleccion = self.lb_playlists.curselection()
        if not seleccion:
            return

        index = seleccion[0]
        playlist = self.playlists[index]

        top = tk.Toplevel(self)
        top.title(f"Canciones - {playlist['nombre']}")
        top.geometry("950x550")
        top.configure(bg=COLOR_FONDO)
        # Usamos resource_path para el icono
        icono_path = resource_path("imagenes/icono.ico")
        top.iconbitmap(icono_path)

        tk.Label(top, text=f"Canciones de: {playlist['nombre']}",
                 bg=COLOR_FONDO, fg=COLOR_PRIMARIO,
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        # --- Barra de búsqueda ---
        frame_search = tk.Frame(top, bg=COLOR_FONDO)
        frame_search.pack(pady=5)

        tk.Label(frame_search, text="🔎 Buscar: ",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=5)

        entry_search = tk.Entry(frame_search, width=40,
                                font=("Segoe UI", 10))
        entry_search.pack(side=tk.LEFT, padx=5)

        
        frame_table = tk.Frame(top, bg=COLOR_FONDO)
        frame_table.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        header = tk.Label(frame_table,
                          text=f"{'Nombre':40} {'Artista':25} {'Álbum':25} {'Duración':8}",
                          bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO,
                          font=("Consolas", 11, "bold"), anchor="w")
        header.pack(fill=tk.X)

        lb_songs = tk.Listbox(frame_table, bg=COLOR_FONDO_OSCURO, fg=COLOR_TEXTO,
                              selectbackground=COLOR_PRIMARIO, selectforeground="#000000",
                              font=("Consolas", 11), activestyle="none")
        lb_songs.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        sb = tk.Scrollbar(frame_table, command=lb_songs.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        lb_songs.config(yscrollcommand=sb.set)

        canciones_guardadas = []   
        canciones_filtradas = []   

        # --- Exportar Excel ---
        def exportar_excel():
            try:
                wb = openpyxl.Workbook()
                ws = wb.active
                ws.title = "Canciones"
                ws.append(["Nombre", "Artista", "Álbum", "Duración"])

                for fila in canciones_guardadas:
                    ws.append(fila)

                archivo = "canciones.xlsx"
                wb.save(archivo)
                messagebox.showinfo("Éxito", f"Canciones exportadas a '{archivo}'")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

        tk.Button(top, text="💾 Exportar a Excel",
                  bg=COLOR_PRIMARIO, fg="#000000",
                  font=("Segoe UI", 10, "bold"),
                  command=exportar_excel).pack(pady=10)

        # --- Filtro dinámico ---
        def filtrar(event=None):
            texto = entry_search.get().lower()
            lb_songs.delete(0, tk.END)
            canciones_filtradas.clear()

            for nombre, artista, album, duracion in canciones_guardadas:
                if (texto in nombre.lower() or
                        texto in artista.lower() or
                        texto in album.lower()):
                    canciones_filtradas.append((nombre, artista, album, duracion))
                    linea = f"{nombre:40} {artista:25} {album:25} {duracion:>8}"
                    lb_songs.insert(tk.END, linea)

        entry_search.bind("<KeyRelease>", filtrar)

        # --- Cargar canciones en lotes ---
        def cargar_lote(offset=0, limit=100):
            try:
                results = self.controller.sp.playlist_items(playlist["id"], offset=offset, limit=limit)
                items = results["items"]

                if not items:
                    return

                for item in items:
                    track = item.get("track")
                    if track:
                        nombre = track["name"][:38]
                        artista = track["artists"][0]["name"][:23]
                        album = track["album"]["name"][:23]
                        duracion_ms = track["duration_ms"]
                        minutos = duracion_ms // 60000
                        segundos = (duracion_ms // 1000) % 60
                        duracion = f"{minutos}:{segundos:02d}"

                        fila = (nombre, artista, album, duracion)
                        canciones_guardadas.append(fila)

                        texto = f"{nombre:40} {artista:25} {album:25} {duracion:>8}"
                        lb_songs.insert(tk.END, texto)

                # Programar siguiente lote
                top.after(100, lambda: cargar_lote(offset + limit, limit))

            except Exception as e:
                messagebox.showerror("Error", f"No se pudieron cargar las canciones: {e}")
                top.destroy()

        # arranca con el primer lote
        cargar_lote()

    def widgets(self):
        tk.Label(self, text="Tus Playlists",
                 bg=COLOR_FONDO, fg=COLOR_TEXTO,
                 font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.lb_playlists = tk.Listbox(self, bg=COLOR_SECUNDARIO, fg=COLOR_TEXTO,
                                       selectbackground=COLOR_PRIMARIO, selectforeground="#000000",
                                       font=("Segoe UI", 11), activestyle="none")
        self.lb_playlists.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        sb_p = tk.Scrollbar(self.lb_playlists, command=self.lb_playlists.yview)
        sb_p.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb_playlists.config(yscrollcommand=sb_p.set)

        self.lb_playlists.bind("<Double-1>", self.abrir_canciones_en_ventana)

        tk.Button(self, text="Recargar playlists",
                  bg=COLOR_PRIMARIO, fg="#000000",
                  font=("Segoe UI", 10, "bold"),
                  command=self.cargar_playlists).pack(pady=5, fill=tk.X, padx=20)
