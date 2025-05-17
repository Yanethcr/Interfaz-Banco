import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from logica import (
    atender_turno, generar_turno, actualizar_lista_turnos,
    mostrar_historial, guardar_datos_clientes, realizar_retiro, realizar_deposito
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
def actualizar_turnos():
    actualizar_lista_turnos(lista_turnos)

for letra, servicio in SERVICIOS.items():
    tk.Button(
        ventana,
        text=servicio,
        **estilo,
        width=25,
        highlightthickness=2,
        relief="groove",
        command=lambda l=letra: generar_turno(l, actualizar_turnos)
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
def abrir_ventana_operacion(cajero_id, var_estado, resultado):
    # resultado es un dict: {"tipo": ..., "cliente": ..., "turno_info": ...}
    turno_info = resultado["turno_info"]
    servicio = turno_info[1]
    cliente = resultado.get("cliente")

    ventana_operacion = tk.Toplevel()
    ventana_operacion.title(f"Ventanilla {cajero_id} - {servicio}")
    ventana_operacion.geometry("400x300")
    ventana_operacion.config(bg=COLOR_FONDO)
    ventana_operacion.resizable(False, False)

    frame = tk.Frame(ventana_operacion, bg=COLOR_FONDO, padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text=f"Atendiendo turno: {turno_info[0]}",
             font=("Arial", 14), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=10)

    def finalizar_operacion():
        ventana_operacion.destroy()
        var_estado.set("Esperando...")

    if servicio == "Depósito":
        tk.Label(frame, text="Cantidad a depositar:",
                 font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
        entrada = ttk.Entry(frame, font=("Arial", 12))
        entrada.pack(pady=10)
        entrada.focus()

        def confirmar_deposito():
            try:
                monto = float(entrada.get())
                if not cliente:
                    messagebox.showerror("Error", "No se encontró el cliente para el depósito.")
                    return
                nip_ingresado = simpledialog.askstring("Validación NIP", "Ingrese su NIP:", show="*")
                if nip_ingresado != cliente["nip"]:
                    messagebox.showerror("Error", "NIP incorrecto. Operación cancelada.")
                    return
                exito, mensaje = realizar_deposito(cliente, monto)
                if exito:
                    messagebox.showinfo("Éxito", mensaje)
                    finalizar_operacion()
                else:
                    messagebox.showerror("Error", mensaje)
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto válido.")

        ttk.Button(frame, text="Confirmar Depósito", command=confirmar_deposito).pack(pady=20)

    elif servicio == "Retiro":
        abrir_ventana_retiro(cliente, turno_info, var_estado)

    elif servicio == "Pago tarjeta":
        tk.Label(frame, text="Número de tarjeta:", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=5)
        ttk.Entry(frame, font=("Arial", 12)).pack(pady=5)
        tk.Label(frame, text="Monto a pagar:", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=5)
        ttk.Entry(frame, font=("Arial", 12)).pack(pady=5)
        ttk.Button(frame, text="Confirmar Pago", command=finalizar_operacion).pack(pady=20)

    elif servicio == "Estado de cuenta":
        def mostrar_estado_cuenta():
            nip_ingresado = simpledialog.askstring("Validación NIP", "Ingrese su NIP:", show="*")
            if nip_ingresado != cliente["nip"]:
                messagebox.showerror("Error", "NIP incorrecto. Operación cancelada.")
                return
            from logica import obtener_movimientos
            movimientos = obtener_movimientos(cliente)

            ventana_estado = tk.Toplevel(ventana_operacion)
            ventana_estado.title("Estado de Cuenta")
            ventana_estado.geometry("500x500")
            ventana_estado.config(bg=COLOR_FONDO)

            frame_estado = tk.Frame(ventana_estado, bg=COLOR_FONDO, padx=20, pady=20)
            frame_estado.pack(expand=True, fill="both")

            info = (
                f"Nombre: {cliente['nombre_cliente']}\n"
                f"Número de cuenta: {cliente['numero_cuenta']}\n"
                f"Tipo de tarjeta: {cliente['tipo_tarjeta']}\n"
                f"Saldo actual: ${cliente['saldo']:.2f}\n"
                "\nMovimientos:\n"
            )
            if movimientos:
                for mov in movimientos:
                    info += f"{mov['timestamp']} - {mov['tipo']}: ${mov['monto']:.2f}\n"
            else:
                info += "Sin movimientos registrados.\n"

            tk.Label(frame_estado, text="ESTADO DE CUENTA", font=("Arial", 14, "bold"),
                     bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=10)
            text_widget = tk.Text(frame_estado, font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO, height=20, width=50)
            text_widget.pack()
            text_widget.insert("1.0", info)
            text_widget.config(state="disabled")

            ttk.Button(frame_estado, text="Cerrar", command=ventana_estado.destroy).pack(pady=10)

        ttk.Button(frame, text="Mostrar Estado de Cuenta", command=mostrar_estado_cuenta).pack(pady=20)

    elif servicio == "Aclaraciones":
        tk.Label(frame, text="Descripción de la aclaración:", font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
        tk.Text(frame, font=("Arial", 12), height=5, width=30).pack(pady=10)
        ttk.Button(frame, text="Registrar Aclaración", command=finalizar_operacion).pack(pady=20)

    ventana_operacion.protocol("WM_DELETE_WINDOW", finalizar_operacion)

# FUNCION PARA MANEJAR ATENCION DE TURNOS
def manejar_atencion_turno(cajero_id, var_estado):
    resultado = atender_turno(ventana, cajero_id, var_estado, lista_turnos, abrir_ventana_operacion)
    if resultado:
        var_estado.set(f"Atendiendo: {resultado['turno_info'][0]} ({resultado['turno_info'][1]})")
        if resultado["tipo"] == "Retiro":
            abrir_ventana_retiro(resultado["cliente"], resultado["turno_info"], var_estado)
        else:
            abrir_ventana_operacion(cajero_id, var_estado, resultado)
    else:
        var_estado.set("Sin turnos.")

def abrir_ventana_retiro(cliente, turno_info, var_estado):
    ventana_retiro = tk.Toplevel(ventana)
    ventana_retiro.title(f"Retiro - Turno {turno_info[0]}")
    ventana_retiro.geometry("400x300")
    ventana_retiro.config(bg=COLOR_FONDO)
    ventana_retiro.resizable(False, False)

    frame = tk.Frame(ventana_retiro, bg=COLOR_FONDO, padx=20, pady=20)
    frame.pack(expand=True, fill="both")

    tk.Label(frame, text=f"Atendiendo turno: {turno_info[0]}",
             font=("Arial", 14), bg=COLOR_FONDO, fg=COLOR_PRIMARIO).pack(pady=10)

    tk.Label(frame, text="Cantidad a retirar:",
             font=("Arial", 12), bg=COLOR_FONDO, fg=COLOR_TEXTO).pack(pady=10)
    entrada = ttk.Entry(frame, font=("Arial", 12))
    entrada.pack(pady=10)
    entrada.focus()

    def confirmar_retiro():
        try:
            monto_retiro = float(entrada.get())
            nip_ingresado = simpledialog.askstring("Validación NIP", "Ingrese su NIP:", show="*")
            if nip_ingresado != cliente["nip"]:
                messagebox.showerror("Error", "NIP incorrecto. Operación cancelada.")
                return
            exito, mensaje = realizar_retiro(cliente, monto_retiro)
            if exito:
                messagebox.showinfo("Éxito", mensaje)
                var_estado.set("Esperando...")
                ventana_retiro.destroy()
            else:
                messagebox.showerror("Error", mensaje)
        except ValueError:
            messagebox.showerror("Error", "Ingrese un monto válido.")

    ttk.Button(frame, text="Confirmar Retiro", command=confirmar_retiro).pack(pady=20)
    ventana_retiro.protocol("WM_DELETE_WINDOW", lambda: ventana_retiro.destroy())

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
              command=lambda i=i, v=estado_var: manejar_atencion_turno(i, v)).pack(pady=5)

ventana.mainloop()