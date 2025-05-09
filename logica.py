import threading
from tkinter import messagebox

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

contador_turnos = {k: 0 for k in SERVICIOS}
cola_turnos = []
historial_turnos = []
semaforo = threading.Semaphore()


def generar_turno(tipo, actualizar_callback):
    contador_turnos[tipo] += 1
    turno = f"{tipo}{contador_turnos[tipo]:03}"
    cola_turnos.append([turno, SERVICIOS[tipo], None])
    cola_turnos.sort(key=lambda x: PRIORIDAD_SERVICIOS[x[0][0]])
    actualizar_callback()
    messagebox.showinfo("Turno generado", f"Su turno es: {turno} - {SERVICIOS[tipo]}")


def actualizar_lista_turnos(lista_widget):
    lista_widget.delete(0, "end")
    for turno, servicio, ventanilla in cola_turnos:
        info = f"{turno} - {servicio}"
        if ventanilla:
            info += f" → Ventanilla {ventanilla}"
        lista_widget.insert("end", info)


def registrar_turno_en_historial(turno_info, cajero_id):
    historial_turnos.append((*turno_info, f"Cajero {cajero_id}"))


def atender_turno(ventana, cajero_id, var_estado, lista_turnos_widget, abrir_operacion):
    semaforo.acquire()
    if cola_turnos:
        turno_info = cola_turnos.pop(0)
        turno_info[2] = cajero_id
        registrar_turno_en_historial(turno_info, cajero_id)
        actualizar_lista_turnos(lista_turnos_widget)
        var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")
        ventana.after(100, lambda: abrir_operacion(cajero_id, var_estado, turno_info))
    else:
        var_estado.set("Sin turnos.")
    semaforo.release()


def mostrar_historial():
    historial_str = "\n".join([
        f"{t} - {s} → Ventanilla {v}" for t, s, v, _ in historial_turnos
    ]) or "Sin historial aún."
    messagebox.showinfo("Historial de Turnos", historial_str)
