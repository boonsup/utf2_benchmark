"""
UTF-2.0 Chaos Kernel Visualizer
Plots parameter drift and convergence from the f_tuning_history.csv file.
"""

import pandas as pd, matplotlib.pyplot as plt, os

def plot_history(csv_path="data/f_tuning_history.csv"):
    if not os.path.exists(csv_path):
        print("⚠️ No tuning history found.")
        return
 #   df = pd.read_csv(csv_path)
    df = pd.read_csv(csv_path, on_bad_lines='skip', engine='python')

    if df.empty:
        print("⚠️ Empty tuning file — no data to visualize.")
        return

    plt.figure(figsize=(9, 5))
    plt.subplot(3, 1, 1)
    plt.plot(df["r_best"], "o-", color="dodgerblue")
    plt.ylabel("r")
    plt.subplot(3, 1, 2)
    plt.plot(df["tolerance_best"], "s-", color="orange")
    plt.ylabel("tolerance")
    plt.subplot(3, 1, 3)
    plt.plot(df["adapt_best"], "^-", color="green")
    plt.ylabel("adapt")
    plt.xlabel("Iteration")
    plt.suptitle("F̂ Chaos Kernel — Hyperparameter Evolution")
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()
