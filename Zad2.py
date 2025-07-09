import sys, time, random, statistics, subprocess
import tkinter as tk
from tkinter import messagebox

# do wykresów
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

if sys.platform.startswith("win"):
    import winsound

class ReactionTester:
    def __init__(self, master):
        self.master = master
        master.title("Tester psychomotoryczny")
        self.frame = tk.Frame(master)
        self.frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.btn_start = tk.Button(
            self.frame, text="Rozpocznij test", font=("Arial",16),
            command=self.start
        )
        self.btn_start.pack(expand=True)

    def start(self):
        self.btn_start.pack_forget()
        self.run_test("optyczny", self.visual_trial)
        self.run_test("akustyczny", self.audio_trial)
        messagebox.showinfo("Koniec", "Dziękujemy za udział!")

    def run_test(self, mode, trial_func):
        trials = 5
        texts = {
            "optyczny":
                "Test PROSTEJ REAKCJI OPTYCZNEJ\n\n"
                "Gdy zmieni się kolor tła na zielony,\n"
                "jak najszybciej kliknij „Reaguję”.",
            "akustyczny":
                "Test PROSTEJ REAKCJI AKUSTYCZNEJ\n\n"
                "Gdy usłyszysz beep,\n"
                "kliknij „Reaguję”."
        }
        messagebox.showinfo(f"Instrukcja – {mode}", texts[mode])

        messagebox.showinfo("Trening", "3 próby treningowe (bez zapisu).")
        for _ in range(3):
            trial_func(record=False)
            time.sleep(0.5)

        messagebox.showinfo("Test", f"Faza właściwa: {trials} prób.")
        results = []
        for _ in range(trials):
            rt = trial_func(record=True)
            if rt is not None:
                results.append(rt)
            time.sleep(0.5)

        self.show_results(mode, results)

    def visual_trial(self, record=True):
        rt = {'value':None}
        start = [0.0]

        w = tk.Toplevel(self.master)
        w.title("Test optyczny")
        w.geometry("400x300")
        w.configure(bg="red")

        btn = tk.Button(
            w, text="Reaguję", state="disabled", font=("Arial",14),
            relief="raised", borderwidth=4, activebackground="grey"
        )
        btn.pack(expand=True, fill="both", padx=20, pady=20)

        def click():
            end = time.perf_counter()
            rt['value'] = end - start[0]
            w.destroy()

        btn.config(command=click)

        def go_green():
            w.configure(bg="green")
            btn.config(state="normal")
            start[0] = time.perf_counter()

        w.after(int(random.uniform(1,2.5)*1000), go_green)
        w.grab_set()
        self.master.wait_window(w)
        return rt['value']

    def audio_trial(self, record=True):
        rt = {'value':None}
        start = [0.0]

        w = tk.Toplevel(self.master)
        w.title("Test akustyczny")
        w.geometry("300x150")

        btn = tk.Button(
            w, text="Reaguję", state="disabled", font=("Arial",14),
            relief="raised", borderwidth=4, activebackground="grey"
        )
        btn.pack(expand=True, fill="both", padx=20, pady=20)

        def click():
            end = time.perf_counter()
            rt['value'] = end - start[0]
            w.destroy()

        btn.config(command=click)

        def play_and_activate():
            if sys.platform.startswith("win"):
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)

                # dzwiek
            elif sys.platform.startswith("darwin"):
                subprocess.Popen([
                    "afplay", "/System/Library/Sounds/Ping.aiff"
                ])
            # Linux / inne – ASCII bell
            else:
                print("\a", end="", flush=True)

            btn.config(state="normal", bg="lightgreen")
            start[0] = time.perf_counter()

        w.after(int(random.uniform(1,2.5)*1000), play_and_activate)
        w.grab_set()
        self.master.wait_window(w)
        return rt['value']

    def show_results(self, mode, data):
        if not data:
            messagebox.showwarning("Brak danych", "Brak pomiarów.")
            return

        ms = [d*1000 for d in data]
        avg, mn, mx = statistics.mean(ms), min(ms), max(ms)
        sd = statistics.pstdev(ms)

        txt = (
            f"Wyniki testu {mode}:\n"
            f"Próby: {len(ms)}\n"
            f"Średni: {avg:.1f} ms\n"
            f"Min: {mn:.1f} ms, Max: {mx:.1f} ms\n"
            f"Std dev: {sd:.1f} ms"
        )
        messagebox.showinfo(f"Wyniki – {mode}", txt)

        fig = Figure(figsize=(8,5), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(range(1,len(ms)+1), ms, color="skyblue")
        ax.set_xlabel("Numer próby")
        ax.set_ylabel("Czas reakcji [ms]")
        ax.set_title(f"Czasy reakcji ({mode})")
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.frame)
        canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)
        canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    ReactionTester(root)
    root.mainloop()