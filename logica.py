import threading
from tkinter import messagebox, simpledialog
import json

# Cargar datos de clientes desde el archivo JSON
with open("clientes.json", "r") as file:
    clientes = json.load(file)

# Configuración de servicios y prioridades
SERVICIOS = {
    "R": "Retiro",
    "D": "Depósito",
    "P": "Pago tarjeta",
    "E": "Estado de cuenta",
    "A": "Aclaraciones"
}

PRIORIDAD_SERVICIOS = {
    "P": 1,
    "D": 2,
    "R": 3,
    "E": 4,
    "A": 5
}

# Variables globales
contador_turnos = {k: 0 for k in SERVICIOS}
cola_turnos = []
historial_turnos = []
semaforo = threading.Semaphore()

# Función para generar un turno
def generar_turno(tipo, actualizar_callback):
    contador_turnos[tipo] += 1
    turno = f"{tipo}{contador_turnos[tipo]:03}"
    cola_turnos.append([turno, SERVICIOS[tipo], None])
    cola_turnos.sort(key=lambda x: PRIORIDAD_SERVICIOS[x[0][0]])
    actualizar_callback()
    messagebox.showinfo("Turno generado", f"Su turno es: {turno} - {SERVICIOS[tipo]}")

# Función para actualizar la lista de turnos en la interfaz
def actualizar_lista_turnos(lista_widget):
    lista_widget.delete(0, "end")
    for turno, servicio, ventanilla in cola_turnos:
        info = f"{turno} - {servicio}"
        if ventanilla:
            info += f" → Ventanilla {ventanilla}"
        lista_widget.insert("end", info)

# Función para registrar un turno en el historial
def registrar_turno_en_historial(turno_info, cajero_id):
    historial_turnos.append({
        "turno": turno_info[0],
        "servicio": turno_info[1],
        "ventanilla": cajero_id
    })

# Función para atender un turno
def atender_turno(ventana, cajero_id, var_estado, lista_turnos_widget, abrir_operacion):
    semaforo.acquire()
    if cola_turnos:
        turno_info = cola_turnos.pop(0)  # Extraer el turno
        turno_info[2] = cajero_id  # Asignar el cajero al turno

        # Solicitar número de cuenta
        numero_cuenta = simpledialog.askstring(
            "Número de Cuenta",
            "Por favor, ingrese su número de cuenta:",
            parent=ventana
        )

        # Validar número de cuenta
        cliente = buscar_cliente_por_cuenta(numero_cuenta)
        if not cliente:
            messagebox.showerror("Error", "Número de cuenta inválido.")
            cola_turnos.insert(0, turno_info)  # Reinsertar el turno si falla
            semaforo.release()
            return

        # Si el servicio es "Retiro", registrar en el historial y devolver los datos necesarios
        if turno_info[1] == "Retiro":
            registrar_turno_en_historial(turno_info, cajero_id)  # Registrar en el historial
            actualizar_lista_turnos(lista_turnos_widget)
            semaforo.release()
            return {"tipo": "Retiro", "cliente": cliente, "turno_info": turno_info}

        # Registrar el turno en el historial para otros servicios
        registrar_turno_en_historial(turno_info, cajero_id)
        actualizar_lista_turnos(lista_turnos_widget)
        var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")
        ventana.after(100, lambda: abrir_operacion(cajero_id, var_estado, turno_info))
    else:
        var_estado.set("Sin turnos.")
    semaforo.release()
    semaforo.acquire()
    if cola_turnos:
        turno_info = cola_turnos.pop(0)  # Extraer el turno
        turno_info[2] = cajero_id  # Asignar el cajero al turno

        # Solicitar número de cuenta
        numero_cuenta = simpledialog.askstring(
            "Número de Cuenta",
            "Por favor, ingrese su número de cuenta:",
            parent=ventana
        )

        # Validar número de cuenta
        cliente = buscar_cliente_por_cuenta(numero_cuenta)
        if not cliente:
            messagebox.showerror("Error", "Número de cuenta inválido.")
            cola_turnos.insert(0, turno_info)  # Reinsertar el turno si falla
            semaforo.release()
            return

        # Si el servicio es "Retiro", devolver los datos necesarios
        if turno_info[1] == "Retiro":
            actualizar_lista_turnos(lista_turnos_widget)
            semaforo.release()
            return {"tipo": "Retiro", "cliente": cliente, "turno_info": turno_info}

        # Registrar el turno en el historial para otros servicios
        registrar_turno_en_historial(turno_info, cajero_id)
        actualizar_lista_turnos(lista_turnos_widget)
        var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")
        ventana.after(100, lambda: abrir_operacion(cajero_id, var_estado, turno_info))
    else:
        var_estado.set("Sin turnos.")
    semaforo.release()
    semaforo.acquire()
    if cola_turnos:
        turno_info = cola_turnos.pop(0)  # Extraer el turno
        turno_info[2] = cajero_id  # Asignar el cajero al turno

        # Solicitar número de cuenta
        numero_cuenta = simpledialog.askstring(
            "Número de Cuenta",
            "Por favor, ingrese su número de cuenta:",
            parent=ventana
        )

        # Validar número de cuenta
        cliente = buscar_cliente_por_cuenta(numero_cuenta)
        if not cliente:
            messagebox.showerror("Error", "Número de cuenta inválido.")
            cola_turnos.insert(0, turno_info)  # Reinsertar el turno si falla
            semaforo.release()
            return

        # Si el servicio es "Retiro", devolver los datos necesarios
        if turno_info[1] == "Retiro":
            actualizar_lista_turnos(lista_turnos_widget)
            semaforo.release()
            return {"tipo": "Retiro", "cliente": cliente, "turno_info": turno_info}

        # Registrar el turno en el historial para otros servicios
        registrar_turno_en_historial(turno_info, cajero_id)
        actualizar_lista_turnos(lista_turnos_widget)
        var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")
        ventana.after(100, lambda: abrir_operacion(cajero_id, var_estado, turno_info))
    else:
        var_estado.set("Sin turnos.")
    semaforo.release()

# Función para cancelar un turno
def cancelar_turno(turno, lista_widget):
    global cola_turnos
    cola_turnos = [t for t in cola_turnos if t[0] != turno]
    lista_widget.delete(0, "end")
    for t in cola_turnos:
        lista_widget.insert("end", f"{t[0]} - {t[1]}")
    messagebox.showinfo("Turno Cancelado", f"El turno {turno} ha sido cancelado.")

# Función para buscar un cliente por número de cuenta
def buscar_cliente_por_cuenta(numero_cuenta):
    for cliente in clientes:
        if cliente["numero_cuenta"] == numero_cuenta:
            return cliente
    return None

# Función para guardar los datos de los clientes en el archivo JSON
def guardar_datos_clientes():
    with open("clientes.json", "w") as file:
        json.dump(clientes, file, indent=4)

# Función para mostrar el historial de turnos atendidos
def mostrar_historial():
    if not historial_turnos:
        messagebox.showinfo("Historial de Turnos", "No hay turnos atendidos aún.")
        return

    historial_str = "\n".join([
        f"Turno: {t['turno']} - Servicio: {t['servicio']} - Ventanilla: {t['ventanilla']}"
        for t in historial_turnos
    ])
    messagebox.showinfo("Historial de Turnos", historial_str)