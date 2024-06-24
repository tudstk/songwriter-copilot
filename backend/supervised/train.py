import glob
import pickle
import numpy as np
from music21 import converter, instrument, note, chord
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, BatchNormalization as BatchNorm
from keras.utils import np_utils
from keras.callbacks import ModelCheckpoint


def extract_notes_from_midi(file_path):
    midi = converter.parse(file_path)
    parts = None

    try:
        parts = instrument.partitionByInstrument(midi).parts[0].recurse()
    except:
        parts = midi.flat.notes

    notes = []
    for element in parts:
        if isinstance(element, note.Note):
            notes.append(str(element.pitch))
        elif isinstance(element, chord.Chord):
            notes.append('.'.join(str(n) for n in element.normalOrder))

    return notes


def save_notes(notes, file_path):
    with open(file_path, 'wb') as filepath:
        pickle.dump(notes, filepath)


def get_notes():
    notes = []
    for file in glob.glob("classical/*.mid"):
        notes.extend(extract_notes_from_midi(file))
    save_notes(notes, './classical_model/notes')
    return notes


def prepare_sequences(notes, sequence_length=100):
    unique_notes = sorted(set(notes))
    note_to_int = {note: number for number, note in enumerate(unique_notes)}
    num_unique_notes = len(unique_notes)

    input_sequences = []
    output_notes = []

    for i in range(len(notes) - sequence_length):
        input_seq = notes[i:i + sequence_length]
        output_note = notes[i + sequence_length]
        input_sequences.append([note_to_int[note] for note in input_seq])
        output_notes.append(note_to_int[output_note])

    num_patterns = len(input_sequences)
    normalized_inputs = (np.reshape(input_sequences,
                                    (num_patterns, sequence_length, 1)) / float(num_unique_notes))
    categorical_outputs = np_utils.to_categorical(output_notes)

    return normalized_inputs, categorical_outputs, num_unique_notes


def create_model(input_shape, num_unique_notes, weights_file=None):
    model = Sequential([
        LSTM(512, input_shape=input_shape, recurrent_dropout=0.3, return_sequences=True),
        LSTM(512, return_sequences=True, recurrent_dropout=0.3),
        LSTM(512),
        BatchNorm(),
        Dropout(0.3),
        Dense(256, activation='relu'),
        BatchNorm(),
        Dropout(0.3),
        Dense(num_unique_notes, activation='softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')

    if weights_file:
        model.load_weights(weights_file)

    return model


def train_model(model, inputs, outputs, epochs=200, batch_size=128):
    checkpoint = ModelCheckpoint(
        "classical/weights-improvement-{epoch:02d}.hdf5",
        monitor='loss',
        save_best_only=True,
        mode='min'
    )
    model.fit(inputs, outputs, epochs=epochs, batch_size=batch_size, callbacks=[checkpoint])


def train_network():
    notes = get_notes()
    inputs, outputs, num_unique_notes = prepare_sequences(notes)
    model = create_model((inputs.shape[1], inputs.shape[2]), num_unique_notes)
    train_model(model, inputs, outputs)


train_network()
