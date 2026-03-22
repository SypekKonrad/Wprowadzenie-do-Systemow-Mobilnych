import math
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


def calculate_m_m_s_s_basic(l_o, l_h, mu, S):

    l_total = l_o + l_h
    denominator = sum([(l_total ** i) / (math.factorial(i) * (mu ** i)) for i in range(int(S) + 1)])
    p0 = 1 / denominator
    return ((l_total ** S) / (math.factorial(S) * (mu ** S))) * p0

def calculate_m_m_s_s_reservation(l_o, l_h, mu, S, Sc):
    S, Sc = int(S), int(Sc)
    term1 = sum([(l_o + l_h) ** i / (math.factorial(i) * mu ** i) for i in range(Sc + 1)])
    term2 = sum([((l_o + l_h) ** Sc * l_h ** (i - Sc)) / (math.factorial(i) * mu ** i) for i in range(Sc + 1, S + 1)])

    p0 = 1 / (term1 + term2)

    probs = []
    for i in range(S + 1):
        if i <= Sc:
            p_i = ((l_o + l_h) ** i / (math.factorial(i) * mu ** i)) * p0
        else:
            p_i = ((l_o + l_h) ** Sc * l_h ** (i - Sc) / (math.factorial(i) * mu ** i)) * p0
        probs.append(p_i)

    return sum(probs[Sc:]), probs[S]

class BaseStationSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Symulator Stacji Bazowej - Systemy Mobilne")
        self.root.geometry("1300x850")
        self.root.configure(bg="#f0f0f0")

        self.setup_ui()
        self.reset_sim_state()

    def setup_ui(self):
        param_frame = tk.LabelFrame(self.root, text="Parametry", bg="#f0f0f0", padx=10, pady=10)
        param_frame.place(x=10, y=10, width=280, height=330)

        self.vars = {
            'S': tk.IntVar(value=10),
            'Queue': tk.IntVar(value=10),
            'Lambda': tk.DoubleVar(value=1.0),
            'N': tk.DoubleVar(value=20),
            'Sigma': tk.DoubleVar(value=5),
            'Min': tk.DoubleVar(value=10),
            'Max': tk.DoubleVar(value=30),
            'SimTime': tk.IntVar(value=30),
            'Sc': tk.IntVar(value=8)
        }

        labels = ["Liczba kanałów (S)", "Długość kolejki", "Lambda", "Średnia (N)",
                  "Sigma", "Min długość", "Max długość", "Czas symulacji"]
        keys = ['S', 'Queue', 'Lambda', 'N', 'Sigma', 'Min', 'Max', 'SimTime']

        for i, (label, key) in enumerate(zip(labels, keys)):
            tk.Label(param_frame, text=label, bg="#f0f0f0").grid(row=i, column=0, sticky="w")
            tk.Entry(param_frame, textvariable=self.vars[key], width=8).grid(row=i, column=1, sticky="e", pady=2)

        stats_frame = tk.LabelFrame(self.root, text="Wyniki", bg="#f0f0f0", padx=10, pady=10)
        stats_frame.place(x=300, y=10, width=150, height=330)

        self.lbl_poisson_x = tk.Label(stats_frame, text="Poisson X: -", bg="#f0f0f0")
        self.lbl_poisson_x.pack(anchor="w")
        self.lbl_gauss_x = tk.Label(stats_frame, text="Gauss X: -", bg="#f0f0f0")
        self.lbl_gauss_x.pack(anchor="w", pady=(10, 0))

        self.viz_container = tk.LabelFrame(self.root, text=" Stan Kanałów ", bg="#f0f0f0")
        self.viz_container.place(x=470, y=10, width=220, height=330)

        self.viz_frame = tk.Frame(self.viz_container, bg="#f0f0f0")
        self.viz_frame.pack(expand=True, fill="both", padx=5, pady=5)

        self.channel_rects = []
        self.channel_labels = []

        list_frame = tk.LabelFrame(self.root, text="Wyniki szczegółowe", bg="#f0f0f0")
        list_frame.place(x=10, y=350, width=440, height=380)

        columns = ("L_Pois", "L_Gaus", "Klient", "C_Przyj", "C_Obsl", "Roi")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=65)
        self.tree.pack(fill="both", expand=True)

        self.lbl_sim_status = tk.Label(self.root, text="Czas symulacji: 0 / 0", font=("Arial", 11, "bold"),
                                       bg="#f0f0f0")
        self.lbl_sim_status.place(x=480, y=750)
        self.btn_start = tk.Button(self.root, text="START", font=("Arial", 12, "bold"), bg="white",
                                   command=self.start_simulation)
        self.btn_start.place(x=60, y=740, width=120, height=50)

        self.lbl_handled = tk.Label(self.root, text="Obsłużone: 0", bg="#f0f0f0")
        self.lbl_handled.place(x=480, y=650)
        self.lbl_rejected = tk.Label(self.root, text="Odrzucone: 0", bg="#f0f0f0")
        self.lbl_rejected.place(x=480, y=710)

        self.setup_plots()

    def setup_plots(self):
        self.plot_container = tk.Frame(self.root, bg="white")
        self.plot_container.place(x=700, y=10, width=580, height=780)

        self.fig, (self.ax_q, self.ax_w, self.ax_ro) = plt.subplots(3, 1, figsize=(5, 8))
        self.fig.patch.set_facecolor('#f0f0f0')

        self.lines = {
            'Q': self.ax_q.plot([], [], 'r-', label='Długość kolejki (Q)')[0],
            'W': self.ax_w.plot([], [], 'b-', label='Czas oczekiwania (W)')[0],
            'Ro': self.ax_ro.plot([], [], 'g-', label='Obciążenie (Ro)')[0]
        }

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def reset_sim_state(self):
        self.sim_time = 0
        self.handled_count = 0
        self.rejected_count = 0
        self.history = {'t': [], 'Q': [], 'W': [], 'Ro': []}
        self.queue = []
        for item in self.tree.get_children(): self.tree.delete(item)

    def start_simulation(self):
        self.reset_sim_state()
        self.arr_ptr = 0
        self.btn_start.config(state="disabled")

        S = self.vars['S'].get()
        for child in self.viz_frame.winfo_children(): child.destroy()
        self.channel_rects, self.channel_labels = [], []

        cols = math.ceil(math.sqrt(S))
        rows = math.ceil(S / cols)

        for i in range(cols): self.viz_frame.grid_columnconfigure(i, weight=1)
        for i in range(rows): self.viz_frame.grid_rowconfigure(i, weight=1)

        for i in range(S):
            r = tk.Frame(self.viz_frame, bg="green", highlightbackground="white", highlightthickness=1)
            r.grid(row=i // cols, column=i % cols, sticky="nsew", padx=1, pady=1)
            l = tk.Label(r, text=f"{i + 1}\nWolny", bg="green", fg="white", font=("Arial", 7, "bold"))
            l.pack(expand=True, fill="both")
            self.channel_rects.append(r)
            self.channel_labels.append(l)

        L = self.vars['Lambda'].get()
        T_max = self.vars['SimTime'].get()
        self.arrivals = []
        curr = 0
        while curr < T_max:
            inter = np.random.exponential(1.0 / L)
            curr += inter
            dur = np.clip(np.random.normal(self.vars['N'].get(), self.vars['Sigma'].get()),
                          self.vars['Min'].get(), self.vars['Max'].get())
            self.arrivals.append({'time': curr, 'dur': dur})

        self.active_channels = [0.0] * S
        self.run_step()

    def run_step(self):
        max_time = self.vars['SimTime'].get()

        if self.sim_time > max_time:
            self.btn_start.config(state="normal")
            self.save_to_file()  # Zapis danych po zakończeniu
            self.lbl_sim_status.config(text=f"Czas: {max_time}/{max_time} - Koniec")
            return

        self.lbl_sim_status.config(text=f"Czas symulacji: {self.sim_time} / {max_time}")

        current_calls = [a for a in self.arrivals if self.sim_time <= a['time'] < self.sim_time + 1]

        if self.arr_ptr < len(self.arrivals):
            current_event = self.arrivals[self.arr_ptr]
            self.lbl_poisson_x.config(text=f"Poisson X: {current_event['time']:.2f}s")
            self.lbl_gauss_x.config(text=f"Gauss X: {current_event['dur']:.2f}s")

        for i in range(len(self.active_channels)):
            if self.active_channels[i] > 0:
                self.active_channels[i] = max(0, self.active_channels[i] - 1)

            if self.active_channels[i] <= 0:
                self.channel_rects[i].config(bg="green")
                self.channel_labels[i].config(text=f"{i + 1}\nWolny", bg="green")
            else:
                self.channel_rects[i].config(bg="red")
                self.channel_labels[i].config(text=f"{i + 1}\n{int(self.active_channels[i])}s", bg="red")

        for call in current_calls:
            placed = False
            for i in range(len(self.active_channels)):
                if self.active_channels[i] <= 0:
                    self.active_channels[i] = call['dur']
                    self.handled_count += 1
                    placed = True
                    self.tree.insert("", "end", values=(
                        f"{1 / self.vars['Lambda'].get():.2f}", f"{call['dur']:.2f}",
                        self.handled_count, f"{call['time']:.1f}", f"{call['dur']:.1f}",
                        f"{self.handled_count / self.vars['S'].get():.2f}"
                    ))
                    break

            if not placed:
                if len(self.queue) < self.vars['Queue'].get():
                    self.queue.append(call['dur'])
                else:
                    self.rejected_count += 1
            self.arr_ptr += 1

        for i in range(len(self.active_channels)):
            if self.active_channels[i] <= 0 and self.queue:
                self.active_channels[i] = self.queue.pop(0)
                self.handled_count += 1

        busy = sum(1 for c in self.active_channels if c > 0)
        rho = busy / self.vars['S'].get()
        self.history['t'].append(self.sim_time)
        self.history['Ro'].append(rho)
        self.history['Q'].append(len(self.queue))
        self.history['W'].append(len(self.queue) / self.vars['Lambda'].get())

        self.update_live_plots()
        self.lbl_handled.config(text=f"Obsłużone: {self.handled_count}")
        self.lbl_rejected.config(text=f"Odrzucone: {self.rejected_count}")

        self.sim_time += 1
        self.root.after(100, self.run_step)

    def update_live_plots(self):
        self.lines['Ro'].set_data(self.history['t'], self.history['Ro'])
        self.lines['Q'].set_data(self.history['t'], self.history['Q'])
        self.lines['W'].set_data(self.history['t'], self.history['W'])
        for ax in [self.ax_q, self.ax_w, self.ax_ro]:
            ax.relim()
            ax.autoscale_view()
        self.canvas.draw_idle()

    def save_to_file(self):
        pd.DataFrame(self.history).to_csv("wyniki_symulacji.txt", sep='\t', index=False, float_format="%.4f")
        messagebox.showinfo("Koniec", "Symulacja zakończona. Dane zapisano do wyniki_symulacji.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = BaseStationSimulator(root)
    root.mainloop()