import pandas as pd
import numpy as np  
import matplotlib.pyplot as plt

import os
dir_path = "results"
list_of_files = os.listdir(dir_path)
list_of_files = [f for f in list_of_files if f.endswith(".csv")]
names={
    "pool": "pool",
    "1": "Conservative",
    "2": "Aggressive",
    "3": "Random",
    "4": "Martingale",
    "5": "Probability",
    "6": "AllIn",
    "7": "Manuel",
    "8": "Manuel_wilches",
    "9": "BadBunny",
    "10": "Wilches",
    "11": "Beltrox",
    "12": "Snowball",
}

def plot_all_games(column, n_games, max_rounds=5000, verbose=False, ax=None, zeros=False):
    if n_games is None:
        n_games=len(list_of_files)
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlabel("Round")
        ax.set_ylabel(column)
        ax.set_title(f"{names[column]} evolution")
    else:
        fig = None
    

    acumulative_round = np.zeros(max_rounds)
    counts = np.zeros(max_rounds)
    

    for file in list_of_files[:n_games]:
        df = pd.read_csv(os.path.join(dir_path, file))
        if verbose:
            ax.plot(df[column], alpha=0.3, label=file if n_games<=5 else None)
        values = df[column].to_numpy()[:max_rounds]
        acumulative_round[:len(values)] += values
        counts[:len(values)] += 1
    if zeros:
        mean_round_zeros=acumulative_round/n_games
        ax.plot(mean_round_zeros, label=names[column]+"_zeros", linestyle="--")
    else:
        mean_round = acumulative_round / counts
        ax.plot(mean_round, label=names[column])
    
    if verbose:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        print("total plata inicial",df.iloc[1].sum())

def plot_all_games_normalized(column, n_games, max_rounds=5000, verbose=False, 
                   ax=None, zeros=False, normalized=False, n_bins=100):
    if n_games is None:
        n_games = len(list_of_files)

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlabel("Round" if not normalized else "Game progress (%)")
        ax.set_ylabel(column)
        ax.set_title(f"{names[column]} evolution")
    else:
        fig = None
    # Each game is stretched to [0, n_bins] bins
    accumulative_norm = np.zeros(n_bins)
    counts_norm = np.zeros(n_bins)

    for file in list_of_files[:n_games]:
        df = pd.read_csv(os.path.join(dir_path, file))
        values = df[column].to_numpy()[:max_rounds]
        n = len(values)
        if n == 0:
            continue

        # Map each value to a normalized bin
        original_positions = np.linspace(0, 1, n)
        bin_positions = np.linspace(0, 1, n_bins)
        interpolated = np.interp(bin_positions, original_positions, values)

        if verbose:
            ax.plot(np.linspace(0, 100, n_bins), interpolated,
                    alpha=0.3, label=file if n_games <= 5 else None)

        accumulative_norm += interpolated
        counts_norm += 1

    mean_normalized = accumulative_norm / counts_norm
    ax.plot(np.linspace(0, 100, n_bins), mean_normalized,
            label=names[column] + "_norm")
    ax.set_xlim(0, 100)
    if verbose:
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
        print("total plata inicial", df.iloc[1].sum())

def main():
    df=pd.read_csv(dir_path+'/'+list_of_files[0])
    players_list=df.keys()
    print("numero de juegos", len(list_of_files))
    print("Lista de jugadores", players_list)
    #----------------------------------------------

    plot_all_games("7", n_games=1000, max_rounds=4000, verbose=True)
    #----------------------------------------------
    fig , ax = plt.subplots(figsize=(10, 8))
    for player in players_list:
        plot_all_games(player, n_games=None, max_rounds=1000, ax=ax, zeros=True)
    ax.legend()
    ax.set_xlabel("Round")
    ax.set_ylabel("stack")
    ax.set_yscale("log")
    ax.set_title("strategy evolution [log]")
    plt.show()
    #----------------------------------------------
    fig , ax = plt.subplots(figsize=(10, 8))
    for player in players_list:
        plot_all_games(player, n_games=None, max_rounds=6000, ax=ax, zeros=False)
    ax.legend()
    ax.set_xlabel("Round")
    ax.set_ylabel("stack")
    ax.set_title("strategy evolution")
    plt.show()
    #----------------------------------------------
    fig , ax = plt.subplots(figsize=(10, 8))
    for player in players_list:
        plot_all_games_normalized(player, n_games=None, max_rounds=6000, ax=ax, normalized=True, n_bins=500)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)
    ax.set_xlabel("Round progress")
    ax.set_ylabel("stack average")
    ax.set_title("strategy evolution")
    plt.show()

if __name__ == "__main__":
    main()