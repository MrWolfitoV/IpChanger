import subprocess
import ctypes
import sys

def is_admin():
    """Verifica si el script se está ejecutando como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    if not is_admin():
        script = sys.executable
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", script, params, None, 1)
        sys.exit()  
    else:
        print("El script está corriendo como administrador.")

def ejecutar_como_administrador():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception as e:
            print(f"Error al intentar ejecutar como administrador: {e}")
            sys.exit(1)

ejecutar_como_administrador()


def obtener_ip_privada():
    try:
        resultado = subprocess.check_output("ipconfig", text=True)
        for linea in resultado.splitlines():
            if "IPv4" in linea or "Dirección IPv4" in linea:
                partes = linea.split(":")
                if len(partes) > 1:
                    return partes[1].strip()
    except Exception as e:
        return f"Error al obtener la IP privada: {e}"
        
def obtener_puerta_de_enlace():
    try:
        resultado = subprocess.check_output("ipconfig", text=True)
        for linea in resultado.splitlines():
            if "predeterminada" in linea or "Puerta de enlace predeterminada" in linea:
                partes = linea.split(":")
                if len(partes) > 1:
                    return partes[1].strip()
    except Exception as e:
        return f"Error al obtener la puerta de enlace: {e}"

ip_privada = obtener_ip_privada()
puerta_enlace=obtener_puerta_de_enlace()


ip=input("Su IP actual es " + ip_privada + " y la puerta de enlace es "+ puerta_enlace +" ahora por favor ingrese la nueva IP: ")

def cambiar_ip_windows(interface, ip, mascara_subred, puerta_enlace):
    try:
        subprocess.run(
            [
                "netsh", "interface", "ip", "set", "address",
                interface, "static", ip, mascara_subred, puerta_enlace
            ],
            check=True
        )
        print(f"La IP de la interfaz {interface} se cambió a {ip}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al cambiar la IP: {e}")

    

print("Su IP se ha cambiado exitosamente a",ip)

cambiar_ip_windows("Ethernet", ip, "255.255.255.0", puerta_enlace)


