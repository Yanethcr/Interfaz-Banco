import threading
from tkinter import messagebox, simpledialog
import json
import time

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
cola_turnos = []  # [turno, servicio, ventanilla, timestamp]
historial_turnos = []
semaforo = threading.Semaphore()
mutex = threading.Lock()
quantum_tiempo = 5  # segundos
TIEMPO_MAX_ESPERA = 15  # segundos

def generar_turno(tipo, actualizar_callback):
    contador_turnos[tipo] += 1
    turno = f"{tipo}{contador_turnos[tipo]:03}"
    timestamp = time.time()
    cola_turnos.append([turno, SERVICIOS[tipo], None, timestamp])
    cola_turnos.sort(key=lambda x: (PRIORIDAD_SERVICIOS[x[0][0]], x[3]))
    actualizar_callback()
    messagebox.showinfo("Turno generado", f"Su turno es: {turno} - {SERVICIOS[tipo]}")

def actualizar_lista_turnos(lista_widget):
    lista_widget.delete(0, "end")
    for turno, servicio, ventanilla, _ in cola_turnos:
        info = f"{turno} - {servicio}"
        if ventanilla:
            info += f" → Ventanilla {ventanilla}"
        lista_widget.insert("end", info)

def registrar_turno_en_historial(turno_info, cajero_id):
    historial_turnos.append({
        "turno": turno_info[0],
        "servicio": turno_info[1],
        "ventanilla": cajero_id
    })

def atender_turno(ventana, cajero_id, var_estado, lista_turnos_widget, abrir_operacion):
    semaforo.acquire()
    if cola_turnos:
        ahora = time.time()
        for t in cola_turnos:
            if ahora - t[3] > TIEMPO_MAX_ESPERA:
                PRIORIDAD_SERVICIOS[t[0][0]] = 0  # Elevar su prioridad

        cola_turnos.sort(key=lambda x: (PRIORIDAD_SERVICIOS[x[0][0]], x[3]))

        turno_info = cola_turnos.pop(0)
        turno_info[2] = cajero_id

        numero_cuenta = simpledialog.askstring(
            "Número de Cuenta",
            "Por favor, ingrese su número de cuenta:",
            parent=ventana
        )

        cliente = buscar_cliente_por_cuenta(numero_cuenta)
        if not cliente:
            messagebox.showerror("Error", "Número de cuenta inválido.")
            cola_turnos.insert(0, turno_info)
            semaforo.release()
            return

        tiempo_inicial = time.time()
        tiempo_limite = tiempo_inicial + quantum_tiempo

        def tiempo_expirado():
            return time.time() >= tiempo_limite

        if turno_info[1] == "Retiro":
            registrar_turno_en_historial(turno_info, cajero_id)
            actualizar_lista_turnos(lista_turnos_widget)
            semaforo.release()
            return {"tipo": "Retiro", "cliente": cliente, "turno_info": turno_info}

        if turno_info[1] == "Depósito":
            registrar_turno_en_historial(turno_info, cajero_id)
            actualizar_lista_turnos(lista_turnos_widget)
            semaforo.release()
            return {"tipo": "Depósito", "cliente": cliente, "turno_info": turno_info}

        registrar_turno_en_historial(turno_info, cajero_id)
        actualizar_lista_turnos(lista_turnos_widget)
        var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")

        def cerrar_operacion_con_tiempo():
            if tiempo_expirado():
                var_estado.set("Quantum terminado. Siguiente cliente.")
                ventana.after(500, lambda: None)
            else:
                abrir_operacion(
                    cajero_id,
                    var_estado,
                    {"tipo": turno_info[1], "cliente": cliente, "turno_info": turno_info}
                )

        ventana.after(100, cerrar_operacion_con_tiempo)
    else:
        var_estado.set("Sin turnos.")
    semaforo.release()

def registrar_movimiento(cliente, tipo, monto):
    if "movimientos" not in cliente:
        cliente["movimientos"] = []
    cliente["movimientos"].append({
        "tipo": tipo,
        "monto": monto,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })
    guardar_datos_clientes()

def obtener_movimientos(cliente):
    return cliente.get("movimientos", [])

def realizar_retiro(cliente, monto):
    if monto > cliente["saldo"]:
        return False, "Saldo insuficiente para realizar el retiro."
    cliente["saldo"] -= monto
    registrar_movimiento(cliente, "Retiro", monto)
    guardar_datos_clientes()
    return True, f"Retiro de ${monto:.2f} realizado con éxito."

def realizar_deposito(cliente, monto):
    cliente["saldo"] += monto
    registrar_movimiento(cliente, "Depósito", monto)
    guardar_datos_clientes()
    return True, f"Depósito de ${monto:.2f} realizado con éxito."

def cancelar_turno(turno, lista_widget):
    global cola_turnos
    cola_turnos = [t for t in cola_turnos if t[0] != turno]
    lista_widget.delete(0, "end")
    for t in cola_turnos:
        lista_widget.insert("end", f"{t[0]} - {t[1]}")
    messagebox.showinfo("Turno Cancelado", f"El turno {turno} ha sido cancelado.")

def buscar_cliente_por_cuenta(numero_cuenta):
    for cliente in clientes:
        if cliente["numero_cuenta"] == numero_cuenta:
            return cliente
    return None

def guardar_datos_clientes():
    with mutex:
        with open("clientes.json", "w") as file:
            json.dump(clientes, file, indent=4)

def mostrar_historial():
    if not historial_turnos:
        messagebox.showinfo("Historial de Turnos", "No hay turnos atendidos aún.")
        return

    historial_str = "\n".join([
        f"Turno: {t['turno']} - Servicio: {t['servicio']} - Ventanilla: {t['ventanilla']}"
        for t in historial_turnos
    ])
    messagebox.showinfo("Historial de Turnos", historial_str)