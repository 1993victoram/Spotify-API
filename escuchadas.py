# escuchadas.py
import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import math
import openpyxl
import sqlite3
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image, ImageTk
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

DB_PATH = resource_path("spotifyAPI.db")


class Escuchadas(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_FONDO)
        self.controller = controller
        self.canciones_data = []  # canciones en memoria para exportar
        self.ventana = None       # referencia a la ventana del historial
        self.lb_songs = None      # listbox para mostrar canciones
        self.entry_buscar = None  # campo de búsqueda
        self.crear_db()
        self.widgets()

    # ---------------------- BASE DE DATOS ----------------------
    def crear_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id TEXT,
                nombre TEXT NOT NULL,
                artistas TEXT NOT NULL,
                album TEXT,
                duracion TEXT,
                played_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def guardar_reproduccion(self, track_id, nombre, artistas, album, duracion, fecha_str):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Evitar duplicados con el mismo track_id + fecha
        c.execute("""
            SELECT 1 FROM historial 
            WHERE track_id = ? AND played_at = ?
        """, (track_id, fecha_str))
        if not c.fetchone():
            c.execute("""
                INSERT INTO historial (track_id, nombre, artistas, album, duracion, played_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (track_id, nombre, artistas, album, duracion, fecha_str))
            conn.commit()
        conn.close()

    def cargar_historial(self, limit=50, filtro=None):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        query = """
            SELECT played_at, nombre, artistas, album, duracion
            FROM historial
        """
        params = ()

        if filtro:
            query += """
                WHERE nombre LIKE ? OR artistas LIKE ? OR played_at LIKE ?
            """
            filtro = f"%{filtro}%"
            params = (filtro, filtro, filtro)

        query += " ORDER BY datetime(played_at) DESC LIMIT ?"
        params = params + (limit,)

        c.execute(query, params)
        filas = c.fetchall()
        conn.close()
        return filas

    # ---------------------- INTERFAZ ----------------------
    def cargar_escuchadas(self):
        """Abrir/cerrar la ventana con las canciones escuchadas"""
        if not self.controller or not getattr(self.controller, "sp", None):
            messagebox.showerror("Error", "Controller o controller.sp no inicializado.")
            return

        # Si la ventana ya existe, la cerramos
        if self.ventana and tk.Toplevel.winfo_exists(self.ventana):
            self.ventana.destroy()
            self.ventana = None
            return

        try:
            hoy = self.controller.sp.current_user_recently_played(limit=50)
            canciones = hoy.get('items', [])

            # Guardar todas las canciones en DB
            for item in canciones:
                track = item['track']
                track_id = track['id']
                nombre = track['name']
                artistas = ', '.join(artist['name'] for artist in track['artists'])
                album = track['album']['name']

                # Duración en min:seg
                dur_ms = track['duration_ms']
                minutos = math.floor(dur_ms / 60000)
                segundos = math.floor((dur_ms % 60000) / 1000)
                duracion = f"{minutos}:{segundos:02d}"

                # Fecha reproducida
                played_at = item['played_at']
                fecha = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
                fecha_str = fecha.strftime("%Y-%m-%d %H:%M:%S")

                # Guardar en DB
                self.guardar_reproduccion(track_id, nombre, artistas, album, duracion, fecha_str)

            # Crear ventana
            self.crear_ventana_historial()

        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar las canciones escuchadas: {e}")

    def crear_ventana_historial(self):
        """Crea la ventana para mostrar historial desde DB"""
        self.ventana = tk.Toplevel(self)
        self.ventana.title("🎧 Canciones Escuchadas")
        self.ventana.geometry("950x550")
        self.ventana.configure(bg=COLOR_FONDO)
        # Usamos resource_path para el icono
        icono_path = resource_path("imagenes/icono.ico")
        self.ventana.iconbitmap(icono_path)

        tk.Label(
            self.ventana,
            text="🎧 Canciones Escuchadas",
            bg=COLOR_FONDO,
            fg=COLOR_PRIMARIO,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        # Campo de búsqueda
        frame_buscar = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame_buscar.pack(pady=5)
        tk.Label(frame_buscar, text="Buscar:", bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(side=tk.LEFT, padx=5)
        self.entry_buscar = tk.Entry(frame_buscar)
        self.entry_buscar.pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame_buscar, text="🔍", command=self.aplicar_filtro
        ).pack(side=tk.LEFT, padx=5)

        # Listbox con scroll
        frame_lista = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.lb_songs = tk.Listbox(
            frame_lista,
            bg=COLOR_FONDO_OSCURO,
            fg=COLOR_TEXTO,
            selectbackground=COLOR_PRIMARIO,
            selectforeground="#000000",
            font=("Consolas", 10),
            activestyle="none"
        )
        self.lb_songs.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = tk.Scrollbar(frame_lista, command=self.lb_songs.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb_songs.config(yscrollcommand=sb.set)

        # Botón exportar a Excel
        tk.Button(
            self.ventana,
            text="📂 Exportar a Excel",
            bg=COLOR_PRIMARIO,
            fg="#000000",
            font=("Segoe UI", 10, "bold"),
            command=self.exportar_excel
        ).pack(pady=10)

        # Cargar historial inicial
        self.mostrar_historial()

    def mostrar_historial(self, filtro=None):
        """Muestra el historial en el listbox"""
        if not self.lb_songs:
            return

        self.lb_songs.delete(0, tk.END)

        # Encabezado
        header = f"{'Fecha':<19} | {'Canción':<30} | {'Artista':<25} | {'Álbum':<20} | Duración"
        self.lb_songs.insert(tk.END, header)
        self.lb_songs.insert(tk.END, "-" * 120)

        historial = self.cargar_historial(50, filtro)
        self.canciones_data = historial  # se guarda para exportar
        for fila in historial:
            fecha, nombre, artistas, album, duracion = fila
            texto = f"{fecha:<19} | {nombre:<30.30} | {artistas:<25.25} | {album:<20.20} | {duracion}"
            self.lb_songs.insert(tk.END, texto)

    def aplicar_filtro(self):
        """Filtra el historial usando el texto en entry_buscar"""
        if self.entry_buscar:
            filtro = self.entry_buscar.get()
            self.mostrar_historial(filtro)

    def exportar_excel(self):
        """Exportar canciones a un archivo Excel"""
        if not self.canciones_data:
            messagebox.showwarning("Aviso", "No hay canciones para exportar.")
            return

        archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Guardar archivo como"
        )
        if not archivo:
            return

        try:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Escuchadas"

            # Encabezados
            encabezados = ["Fecha", "Canción", "Artista", "Álbum", "Duración"]
            ws.append(encabezados)

            # Datos
            for fila in self.canciones_data:
                ws.append(fila)

            wb.save(archivo)
            messagebox.showinfo("Éxito", f"Archivo guardado en:\n{archivo}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {e}")

    def cargar_cola(self):
        """Abrir/cerrar la ventana con la cola de reproducción"""
        if not self.controller or not getattr(self.controller, "sp", None):
            messagebox.showerror("Error", "Controller o controller.sp no inicializado.")
            return

        # Si la ventana ya existe, la cerramos
        if self.ventana and tk.Toplevel.winfo_exists(self.ventana):
            self.ventana.destroy()
            self.ventana = None
            return

        try:
            queue = self.controller.sp.queue()
            current = queue.get("currently_playing")
            upcoming = queue.get("queue", [])

            # Crear ventana
            self.ventana = tk.Toplevel(self)
            self.ventana.title("🎶 Cola de Reproducción")
            self.ventana.geometry("950x550")
            self.ventana.configure(bg=COLOR_FONDO)
            # Usamos resource_path para el icono
            icono_path = resource_path("imagenes/icono.ico")
            self.ventana.iconbitmap(icono_path)
            

            tk.Label(
                self.ventana,
                text="🎶 Cola de Reproducción",
                bg=COLOR_FONDO,
                fg=COLOR_PRIMARIO,
                font=("Segoe UI", 14, "bold")
            ).pack(pady=10)

            frame_lista = tk.Frame(self.ventana, bg=COLOR_FONDO)
            frame_lista.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            lb = tk.Listbox(
                frame_lista,
                bg=COLOR_FONDO_OSCURO,
                fg=COLOR_TEXTO,
                selectbackground=COLOR_PRIMARIO,
                selectforeground="#000000",
                font=("Consolas", 10),
                activestyle="none"
            )
            lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            sb = tk.Scrollbar(frame_lista, command=lb.yview)
            sb.pack(side=tk.RIGHT, fill=tk.Y)
            lb.config(yscrollcommand=sb.set)

            # Encabezado
            header = f"{'Posición':<9} | {'Canción':<30} | {'Artista':<25} | {'Álbum':<20} | Duración"
            lb.insert(tk.END, header)
            lb.insert(tk.END, "-" * 120)

            # Canción actual primero
            if current:
                nombre = current['name']
                artistas = ", ".join(a['name'] for a in current['artists'])
                album = current['album']['name']
                dur_ms = current['duration_ms']
                minutos = dur_ms // 60000
                segundos = (dur_ms % 60000) // 1000
                duracion = f"{minutos}:{segundos:02d}"

                lb.insert(tk.END, f"{'▶ Actual':<9} | {nombre:<30.30} | {artistas:<25.25} | {album:<20.20} | {duracion}")

            # Cola de canciones
            for i, track in enumerate(upcoming, start=1):
                nombre = track['name']
                artistas = ", ".join(a['name'] for a in track['artists'])
                album = track['album']['name']
                dur_ms = track['duration_ms']
                minutos = dur_ms // 60000
                segundos = (dur_ms % 60000) // 1000
                duracion = f"{minutos}:{segundos:02d}"

                lb.insert(tk.END, f"{i:<9} | {nombre:<30.30} | {artistas:<25.25} | {album:<20.20} | {duracion}")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la cola: {e}")


    def widgets(self):
        frame7 = tk.Frame(self, bg=COLOR_FONDO)
        frame7.place(x=0, y=0, width=800, height=600)

        tk.Label(
            frame7,
            text="🎧 Canciones Escuchadas",
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO,
            font=("Segoe UI", 16, "bold")
        ).place(x=20, y=20)

        btn_historial = tk.Button(
            self,
            text="Ver Historial",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_PRIMARIO,
            fg="#000000",
            command=self.cargar_escuchadas
        )
        btn_historial.place(x=100, y=430, width=150, height=40)

        btn_cola = tk.Button(
            self,
            text="Ver Cola",
            font=("Segoe UI", 12, "bold"),
            bg=COLOR_PRIMARIO,
            fg="#000000",
            command=self.cargar_cola
        )
        btn_cola.place(x=300, y=430, width=150, height=40)



