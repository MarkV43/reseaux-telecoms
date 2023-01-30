import multiprocessing
from functools import partial
import PySimpleGUI as sg

import static_main
import partage_main
import adaptatif_main

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TkAgg")

left_column = [
    [sg.Text("Plot type:")],
    [sg.Radio("Loss Probability", 1, key="--LOSS--",
              default=True, enable_events=True)],
    [sg.Radio("Peak Response", 1, key="--PEAK--", enable_events=True)],
    [sg.HSeparator()],
    [sg.Text("Routing algorithms:")],
    [sg.Checkbox("Static", default=True, key="--STATIC--")],
    [sg.Checkbox("Load Balancer", default=True, key="--BALANCER--")],
    [sg.Checkbox("Adaptive", default=True, key="--ADAPTIVE--")],
    [sg.Checkbox("Adaptive + Delay", default=True, key="--ADAPTIVE-DELAY--", enable_events=True)],
    [sg.Text("Delay:"), sg.Push(), sg.Input(30, key="--DELAY--", size=(5, None))]
]

right_column_loss = [
    [sg.Push(), sg.Text("Loss probability configuration"), sg.Push()],
    [sg.VPush()],
    [sg.Text("Total simulation time (minutes):"), sg.Push(), sg.Input(
        key="--SIMULATION-TIME--", default_text="40", size=(10, None))],
    [sg.VPush()],
    [sg.Button("Apply", key="--LOSS-APPLY--")],
]

peak_labels = [
    [sg.Text("Total simulation time (minutes):")],
    [sg.Text("Output time step (seconds):")],
    [sg.Text("Valley size")],
    [sg.Text("Peak size")],
    [sg.Text("Peak duration")],
    [sg.Text("Peak offset")],
]

peak_inputs = [
    [sg.Input(key="--SIMULATION-TIME--", default_text="15", size=(10, None))],
    [sg.Input(key="--OUT-STEP--", default_text="20", size=(10, None))],
    [sg.Input(key="--VALLEY-SIZE--", default_text="20", size=(10, None))],
    [sg.Input(key="--PEAK-SIZE--", default_text="300", size=(10, None))],
    [sg.Input(key="--PEAK-DURATION--", default_text="2", size=(10, None))],
    [sg.Input(key="--PEAK-OFFSET--", default_text="2", size=(10, None))]
]

right_column_peak = [
    [sg.Text("Peak response configuration")],
    [sg.VPush()],
    [sg.Column(peak_labels, element_justification='r'),
     sg.Column(peak_inputs)],
    [sg.Button("Apply", key="--PEAK-APPLY--")]
]

layout = [
    [
        sg.Column(left_column),
        sg.VSeparator(),
        sg.Column(right_column_loss, visible=True, key="--LOSS-COL--"),
        sg.Column(right_column_peak, visible=False,
                  key="--PEAK-COL--", element_justification='c'),
    ],
    [sg.HSeparator(), sg.Input('filename', size=(20, None), key="--SAVE-NAME--",
                               visible=False), sg.Button("Save Plot", key="--SAVE-PLOT--", visible=False)],
    [sg.Canvas(key="--CANVAS--", expand_x=True, expand_y=True)],
]

window = sg.Window("Réseaux Télécoms", layout, finalize=True)
fig_agg = None
plt_fig = None


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side="top", fill="both", expand=1)
    return figure_canvas_agg


while True:
    event, values = window.read()

    print(event)

    if event == "OK" or event == sg.WIN_CLOSED:
        break
    elif event == "--LOSS--" or event == "--PEAK--":
        if values["--LOSS--"] == True:
            window["--LOSS-COL--"].update(visible=True)
            window["--PEAK-COL--"].update(visible=False)
        elif values["--PEAK--"] == True:
            window["--PEAK-COL--"].update(visible=True)
            window["--LOSS-COL--"].update(visible=False)
    elif event == "--SAVE-PLOT--":
        filename = window["--SAVE-NAME--"].get()
        if '.' not in filename:
            filename += '.eps'
        fig.savefig(f'exports/{filename}.eps')
    elif event == "--PEAK-APPLY--":
        if fig_agg is not None:
            fig_agg.get_tk_widget().forget()

        time = int(values["--SIMULATION-TIME--"])
        out_step = int(values["--OUT-STEP--"])
        valley_size = int(values["--VALLEY-SIZE--"])
        peak_size = int(values["--PEAK-SIZE--"])
        peak_dur = int(values["--PEAK-DURATION--"])
        peak_off = int(values["--PEAK-OFFSET--"])

        xs = [valley_size] * (5 + peak_off) + [peak_size] * \
            peak_dur + [valley_size] * time

        def xf(x): return xs[x]

        outs = []
        labels = []

        if values["--STATIC--"]:
            static_main.SIMULATION_MINUTES = time
            outs.append(static_main.measure_loss(xf, out_step))
            labels.append("Statique")
        if values["--BALANCER--"]:
            partage_main.SIMULATION_MINUTES = time
            outs.append(partage_main.measure_loss(xf, out_step))
            labels.append("Partage de Charge")
        if values["--ADAPTIVE--"]:
            adaptatif_main.SIMULATION_MINUTES = time
            outs.append(adaptatif_main.measure_loss(xf, out_step, 0))
            labels.append("Adaptatif")
        if values["--ADAPTIVE-DELAY--"]:
            adaptatif_main.SIMULATION_MINUTES = time
            outs.append(adaptatif_main.measure_loss(xf, out_step, int(values["--DELAY--"])))
            labels.append("Adaptatif avec 30s délai")

        minute = (len(outs[0]) * out_step) // 60

        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        ax.step(list(range(minute + 1)),
                [valley_size] + xs[:minute], label="Appels démarrés par minute")

        for ys, label in zip(outs, labels):
            ax.step([i * out_step / 60 for i in range(len(ys)+1)],
                    [0] + ys, label=label)

        ax.set_xlabel("Minutes")
        ax.grid(True)
        ax.legend(loc="upper right")

        fig_agg = draw_figure(window["--CANVAS--"].TKCanvas, fig)
        plt_fig = fig
        window["--SAVE-PLOT--"].update(visible=True)
        window["--SAVE-NAME--"].update(visible=True)
    elif event == "--LOSS-APPLY--":
        if fig_agg is not None:
            fig_agg.get_tk_widget().forget()

        time = int(values["--SIMULATION-TIME--"])
        out_step = int(values["--OUT-STEP--"])
        valley_size = int(values["--VALLEY-SIZE--"])
        peak_size = int(values["--PEAK-SIZE--"])
        peak_dur = int(values["--PEAK-DURATION--"])
        peak_off = int(values["--PEAK-OFFSET--"])

        xs = [1] + list(range(10, 1000, 10)) + list(range(1020, 2000, 20))

        outs = []
        labels = []

        with multiprocessing.Pool() as ex:
            if values["--STATIC--"]:
                static_main.SIMULATION_MINUTES = time
                outs.append(list(ex.map(partial(static_main.measure_probability), xs)))
                labels.append("Statique")
            if values["--BALANCER--"]:
                partage_main.SIMULATION_MINUTES = time
                outs.append(list(ex.map(partial(partage_main.measure_probability), xs)))
                labels.append("Partage de Charge")
            if values["--ADAPTIVE--"]:
                adaptatif_main.SIMULATION_MINUTES = time
                outs.append(list(ex.map(partial(adaptatif_main.measure_probability, delay=0), xs)))
                labels.append("Adaptatif")
            if values["--ADAPTIVE-DELAY--"]:
                adaptatif_main.SIMULATION_MINUTES = time
                outs.append(list(map(partial(adaptatif_main.measure_probability, delay=int(values["--DELAY--"])), xs)))
                labels.append("Adaptatif avec 30s délai")
            
        fig = plt.figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)

        for ys, label in zip(outs, labels):
            ax.plot(xs, [100*y for y in ys], label=label)
        ax.set_xlabel("Densité d'appels")
        ax.set_ylabel("% d'appels perdus")
        ax.set_xlim((0, max(xs)))
        ax.set_ylim((0, 100))
        ax.grid(True)
        ax.legend()

        fig_agg = draw_figure(window["--CANVAS--"].TKCanvas, fig)
        plt_fig = fig
        window["--SAVE-PLOT--"].update(visible=True)
        window["--SAVE-NAME--"].update(visible=True)        

    elif event == "--ADAPTIVE-DELAY--":
        window["--DELAY--"].update(disabled=not values["--ADAPTIVE-DELAY--"])

window.close()
