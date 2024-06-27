from midiutil import MIDIFile
from pyo import *
import os

BITS_PER_NOTE = 4


def int_from_bits(bits):
    return int(sum([bit * pow(2, index) for index, bit in enumerate(bits)]))


def create_melody(genome, bars, num_notes, num_steps, pauses, key, scale, root):
    notes = [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE] for i in range(bars * num_notes)]
    note_length = 4 / float(num_notes)
    scl = EventScale(root=key, scale=scale, first=root)
    max_int = pow(2, BITS_PER_NOTE - 1)

    melody = {"notes": [], "velocity": [], "beat": []}

    for i, note in enumerate(notes):
        integer = int_from_bits(note)
        if not pauses:
            integer %= max_int

        if integer >= max_int:
            note_value, velocity, beat = 0, 0, note_length
        else:
            note_value, velocity, beat = integer, 127, note_length
            if melody["notes"] and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
                continue

        melody["notes"].append(note_value)
        melody["velocity"].append(velocity)
        melody["beat"].append(beat)

    steps = [[scl[(note + step * 2) % len(scl)] for note in melody["notes"]] for step in range(num_steps)]
    melody["notes"] = steps

    return melody


def save_genome_to_midi(filename, genome, bars, num_notes, num_steps, pauses, key, scale, root, bpm):
    melody = create_melody(genome, bars, num_notes, num_steps, pauses, key, scale, root)

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
