import tkinter as tk
from tkinter import messagebox

COLOR_FONDO = "#121212"      # Fondo estilo Spotify
COLOR_PRIMARIO = "#1DB954"   # Verde Spotify
COLOR_TEXTO = "#FFFFFF"
COLOR_CARD = "#1E1E1E"

class Perfil(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_FONDO)
        self.controller = controller
        self.widgets()

    def widgets(self):
        # Título
        label = tk.Label(
            self, text="👤 Perfil de Spotify", 
            bg=COLOR_FONDO, fg=COLOR_PRIMARIO, 
            font=("Segoe UI", 18, "bold")
        )
        label.pack(pady=15)

        # Botón con hover
        self.btn_cargar = tk.Button(
            self, text="Cargar perfil", 
            bg=COLOR_PRIMARIO, fg="#000000",
            font=("Segoe UI", 12, "bold"),
            relief="flat", padx=10, pady=5,
            command=self.mostrar_perfil
        )
        self.btn_cargar.pack(pady=10)

        # Hover en botón
        self.btn_cargar.bind("<Enter>", lambda e: self.btn_cargar.config(bg="#1ed760"))
        self.btn_cargar.bind("<Leave>", lambda e: self.btn_cargar.config(bg=COLOR_PRIMARIO))

        # Tarjeta con los datos
        frame_card = tk.Frame(self, bg=COLOR_CARD, bd=2, relief="groove")
        frame_card.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Widget de texto para mostrar info
        self.text_info = tk.Text(
            frame_card,
            bg=COLOR_CARD, fg=COLOR_TEXTO,
            font=("Consolas", 12),
            wrap="word", height=15,
            bd=0, padx=10, pady=10
        )
        self.text_info.pack(fill=tk.BOTH, expand=True)

        # Hacer que el Text sea solo lectura
        self.text_info.config(state="disabled")

    def mostrar_perfil(self):
        try:
            perfil = self.controller.sp.current_user()  # usa la instancia de Spotify del controlador

            # Limpiar el Text
            self.text_info.config(state="normal")
            self.text_info.delete(1.0, tk.END)

            # Insertar datos con formato
            datos = [
                ("Nombre", perfil.get("display_name", "N/A")),
                ("ID", perfil.get("id", "N/A")),
                ("Email", perfil.get("email", "N/A")),
                ("País", perfil.get("country", "N/A")),
                ("Tipo de cuenta", perfil.get("product", "N/A")),
                ("Seguidores", perfil["followers"]["total"]),
                ("URL", perfil["external_urls"]["spotify"]),
            ]

            if perfil.get("images"):
                datos.append(("Imagen", perfil["images"][0]["url"]))
            else:
                datos.append(("Imagen", "Sin foto"))

            for campo, valor in datos:
                self.text_info.insert(tk.END, f"{campo:<15}: {valor}\n")

            self.text_info.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el perfil: {e}")
