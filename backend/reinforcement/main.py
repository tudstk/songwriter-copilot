from .genetic_algorithm import run_evolution, fitness_rating_mode, fitness_automated
from .utils import create_events, save_genome_to_midi
from datetime import datetime
from pyo import *
import time

BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]
DEFAULT_NUM_MUTATIONS = 2
DEFAULT_MUTATION_PROBABILITY = 0.5
DEFAULT_BPM = 120


# used only for console approach
def get_user_input():
    bars = int(input('Number of bars (default 8): ') or 8)
    num_notes = int(input('Notes per bar (default 4): ') or 4)
    num_steps = int(input('Number of steps (default 1): ') or 1)
    pauses = input('Introduce Pauses? (default True) [y/n]: ').lower() in ['y', 'yes', '']
    key = input('Key (default C): ') or 'C'
    scale = input(f'Scale (default major) {SCALES}: ') or 'major'
    root = int(input('Scale Root (default 4): ') or 4)
    population_size = int(input('Population size (default 10): ') or 10)
    fitness_choice = input('Use evaluation by rating or automated? (default: automated) [r/a]: ').lower() or 'a'
    return bars, num_notes, num_steps, pauses, key, scale, root, population_size, fitness_choice


def run_genetic_algorithm(bars, num_notes, num_steps, pauses, key, scale, root, population_size, fitness_choice, rating):
    num_mutations = DEFAULT_NUM_MUTATIONS
    mutation_probability = DEFAULT_MUTATION_PROBABILITY
    bpm = DEFAULT_BPM
    fitness_func = fitness_automated if fitness_choice == 'a' else lambda genome, s, bars, num_notes, num_steps, pauses, key, scale, root, bpm: fitness_rating_mode(genome, s, bars, num_notes, num_steps, pauses, key, scale, root, bpm, rating)

    folder = str(int(datetime.now().timestamp()))
    os.makedirs(folder, exist_ok=True)
    genome_length = bars * num_notes * BITS_PER_NOTE
    s = Server().boot()

    for population_id, population, next_generation, population_fitness in run_evolution(
            population_size, genome_length, fitness_func, num_mutations, mutation_probability, s, bars,
            num_notes, num_steps, pauses, key, scale, root, bpm
    ):
        print(f"Population {population_id} done")

        print("Saving results...")
        for i, genome in enumerate(population):
            save_genome_to_midi(f"{folder}/{population_id}/{scale}-{key}-{i}.mid", genome, bars, num_notes, num_steps,
                                pauses, key, scale, root, bpm)
        print("Done!")

        running = input("Continue? [Y/n]") != "n"
        if not running:
            break



if __name__ == '__main__':
    run_genetic_algorithm()
