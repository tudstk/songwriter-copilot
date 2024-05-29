import click
from datetime import datetime
from typing import List, Dict
from midiutil import MIDIFile
from pyo import *

from algorithms.genetic import generate_genome, Genome, selection_pair, single_point_crossover, mutation

BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]


def int_from_bits(bits: List[int]) -> int:
    return int(sum([bit * pow(2, index) for index, bit in enumerate(bits)]))


def genome_to_melody(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: int, key: str, scale: str, root: int) -> Dict[str, list]:
    notes = [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE] for i in range(num_bars * num_notes)]

    note_length = 4 / float(num_notes)

    scl = EventScale(root=key, scale=scale, first=root)

    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    for note in notes:
        integer = int_from_bits(note)

        if not pauses:
            integer = int(integer % pow(2, BITS_PER_NOTE - 1))

        if integer >= pow(2, BITS_PER_NOTE - 1):
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]

    steps = []
    for step in range(num_steps):
        steps.append([scl[(note + step * 2) % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps
    return melody


def genome_to_events(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int, bpm: int) -> [Events]:
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            attack=0.001,
            decay=0.05,
            sustain=0.5,
            release=0.005,
            bpm=bpm
        ) for step in melody["notes"]
    ]


def fitness(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
            pauses: bool, key: str, scale: str, root: int, bpm: int, s: Server) -> int:
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    all_notes = [note for step in melody["notes"] for note in step]

    pitch_range = max(all_notes) - min(all_notes)

    contour_changes = sum(1 for i in range(1, len(all_notes)) if all_notes[i] != all_notes[i - 1])

    note_repetition_penalty = sum(
        1 for i in range(1, len(all_notes)) if all_notes[i] == all_notes[i - 1])

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


def metronome(bpm: int):
    met = Metro(time=1 / (bpm / 60.0)).play()
    t = CosTable([(0, 0), (50, 1), (200, .3), (500, 0)])
    amp = TrigEnv(met, table=t, dur=.25, mul=1)
    freq = Iter(met, choice=[660, 440, 440, 440])
    return Sine(freq=freq, mul=amp).mix(2).out()


def save_genome_to_midi(filename: str, genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                        pauses: bool, key: str, scale: str, root: int, bpm: int):
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track = 0
    channel = 0

    time = 0.0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

        time += melody["beat"][i]

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)


# MELODY_CONFIG = {
#     "num_bars": 4,
#     "num_notes": 12,
#     "num_steps": 2,
#     "root": 4,
#     "pauses": True
# }


MELODY_CONFIG = {
    "num_bars": 4,
    "num_notes": 8,
    "num_steps": 2,
    "root": 5,
    "pauses": True
}

HARMONY_CONFIG = {
    "num_bars": 4,
    "num_notes": 1,
    "num_steps": 3,
    "root": 4,
    "pauses": False
}


def get_configuration(choice: str):
    if choice == 'melody':
        return MELODY_CONFIG
    elif choice == 'harmony':
        return HARMONY_CONFIG
    else:
        raise ValueError("Invalid choice")


@click.command()
@click.option("--scale", prompt='Choose a scale:', type=click.Choice(SCALES, case_sensitive=False))
@click.option("--key", prompt='Choose a key:', type=click.Choice(KEYS, case_sensitive=False))
@click.option("--type", prompt='Choose between melody and harmony:', type=click.Choice(['melody', 'harmony']))
@click.option("--num-mutations", default=2, type=int)
@click.option("--bpm", default=140, type=int)
def main(scale: str, key: str, type: str, num_mutations: int, bpm: int):
    configuration = get_configuration(type)

    num_bars = configuration["num_bars"]
    num_notes = configuration["num_notes"]
    num_steps = configuration["num_steps"]
    root = configuration["root"]
    pauses = configuration["pauses"]

    population_size = 8
    mutation_probability = 0.5
    folder = str(int(datetime.now().timestamp()))

    population = [generate_genome(num_bars * num_notes * BITS_PER_NOTE) for _ in range(population_size)]

    s = Server().boot()

    population_id = 0

    running = True
    pop_number = 3
    k = 0
    while k < pop_number:
        random.shuffle(population)

        population_fitness = [
            (genome, fitness(genome, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm, s)) for genome in
            population
        ]

        sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)

        population = [e[0] for e in sorted_population_fitness]

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):

            def fitness_lookup(genome):
                for e in population_fitness:
                    if e[0] == genome:
                        return e[1]
                return 0

            parents = selection_pair(population, fitness_lookup)
            offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
            offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
            offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
            next_generation += [offspring_a, offspring_b]

        print(f"population {population_id} done")

        events = genome_to_events(population[0], num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
        if k == pop_number - 1:
            for e in events:
                e.play()
            s.start()
            input("here is the no1 hit …")
            s.stop()
            for e in events:
                e.stop()

        time.sleep(1)

        events = genome_to_events(population[1], num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
        if k == pop_number - 1:
            for e in events:
                e.play()
            s.start()
            input("here is the second best …")
            s.stop()
            for e in events:
                e.stop()

        time.sleep(1)

        if k == pop_number - 1:
            print("saving population midi …")
            for i, genome in enumerate(population[0:2]):
                save_genome_to_midi(f"{folder}/{population_id}/{type}-{key}-{i}.mid", genome, num_bars, num_notes,
                                    num_steps, pauses, key, scale, root, bpm)
            print("done")

        # running = input("continue? [Y/n]") != "n"
        population = next_generation
        population_id += 1

        k = k + 1


if __name__ == '__main__':
    main()
