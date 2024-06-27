from random import choices, randint, randrange, sample
import random as rand
from reinforcement.utils import create_melody, save_genome_to_midi


KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]


def initialize_population(size, genome_length):
    return [generate_genome(genome_length) for _ in range(size)]


def generate_genome(length):
    return choices([0, 1], k=length)


def single_point_crossover(a, b):
    if len(a) != len(b):
        raise ValueError("Genomes a and b must be of same length")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]


def mutation(genome, num=1, probability=0.5):
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if rand.random() > probability else abs(genome[index] - 1)
    return genome


def selection_pair(population, fitness_func):
    return sample(
        population=generate_weighted_distribution(population, fitness_func),
        k=2
    )


def generate_weighted_distribution(population, fitness_func):
    result = []
    for gene in population:
        # Convert gene (list) to a tuple to make it hashable
        fitness_score = fitness_func(tuple(gene))
        result += [gene] * int(fitness_score + 1)
    return result


def generate_next_generation(population, population_fitness, num_mutations, mutation_probability):
    next_generation = population[:2]
    fitness_dict = {tuple(g): fitness for g, fitness in population_fitness}
    for _ in range((len(population) // 2) - 1):
        parents = selection_pair(population, fitness_dict.get)
        offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
        offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
        offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
        next_generation.extend([offspring_a, offspring_b])
    return next_generation


def evaluate_population(population, fitness_func, *args):
    population_fitness = [(genome, fitness_func(genome, *args)) for genome in population]
    sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)
    return [e[0] for e in sorted_population_fitness], population_fitness


def run_evolution(population_size, genome_length, fitness_func, num_mutations, mutation_probability, *fitness_args):
    population = initialize_population(population_size, genome_length)
    population_id = 0
    running = True

    while running:
        rand.shuffle(population)
        population, population_fitness = evaluate_population(population, fitness_func, *fitness_args)
        next_generation = generate_next_generation(population, population_fitness, num_mutations, mutation_probability)
        yield population_id, population, next_generation, population_fitness
        population = next_generation
        population_id += 1


def fitness_automated(genome, bars, num_notes, num_steps, pauses, key, scale, root):
    melody = create_melody(genome, bars, num_notes, num_steps, pauses, key, scale, root)
    all_notes = [note for step in melody["notes"] for note in step]
    pitch_range = max(all_notes) - min(all_notes)
    contour_changes = sum(1 for i in range(1, len(all_notes)) if all_notes[i] != all_notes[i - 1])
    note_repetition_penalty = sum(1 for i in range(1, len(all_notes)) if all_notes[i] == all_notes[i - 1])
    scale_degrees = [note % len(SCALES) for note in all_notes]
    scale_conformance = sum(1 for degree in scale_degrees if degree not in range(len(SCALES)))
    unique_durations = set(melody["beat"])
    rhythmic_variety = len(unique_durations)
    diversity_score = 0
    contour_types = set()
    for i in range(1, len(all_notes)):
        contour_types.add((all_notes[i] - all_notes[i - 1]) // 2)
    diversity_score += len(contour_types)
    harmony_intervals = set()
    for i in range(1, len(all_notes)):
        harmony_intervals.add(abs(all_notes[i] - all_notes[i - 1]) % len(SCALES))
    diversity_score += len(harmony_intervals)
    unique_pitches = set(all_notes)
    diversity_score += len(unique_pitches)
    rhythmic_patterns = set(tuple(zip(map(tuple, melody["notes"]), melody["beat"])))
    diversity_score += len(rhythmic_patterns)
    fitness_score = pitch_range + contour_changes - note_repetition_penalty - scale_conformance + rhythmic_variety - diversity_score
    print(fitness_score)
    return fitness_score
