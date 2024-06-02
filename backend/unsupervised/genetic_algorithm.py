from random import choices, randint, randrange, random, sample
from utils import create_melody, create_events
import random
import time

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
        genome[index] = genome[index] if random() > probability else abs(genome[index] - 1)
    return genome


def selection_pair(population, fitness_func):
    return sample(
        population=generate_weighted_distribution(population, fitness_func),
        k=2
    )


def generate_weighted_distribution(population, fitness_func):
    result = []

    for gene in population:
        result += [gene] * int(fitness_func(gene) + 1)

    return result


def evaluate_population(population, fitness_func, *args):
    population_fitness = [(genome, fitness_func(genome, *args)) for genome in population]
    sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)
    return [e[0] for e in sorted_population_fitness], population_fitness


def generate_next_generation(population, population_fitness, num_mutations, mutation_probability):
    next_generation = population[:2]
    for _ in range((len(population) // 2) - 1):
        parents = selection_pair(population, dict(population_fitness).get)
        offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
        offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
        offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
        next_generation.extend([offspring_a, offspring_b])
    return next_generation


def run_evolution(population_size, genome_length, fitness_func, num_mutations, mutation_probability, *fitness_args):
    population = initialize_population(population_size, genome_length)
    population_id = 0
    running = True

    while running:
        random.shuffle(population)
        population, population_fitness = evaluate_population(population, fitness_func, *fitness_args)
        next_generation = generate_next_generation(population, population_fitness, num_mutations, mutation_probability)
        yield population_id, population, next_generation, population_fitness
        population = next_generation
        population_id += 1


def fitness_rating_mode(genome, s, bars, num_notes, num_steps, pauses, key, scale, root, bpm):
    events = create_events(genome, bars, num_notes, num_steps, pauses, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()
    rating = input("Rating (0-5)")
    for e in events:
        e.stop()
    s.stop()
    time.sleep(1)

    try:
        rating = int(rating)
    except ValueError:
        rating = 0

    return rating


def fitness_automated(genome, s, bars, num_notes, num_steps, pauses, key, scale, root, bpm):
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
