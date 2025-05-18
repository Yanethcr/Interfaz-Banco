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
    "A": "Asesor",
    "T": "Tramitar tarjeta",
    "C": "Cancelar tarjeta"
}

PRIORIDAD_SERVICIOS = {
    "P": 1,
    "D": 2,
    "R": 3,
    "E": 4,
    "A": 5,
    "T": 6,
    "C": 7
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
    try:
        if cola_turnos:
            ahora = time.time()
            for t in cola_turnos:
                if ahora - t[3] > TIEMPO_MAX_ESPERA:
                    PRIORIDAD_SERVICIOS[t[0][0]] = 0  # Elevar su prioridad

            cola_turnos.sort(key=lambda x: (PRIORIDAD_SERVICIOS[x[0][0]], x[3]))

            turno_info = cola_turnos.pop(0)
            turno_info[2] = cajero_id

            servicio_letra = turno_info[0][0]
            servicio_nombre = turno_info[1]

            # NO pedir número de cuenta para tramitar/cancelar tarjeta
            if servicio_letra in ["T", "C"]:
                registrar_turno_en_historial(turno_info, cajero_id)
                actualizar_lista_turnos(lista_turnos_widget)
                return {"tipo": servicio_nombre, "turno_info": turno_info}

            numero_cuenta = simpledialog.askstring(
                "Número de Cuenta",
                "Por favor, ingrese su número de cuenta:",
                parent=ventana
            )

            cliente = buscar_cliente_por_cuenta(numero_cuenta)
            if not cliente:
                messagebox.showerror("Error", "Número de cuenta inválido.")
                cola_turnos.insert(0, turno_info)
                return

            registrar_turno_en_historial(turno_info, cajero_id)
            actualizar_lista_turnos(lista_turnos_widget)
            var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")

            return {"tipo": servicio_nombre, "cliente": cliente, "turno_info": turno_info}
        else:
            var_estado.set("Sin turnos.")
    finally:
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

# --- Lógica de anualidad de tarjeta de crédito ---

def calcular_pago_anualidad(cliente, meses):
    """Devuelve el monto a pagar cada mes según los meses elegidos."""
    if cliente["tipo_tarjeta"].lower() != "credito":
        return 0.0
    if meses < 1 or meses > 12:
        return 0.0
    return round(cliente.get("anualidad_pendiente", 0.0) / meses, 2)

def pagar_anualidad(cliente, monto):
    """Realiza el pago de la anualidad, descuenta saldo y anualidad pendiente, y registra el movimiento."""
    if monto <= 0 or monto > cliente.get("anualidad_pendiente", 0.0):
        return False, "Monto inválido."
    if monto > cliente["saldo"]:
        return False, "Saldo insuficiente."
    cliente["saldo"] -= monto
    cliente["anualidad_pendiente"] -= monto
    registrar_movimiento(cliente, "Pago Anualidad", monto)
    guardar_datos_clientes()
    return True, f"Pago de ${monto:.2f} realizado. Anualidad restante: ${cliente['anualidad_pendiente']:.2f}"

def crear_cliente(nombre, tipo_tarjeta, saldo, nip):
    nuevo_cliente = {
        "numero_cuenta": str(int(time.time() * 1000)),  # Genera un número único
        "id_cliente": f"C{len(clientes)+1:03}",
        "nombre_cliente": nombre,
        "tipo_tarjeta": tipo_tarjeta,
        "saldo": saldo,
        "nip": nip,
        "aclaraciones": [],
        "movimientos": []
    }
    if tipo_tarjeta.lower() == "credito":
        nuevo_cliente["anualidad_pendiente"] = 10000.0
    clientes.append(nuevo_cliente)
    guardar_datos_clientes()
    return nuevo_cliente

def cancelar_cliente(numero_cuenta):
    global clientes
    clientes = [c for c in clientes if c["numero_cuenta"] != numero_cuenta]
    guardar_datos_clientes()
    return True