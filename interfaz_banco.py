import tkinter as tk
from tkinter import messagebox
import threading

SERVICIOS = {
    "R": "Retiro",
    "D": "Depósito",
    "P": "Pago tarjeta",
    "E": "Estado de cuenta",
    "A": "Aclaraciones"
}

contador_turnos = {k: 0 for k in SERVICIOS}
cola_turnos = []  # turno, servicio, ventanilla
historial_turnos = []
semaforo = threading.Semaphore()

def generar_turno(tipo):
    contador_turnos[tipo] += 1
    turno = f"{tipo}{contador_turnos[tipo]:03}"
    cola_turnos.append([turno, SERVICIOS[tipo], None])
    actualizar_lista_turnos()
    messagebox.showinfo("Turno generado", f"Su turno es: {turno} - {SERVICIOS[tipo]}")

def actualizar_lista_turnos():
    lista_turnos.delete(0, tk.END)
    for turno, servicio, ventanilla in cola_turnos:
        info = f"{turno} - {servicio}"
        if ventanilla:
            info += f" → Ventanilla {ventanilla}"
        lista_turnos.insert(tk.END, info)

def atender_turno_cajero(cajero_id, var_estado):
    semaforo.acquire()
    if cola_turnos:
        turno_info = cola_turnos.pop(0)
        turno_info[2] = cajero_id
        historial_turnos.append((*turno_info, f"Cajero {cajero_id}"))
        actualizar_lista_turnos()
        var_estado.set(f"Atendiendo: {turno_info[0]} ({turno_info[1]})")
    else:
        var_estado.set("Sin turnos.")
    semaforo.release()

# INTERFAZ
ventana = tk.Tk()
ventana.title("Sistema de Turnos Bancarios - MultiCajero")
ventana.geometry("650x600")
ventana.config(bg="#f2f2f2")

tk.Label(ventana, text="Seleccione un servicio:", font=("Arial", 14), bg="#f2f2f2").pack(pady=10)

for letra, servicio in SERVICIOS.items():
    tk.Button(
        ventana,
        text=servicio,
        font=("Arial", 12),
        width=25,
        command=lambda l=letra: generar_turno(l)
    ).pack(pady=3)

tk.Label(ventana, text="Turnos en espera:", font=("Arial", 12), bg="#f2f2f2").pack(pady=10)
lista_turnos = tk.Listbox(ventana, width=50, font=("Courier", 10))
lista_turnos.pack(pady=5)

# SCROLL ZONE PARA CAJEROS
frame_scroll = tk.Frame(ventana)
frame_scroll.pack(pady=10, fill="both", expand=True)

canvas = tk.Canvas(frame_scroll, bg="#f2f2f2", height=200)
scrollbar = tk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas, bg="#f2f2f2")

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Crear paneles para múltiples cajeros
NUM_CAJEROS = 5  # Puedes poner más aquí
for i in range(1, NUM_CAJEROS + 1):
    frame = tk.Frame(scrollable_frame, bg="#e6f7ff", bd=2, relief="groove", padx=10, pady=10)
    frame.pack(pady=5, fill="x", padx=10)

    tk.Label(frame, text=f"Cajero {i}", font=("Arial", 12, "bold"), bg="#e6f7ff").pack(anchor="w")
    estado_var = tk.StringVar()
    estado_var.set("Esperando...")
    tk.Label(frame, textvariable=estado_var, font=("Arial", 11), bg="#e6f7ff", fg="blue").pack(anchor="w", pady=5)
    tk.Button(
        frame,
        text="Atender siguiente turno",
        font=("Arial", 11),
        command=lambda cid=i, var=estado_var: atender_turno_cajero(cid, var)
    ).pack(pady=5)

# Botón para historial
def mostrar_historial():
    historial_str = "\n".join([f"{t} - {s} → Ventanilla {v}" for t, s, v, _ in historial_turnos]) or "Sin historial aún."
    messagebox.showinfo("Historial de Turnos", historial_str)

tk.Button(
    ventana,
    text="Ver historial de turnos atendidos",
    font=("Arial", 11),
    bg="#fff2cc",
    command=mostrar_historial
).pack(pady=10)

ventana.mainloop()

