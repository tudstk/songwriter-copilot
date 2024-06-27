from genetic_algorithm import run_evolution, fitness_automated
from utils import  save_genome_to_midi
from datetime import datetime
from pyo import *
import time


BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]
DEFAULT_NUM_MUTATIONS = 2
DEFAULT_MUTATION_PROBABILITY = 0.5
DEFAULT_BPM = 160


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

