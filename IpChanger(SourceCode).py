import subprocess
import ctypes
import sys
import os
import platform
import threading
import time

from tkinter import *

def centrar_ventana(ventana):
    ventana.update_idletasks()  
    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()
    ancho_pantalla = ventana.winfo_screenwidth()
    alto_pantalla = ventana.winfo_screenheight()

    # Calcula las coordenadas para centrar la ventana
    pos_x = (ancho_pantalla // 2) - (ancho_ventana // 2)
    pos_y = (alto_pantalla // 2) - (alto_ventana // 1)

    # Define la geometría de la ventana
    ventana.geometry(f"{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}")


class Interface(Frame):
    def __init__(self, master=None):
        super().__init__(master, bg="Grey")
        self.master = master
        self.pack()
        self.ip_privada = self.obtener_ip_privada()
        self.puerta_enlace = self.obtener_puerta_de_enlace()
        self.crear_widgets()
        self.estado_ping = None  # Variable para el estado del ping

        # Inicia hilos para verificar ping y monitorear cambios de IP
        self.hilo_ping = threading.Thread(target=self.verificar_estado_ping, daemon=True)
        self.hilo_ping.start()

        self.hilo_ip_monitor = threading.Thread(target=self.monitorear_cambio_ip, daemon=True)
        self.hilo_ip_monitor.start()

    

    def crear_widgets(self):
        self.lbl1 = Label(self, text=f"IP actual es {self.ip_privada}", bg="Grey") 
        self.lbl1.grid(row=0, column=0, padx=10, pady=2, sticky="w", ipady=5)

        self.lbl_ping_estado = Label(self, text="", bg="Grey", font=("Arial", 9, "bold"))
        self.lbl_ping_estado.grid(row=0, column=1, padx=10, pady=2, sticky="w", ipady=5)
        
        self.lbl2 = Label(self, text="Ingrese una nueva IP:", bg="Grey")
        self.lbl2.grid(row=2, column=0, padx=10, pady=1, sticky="w", ipady=5)

        self.ipcontainer = Entry(self)
        self.ipcontainer.grid(row=2, column=1, padx=1, pady=1, ipady=5)

        self.ipcontainer.bind("<Return>", lambda event: self.cambiar_ip())

        self.lbl3 = Label(self, text="Formato: 0.0.0.0", bg="Grey")
        self.lbl3.grid(row=2, column=2, padx=6, pady=1, ipady=5)

        self.bttn = Button(self, text="Cambiar", bg="Grey", fg="Black", activebackground="Grey", command=self.cambiar_ip)
        self.bttn.grid(row=2, column=3, padx=6, pady=2, ipadx=10, ipady=4)

        

    def obtener_ip_privada(self):
        try:
            resultado = subprocess.check_output(
                "ipconfig", text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for linea in resultado.splitlines():
                if "IPv4" in linea or "Dirección IPv4" in linea:
                    partes = linea.split(":")
                    if len(partes) > 1:
                        return partes[1].strip()
        except Exception as e:
            return f"Error al obtener la IP privada: {e}"
        return "No disponible"
        
    def obtener_puerta_de_enlace(self):
        try:
            resultado = subprocess.check_output(
                "ipconfig", text=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            for linea in resultado.splitlines():
                if "predeterminada" in linea or "Puerta de enlace predeterminada" in linea:
                    partes = linea.split(":")
                    if len(partes) > 1:
                        return partes[1].strip()
        except Exception as e:
            return f"Error al obtener la puerta de enlace: {e}"
        return "No disponible"

    def cambiar_ip(self):
        nueva_ip = self.ipcontainer.get()
        interface = "Ethernet" 
        mascara_red = "255.255.255.0" 
        puerta_enlace = self.puerta_enlace
        try:
            subprocess.run(
                [
                    "netsh", "interface", "ip", "set", "address", 
                    f"name={interface}", "static", nueva_ip, mascara_red, puerta_enlace
                ],
                check=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
        except subprocess.CalledProcessError as e:
            print(f"Error al cambiar la IP: {e}")

    def ping_google_dns(self):
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", "8.8.8.8"]

        try:
            subprocess.run(
                command, capture_output=True, text=True, check=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def verificar_estado_ping(self):
        while True:
            estado_actual = self.ping_google_dns()
            if estado_actual != self.estado_ping:  # Solo actualiza si hay un cambio
                self.estado_ping = estado_actual
                self.master.after(0, self.actualizar_estado_ping)
            time.sleep(2)  # Tiempo entre pings

    def actualizar_estado_ping(self):
        if self.estado_ping:
            self.lbl_ping_estado.config(text="Conectado", fg="green")
        else:
            self.lbl_ping_estado.config(text="Desconectado", fg="red")

    def monitorear_cambio_ip(self):
        while True:
            ip_actual = self.obtener_ip_privada()
            if ip_actual != self.ip_privada:  # Solo actualiza si hay un cambio
                self.ip_privada = ip_actual
                self.master.after(0, self.actualizar_ip_actual)
            time.sleep(2)  # Tiempo entre verificaciones

    def actualizar_ip_actual(self):
        self.lbl1.config(text=f"IP actual es {self.ip_privada}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def resource_path(relative_path):
    try:
        # PyInstaller almacena los archivos en una carpeta temporal
        base_path = sys._MEIPASS
    except AttributeError:
        # Si estás ejecutando el script directamente
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    if not is_admin():
        script = sys.executable
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 0x80000)
        sys.exit()

    root = Tk()
    root.title("IPChanger")
    root.resizable(False, False)
    app = Interface(master=root)
    root.iconbitmap("resources/wolf.ico")

    # Centrar la ventana antes de iniciar el bucle principal
    centrar_ventana(root)

    app.mainloop()

    # /// Este Programa fue creado por Jesus Valduz y es una beta y prueba para futuros proyectos, open source so u can do wathever u want with it :D
