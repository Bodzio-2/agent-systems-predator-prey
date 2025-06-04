import json
import numpy as np
import matplotlib.pyplot as plt

# Load population history
def load_population_history(json_path="population_history.json"):
    with open(json_path) as f:
        history = json.load(f)
    return history

def moving_average(data, window_size=15):
    return np.convolve(data, np.ones(window_size)/window_size, mode='same')

def plot_smoothed_population(history, window=15):
    keys = list(history[0].keys())
    populations = {k: np.array([h[k] for h in history]) for k in keys}
    time_steps = np.arange(len(history))
    
    plt.figure(figsize=(10, 6))
    plt.plot(moving_average(populations['plant'], window), color='green', label='Plants')
    plt.plot(moving_average(populations['stage2'], window), color='orange', label='Stage2 (Herbivores)')
    plt.plot(moving_average(populations['stage3'], window), color='blue', label='Stage3 (Omnivores)')
    plt.plot(moving_average(populations['stage4'], window), color='red', label='Stage4 (Carnivores)')
    plt.plot(moving_average(populations['stage5'], window), color='purple', label='Stage5 (Apex Predators)')

    plt.xlabel("Time Step")
    plt.ylabel("Population")
    plt.title(f"Population of Each Organism Type Over Time (window={window})")
    plt.legend()
    plt.tight_layout()
    plt.savefig("smoothed_population.png")
    plt.show()

if __name__ == "__main__":
    history = load_population_history()
    plot_smoothed_population(history, window=25)  # Increase window for more smoothing
