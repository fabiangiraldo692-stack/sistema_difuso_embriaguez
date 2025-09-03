import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# --- 1. Definición del sistema difuso ---
tiempo = ctrl.Antecedent(np.arange(0, 181, 1), 'tiempo')
peso = ctrl.Antecedent(np.arange(40, 151, 1), 'peso')
alcohol = ctrl.Antecedent(np.arange(0, 1001, 1), 'alcohol')
alcoholemia = ctrl.Consequent(np.arange(0, 201, 1), 'alcoholemia')

tiempo['poco'] = fuzz.trimf(tiempo.universe, [0, 0, 60])
tiempo['moderado'] = fuzz.trimf(tiempo.universe, [30, 90, 150])
tiempo['mucho'] = fuzz.trimf(tiempo.universe, [120, 180, 180])

peso['ligero'] = fuzz.trimf(peso.universe, [40, 40, 70])
peso['normal'] = fuzz.trimf(peso.universe, [60, 85, 110])
peso['pesado'] = fuzz.trapmf(peso.universe, [100, 150, 150, 150])

alcohol['poco'] = fuzz.trapmf(alcohol.universe, [0, 0, 100, 200])
alcohol['moderado'] = fuzz.trimf(alcohol.universe, [150, 350, 550])
alcohol['mucho'] = fuzz.trapmf(alcohol.universe, [450, 600, 1000, 1000])

alcoholemia['negativa'] = fuzz.trapmf(alcoholemia.universe, [0, 0, 10, 25])
alcoholemia['grado_0'] = fuzz.trimf(alcoholemia.universe, [20, 45, 70])
alcoholemia['primer_grado'] = fuzz.trimf(alcoholemia.universe, [50, 75, 100])
alcoholemia['segundo_grado'] = fuzz.trimf(alcoholemia.universe, [90, 130, 150])
alcoholemia['tercer_grado'] = fuzz.trapmf(alcoholemia.universe, [140, 160, 200, 200])

reglas = [
    ctrl.Rule(alcohol['poco'] & tiempo['mucho'], alcoholemia['negativa']),
    ctrl.Rule(alcohol['moderado'] & tiempo['mucho'] & peso['ligero'], alcoholemia['grado_0']),
    ctrl.Rule(alcohol['moderado'] & tiempo['poco'] & peso['normal'], alcoholemia['primer_grado']),
    ctrl.Rule(alcohol['mucho'] & tiempo['moderado'] & peso['ligero'], alcoholemia['segundo_grado']),
    ctrl.Rule(alcohol['mucho'] & tiempo['poco'], alcoholemia['tercer_grado']),
    ctrl.Rule(alcohol['poco'] & tiempo['moderado'] & peso['ligero'], alcoholemia['grado_0']),
    ctrl.Rule(alcohol['poco'] & tiempo['moderado'] & peso['normal'], alcoholemia['grado_0']),
    ctrl.Rule(alcohol['moderado'] & tiempo['moderado'] & peso['normal'], alcoholemia['primer_grado']),
    ctrl.Rule(alcohol['moderado'] & tiempo['moderado'] & peso['ligero'], alcoholemia['grado_0']),
    ctrl.Rule(alcohol['poco'] & tiempo['poco'] & peso['ligero'], alcoholemia['negativa']),
    ctrl.Rule(alcohol['moderado'] & tiempo['mucho'] & peso['normal'], alcoholemia['grado_0']),
    ctrl.Rule(alcohol['mucho'] & tiempo['moderado'] & peso['normal'], alcoholemia['primer_grado']),
    ctrl.Rule(alcohol['mucho'] & tiempo['mucho'], alcoholemia['primer_grado']),
    ctrl.Rule(alcohol['moderado'] & tiempo['poco'] & peso['ligero'], alcoholemia['grado_0'])
]

alcoholemia_ctrl = ctrl.ControlSystem(reglas)
simulador = ctrl.ControlSystemSimulation(alcoholemia_ctrl)

# --- 2. Interfaz gráfica ---
ventana = tk.Tk()
ventana.title("Sistema Difuso de Alcoholemia")

fig, ax = plt.subplots(ncols=2, nrows=2, figsize=(10, 8))
ax_alcohol = ax[0, 0]
ax_tiempo = ax[0, 1]
ax_peso = ax[1, 0]
ax_alcoholemia = ax[1, 1]
fig.tight_layout(pad=3.0)

def dibujar_conjunto(ax, universo, etiquetas, funciones, titulo):
    ax.clear()
    for nombre, mf in zip(etiquetas, funciones):
        ax.plot(universo, mf, label=nombre)
    ax.set_title(titulo)
    ax.set_ylabel("Grado de pertenencia")
    ax.set_xlabel("Valor")
    ax.legend()

dibujar_conjunto(ax_alcohol, alcohol.universe, alcohol.terms.keys(), [alcohol[term].mf for term in alcohol.terms], "Alcohol (mL)")
dibujar_conjunto(ax_tiempo, tiempo.universe, tiempo.terms.keys(), [tiempo[term].mf for term in tiempo.terms], "Tiempo (min)")
dibujar_conjunto(ax_peso, peso.universe, peso.terms.keys(), [peso[term].mf for term in peso.terms], "Peso (kg)")
dibujar_conjunto(ax_alcoholemia, alcoholemia.universe, alcoholemia.terms.keys(), [alcoholemia[term].mf for term in alcoholemia.terms], "Alcoholemia (mg/100mL)")

def dibujar_resultado(ax, valor, etiqueta):
    for line in ax.get_lines():
        if line.get_label() == etiqueta:
            line.remove()
    ax.axvline(valor, color='red', linestyle='--', label=etiqueta)
    ax.legend()

def dibujar_fusificacion(ax, valor):
    for line in ax.get_lines():
        if ':' in line.get_label():
            line.remove()

def obtener_grados_fusificados(valor_alcoholemia, umbral=0.1):
    grados = {
        'negativa': fuzz.interp_membership(alcoholemia.universe, alcoholemia['negativa'].mf, valor_alcoholemia),
        'grado_0': fuzz.interp_membership(alcoholemia.universe, alcoholemia['grado_0'].mf, valor_alcoholemia),
        'primer_grado': fuzz.interp_membership(alcoholemia.universe, alcoholemia['primer_grado'].mf, valor_alcoholemia),
        'segundo_grado': fuzz.interp_membership(alcoholemia.universe, alcoholemia['segundo_grado'].mf, valor_alcoholemia),
        'tercer_grado': fuzz.interp_membership(alcoholemia.universe, alcoholemia['tercer_grado'].mf, valor_alcoholemia)
    }
    # Filtrar grados con pertenencia significativa
    grados_significativos = [g for g, val in grados.items() if val > umbral]
    return grados_significativos


def calcular_alcoholemia():
    try:
        valor_alcohol = float(entrada_alcohol.get())
        valor_tiempo = float(entrada_tiempo.get())
        valor_peso = float(entrada_peso.get())

        simulador.input['alcohol'] = valor_alcohol
        simulador.input['tiempo'] = valor_tiempo
        simulador.input['peso'] = valor_peso

        simulador.compute()
        resultado = simulador.output['alcoholemia']

        dibujar_resultado(ax_alcohol, valor_alcohol, 'input_val')
        dibujar_resultado(ax_tiempo, valor_tiempo, 'input_val')
        dibujar_resultado(ax_peso, valor_peso, 'input_val')
        dibujar_resultado(ax_peso, valor_peso, 'input_val')
        dibujar_resultado(ax_alcoholemia, resultado, 'resultado')
        dibujar_fusificacion(ax_alcoholemia, resultado)  # 👈 Visualiza la fusificación

        fig.canvas.draw_idle()

        grados = obtener_grados_fusificados(resultado)

        # Detectar transiciones difusas entre grados
        transiciones = [
            ('grado_0', 'primer_grado'),
            ('primer_grado', 'segundo_grado'),
            ('segundo_grado', 'tercer_grado')
        ]

        mensajes_transicion = []
        for g1, g2 in transiciones:
            if g1 in grados and g2 in grados:
                mensajes_transicion.append(
                    f"⚠️ Atención: El grado de alcoholemia se encuentra en una zona de transición entre {g1.replace('_', ' ').capitalize()} y {g2.replace('_', ' ').capitalize()}."
                )

        if len(grados) == 1:
            clasificacion = grados[0].replace('_', ' ').capitalize()
        else:
            clasificacion = " y ".join([g.replace('_', ' ').capitalize() for g in grados])

        mensaje_extra = "\n\n" + "\n".join(mensajes_transicion) if mensajes_transicion else ""
        mensaje = (
        f"Grado de alcoholemia estimado: {resultado:.2f} mg/100 mL de sangre.\n\n"
        f"Clasificación: {clasificacion}"
        f"{mensaje_extra}"
        )
        messagebox.showinfo("Resultado del Sistema", mensaje)

    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {e}")

# --- 3. Entradas y botón ---
input_frame = tk.Frame(ventana)
input_frame.pack(side=tk.LEFT, padx=10, pady=10)

tk.Label(input_frame, text="Alcohol (mL):").grid(row=0, column=0)
entrada_alcohol = tk.Entry(input_frame)
entrada_alcohol.grid(row=0, column=1)

tk.Label(input_frame, text="Tiempo (min):").grid(row=1, column=0)
entrada_tiempo = tk.Entry(input_frame)
entrada_tiempo.grid(row=1, column=1)

tk.Label(input_frame, text="Peso (kg):").grid(row=2, column=0)
entrada_peso = tk.Entry(input_frame)
entrada_peso.grid(row=2, column=1)

boton_calcular = tk.Button(input_frame, text="Calcular", command=calcular_alcoholemia)
boton_calcular.grid(row=3, column=0, columnspan=2, pady=10)

# --- 4. Canvas embebido ---
canvas = FigureCanvasTkAgg(fig, master=ventana)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=1, padx=10, pady=10)

toolbar = NavigationToolbar2Tk(canvas, ventana)
toolbar.update()
canvas_widget.pack()

# --- 5. Ejecutar la aplicación ---
ventana.mainloop()