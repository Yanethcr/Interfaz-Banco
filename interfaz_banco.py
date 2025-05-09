import tkinter as tk
from tkinter import ttk
from logica import (
    generar_turno,
    actualizar_lista_turnos,
    atender_turno,
    mostrar_historial
)

# Configuraciones visuales
COLOR_FONDO = "#121212"
COLOR_PRIMARIO = "#FFD700"
COLOR_SECUNDARIO = "#D4AF37"
COLOR_TEXTO = "#FFFFFF"
COLOR_LISTA_FONDO = "#1E1E1E"
COLOR_BOTON_ACTIVO = "#D4AF37"
COLOR_BORDE = "#FFD700"

SERVICIOS = {
    "R": "Retiro",
    "D": "Depósito",
    "P": "Pago tarjeta",
    "E": "Estado de cuenta",
    "A": "Aclaraciones"
}

# INTERFAZ PRINCIPAL
ventana = tk.Tk()
ventana.title("Sistema de Turnos Bancarios - MultiCajero")
ventana.geometry("900x900")
ventana.config(bg=COLOR_FONDO)

estilo = {
    'font': ("Arial", 12),
    'bg': COLOR_FONDO,
    'fg': COLOR_PRIMARIO,
    'activebackground': COLOR_BOTON_ACTIVO,
    'activeforeground': COLOR_FONDO,
    'highlightbackground': COLOR_BORDE
}

# Título principal
tk.Label(ventana, text="Sistema de Turnos Bancarios", 
         font=("Arial", 18, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=20)

tk.Label(ventana, text="Seleccione un servicio:", 
         font=("Arial", 14), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=10)

# Botones de servicio
for letra, servicio in SERVICIOS.items():
    tk.Button(
        ventana,
        text=servicio,
        **estilo,
        width=25,
        highlightthickness=2,
        relief="groove",
        command=lambda l=letra: generar_turno(l, lambda: actualizar_lista_turnos(lista_turnos))
    ).pack(pady=5)

# Lista de turnos
lista_turnos = tk.Listbox(
    ventana,
    width=50,
    height=15,
    font=("Courier", 10),
    bg=COLOR_LISTA_FONDO,
    fg=COLOR_PRIMARIO,
    selectbackground=COLOR_SECUNDARIO,
    selectforeground=COLOR_FONDO,
    highlightthickness=1,
    highlightbackground=COLOR_BORDE,
    relief="solid"
)
lista_turnos.pack(pady=10)

# Botón historial
tk.Button(
    ventana,
    text="Ver historial de turnos atendidos",
    **estilo,
    command=mostrar_historial
).pack(pady=20)

# FUNCION DE VENTANA DE OPERACION

def abrir_ventana_operacion(cajero_id, var_estado, turno_info):
    ventana_operacion = tk.Toplevel()
    ventana_operacion.title(f"Ventanilla {cajero_id} - {turno_info[1]}")
    ventana_operacion.geometry("400x300")
    ventana_operacion.config(bg=COLOR_FONDO)
    ventana_operacion.resizable(False, False)

    frame = tk.Frame(ventana_operacion, bg=COLOR_FONDO, padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text=f"Atendiendo turno: {turno_info[0]}", 
             font=("Arial", 14), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=10)

    servicio = turno_info[1]

    def finalizar_operacion():
        ventana_operacion.destroy()
        var_estado.set("Esperando...")

    if servicio == "Depósito":
        tk.Label(frame, text="Cantidad a depositar:", 
                font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
        entrada = ttk.Entry(frame, font=("Arial", 12))
        entrada.pack(pady=10)
        entrada.focus()
        ttk.Button(frame, text="Confirmar Depósito", command=finalizar_operacion).pack(pady=20)
        ventana_operacion.bind('<Return>', lambda e: finalizar_operacion())

    elif servicio == "Retiro":
        tk.Label(frame, text="Cantidad a retirar:", 
                font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
        entrada = ttk.Entry(frame, font=("Arial", 12))
        entrada.pack(pady=10)
        entrada.focus()
        ttk.Button(frame, text="Confirmar Retiro", command=finalizar_operacion).pack(pady=20)
        ventana_operacion.bind('<Return>', lambda e: finalizar_operacion())

    elif servicio == "Pago tarjeta":
        tk.Label(frame, text="Número de tarjeta:", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=5)
        ttk.Entry(frame, font=("Arial", 12)).pack(pady=5)
        tk.Label(frame, text="Monto a pagar:", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=5)
        ttk.Entry(frame, font=("Arial", 12)).pack(pady=5)
        ttk.Button(frame, text="Confirmar Pago", command=finalizar_operacion).pack(pady=20)
        ventana_operacion.bind('<Return>', lambda e: finalizar_operacion())

    elif servicio == "Estado de cuenta":
        tk.Label(frame, text="Consultando estado de cuenta...", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=20)
        tk.Label(frame, text="Saldo actual: $10,000.00", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=10)
        ttk.Button(frame, text="Cerrar Consulta", command=finalizar_operacion).pack(pady=20)

    elif servicio == "Aclaraciones":
        tk.Label(frame, text="Descripción de la aclaración:", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
        tk.Text(frame, font=("Arial", 12), height=5, width=30).pack(pady=10)
        ttk.Button(frame, text="Registrar Aclaración", command=finalizar_operacion).pack(pady=20)

    ventana_operacion.protocol("WM_DELETE_WINDOW", finalizar_operacion)

# PANEL DE CAJEROS
ventana2 = tk.Toplevel(ventana)
ventana2.title("Panel de Cajeros")
ventana2.geometry("600x600")
ventana2.config(bg=COLOR_FONDO)

NUM_CAJEROS = 5
for i in range(1, NUM_CAJEROS + 1):
    frame = tk.Frame(
        ventana2,
        bg=COLOR_FONDO,
        bd=2,
        highlightbackground=COLOR_BORDE,
        highlightthickness=2,
        padx=10,
        pady=10
    )
    frame.pack(pady=10, fill="x", padx=20)

    tk.Label(frame, text=f"Cajero {i}", font=("Arial", 12, "bold"), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(anchor="w")
    estado_var = tk.StringVar(value="Esperando...")
    tk.Label(frame, textvariable=estado_var, font=("Arial", 11), bg=COLOR_FONDO, fg=COLOR_SECUNDARIO).pack(anchor="w", pady=5)
    tk.Button(frame, text="Atender siguiente turno", **estilo,
              command=lambda i=i, v=estado_var: atender_turno(ventana, i, v, lista_turnos, abrir_ventana_operacion)).pack(pady=5)

ventana.mainloop()
