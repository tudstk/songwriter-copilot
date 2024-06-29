import styled from "@emotion/styled";
import { FC, useState } from "react";
import { Localized } from "../../../components/Localized";
import { Tooltip } from "../../../components/Tooltip";
import { ToolbarButton } from "./ToolbarButton";
import { getSong } from "../../actions"
import { useStores } from "../../hooks/useStores"

const DarkInput = styled.input`
    background-color: #1e1f24;
    color: white;
    width: 3rem;
    height: 1rem;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    margin-right: 0.5rem;
    cursor: pointer;

    &:hover {
        background-color: #555;
    }
`;

const CloseButton = styled.button`
    background: none;
    border: none;
    color: white;
    font-size: 1rem;
    cursor: pointer;
    margin-left: 0.5rem;
    margin-right: 0.5rem;
    &:hover {
        color: gray;
    }
`;

const Label = styled.label`
    color: white;
    margin-right: 0.5rem;
`;

const Select = styled.select`
    background-color: #1e1f24;
    color: white;
    height: 2rem;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 999px;
    margin-right: 0.5rem;
    cursor: pointer;

    &:hover {
        background-color: #555;
    }
`;

const steps = [
  "Number of bars",
  "Number of notes",
  "Number of steps",
  "Pauses",
  "Key",
  "Scale",
  "Root",
  "Population size",
  "Generation Number",
  "Fitness Choice"
];

export const GenerateMusicIdeaButton: FC = () => {
  const rootStore = useStores();
  const [barsNumber, setBarsNumber] = useState(4);
  const [notesNumber, setNotesNumber] = useState(8);
  const [stepsNumber, setStepsNumber] = useState(1);
  const [pauses, setPauses] = useState("yes");
  const [key, setKey] = useState("C");
  const [scale, setScale] = useState("major");
  const [root, setRoot] = useState(4);
  const [populationSize, setPopulationSize] = useState(4);
  const [fitnessChoice, setFitnessChoice] = useState('Automated');
  const [currentStep, setCurrentStep] = useState(0);
  const [keySignature, setKeySignature] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [rating, setRating] = useState(0);
  const [generatedClicked, setGeneratedClicked] = useState(false);
  const [midiFiles, setMidiFiles] = useState<string[]>([]);
  const [generationIndex, setGenerationIndex] = useState(0);
  const [genomeIndex, setGenomeIndex] = useState(0);
  const [startRatingClicked, setStartRatingClicked] = useState(false);
  const [numberOfGenerations, setNumberOfGenerations] = useState(10);
  const handleInitialClick = () => {
    setShowOptions(true);
  };

  const handleCloseClick = () => {
    setShowOptions(false);
    setKeySignature("");
    setCurrentStep(0);
  };


  const handleAutomatedFitnessSteps = async (e: React.MouseEvent<HTMLButtonElement>) => {
    setStartRatingClicked(true);
    e.preventDefault();

    const fetchUrl = `http://127.0.0.1:5000/get_best_genome?generation_index=${generationIndex}`;

    try {
      const response = await fetch(fetchUrl);
      if (!response.ok) {
        throw new Error('Failed to fetch MIDI file');
      }

      const midiBlob = await response.blob();
      const filename = `best.mid`;
      const file = new File([midiBlob], filename, { type: 'audio/midi' });

      console.log("SUNT IN TRY");
      await getSong(rootStore)(file);
      setGenomeIndex(genomeIndex + 1);
      setGenerationIndex(generationIndex + 1)
    } catch (error) {
      console.error((error as Error).message);
    }
  };

  const startRating = async (e: React.MouseEvent<HTMLButtonElement>) =>  {

    setStartRatingClicked(true);
    e.preventDefault()
    if(fitnessChoice === 'Rating'){
      const response = await fetch(`http://127.0.0.1:5000/get_genome?scale=${scale}&key=${key}&genome_index=0&generation_index=0`);
      if (!response.ok) {
        throw new Error('Failed to fetch MIDI file');
      }
      const midiBlob = await response.blob();
      const filename = `${scale}-${key}-0.mid`;
      const file = new File([midiBlob], filename, { type: 'audio/midi' });

      try {
        await getSong(rootStore)(file);
      } catch (e) {
        console.error((e as Error).message);
      }
    }
    else
    {
      const response = await fetch(`http://127.0.0.1:5000/get_best_genome?generation_index=0`);
      if (!response.ok) {
        throw new Error('Failed to fetch MIDI file');
      }
      const midiBlob = await response.blob();
      const filename = `best.mid`;
      const file = new File([midiBlob], filename, { type: 'audio/midi' });

      try {
        await getSong(rootStore)(file);
        setGenomeIndex(genomeIndex + 1);
        setGenerationIndex(generationIndex + 1)
      } catch (e) {
        console.error((e as Error).message);
      }
    }
  }

  const handleClick = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    if (!generatedClicked) {
      setGeneratedClicked(true);

      console.log('Generate button clicked');
      console.log('Fitness Choice:', fitnessChoice)
      try {
        const generateMelodyResponse = await fetch(`http://127.0.0.1:5000/generate_custom_melody`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            bars: barsNumber,
            num_notes: notesNumber,
            num_steps: stepsNumber,
            pauses: pauses,
            key: key,
            scale: scale,
            root: root,
            population_size: populationSize,
            number_of_generations:numberOfGenerations,
            fitness_choice: fitnessChoice,
          }),
        });
        if (!generateMelodyResponse.ok) {
          throw new Error('Failed to generate music');
        }
        const midiFiles = await generateMelodyResponse.json();
        setMidiFiles(midiFiles);

      } catch (error) {
        console.error(error);
      }
    } else if(fitnessChoice === 'Feedback'){
      setShowOptions(false);
      setKeySignature("");
      setCurrentStep(0);
      e.preventDefault();
      console.log('Button clicked');
      try {
        const response = await fetch(`http://127.0.0.1:5000/get_genome?scale=${scale}&key=${key}&genome_index=${genomeIndex}&generation_index=${generationIndex}`);
        if (!response.ok) {
          throw new Error('Failed to fetch MIDI file');
        }
        const midiBlob = await response.blob();
        const filename = `${scale}-${key}-${genomeIndex}.mid`;
        const file = new File([midiBlob], filename, { type: 'audio/midi' });

        try {
          await getSong(rootStore)(file);
          if (genomeIndex == populationSize - 1) {
            setGenerationIndex(generationIndex + 1);
            setGenomeIndex(0);
          } else{
            setGenomeIndex(genomeIndex + 1);
          }
          const ratingResponse = await fetch(`http://127.0.0.1:5000/rate_melody`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              filename: filename,
              rating: rating,
            }),
          });
          if (!ratingResponse.ok) {
            throw new Error('Failed to send rating');
          }
          console.log('Rating sent', rating);
        } catch (e) {
          console.error((e as Error).message);
        }
      } catch (error) {
        console.error('Error opening MIDI file:', error);
      }
    }
    else{
      setShowOptions(false);
      setKeySignature("");
      setCurrentStep(0);
      e.preventDefault();
      console.log('Button clicked');
      try {
        const response = await fetch(`http://127.0.0.1:5000/get_best_genome?generation_index=${generationIndex}`);
        if (!response.ok) {
          throw new Error('Failed to fetch MIDI file');
        }
        const midiBlob = await response.blob();
        const filename = `best.mid`;
        const file = new File([midiBlob], filename, { type: 'audio/midi' });

        try {
          await getSong(rootStore)(file);
          if (genomeIndex == populationSize - 1) {
            setGenerationIndex(generationIndex + 1);
          }
        } catch (e) {
          console.error((e as Error).message);
        }
      } catch (error) {
        console.error('Error opening MIDI file:', error);
      }
    }
  };

  const nextStep = () => {
    setCurrentStep(currentStep + 1);
  };

  const renderCurrentStep = () => {
    switch (steps[currentStep]) {
      case "Number of bars":
        return (
          <>
            <Label htmlFor="barsInput">Number of bars</Label>
            <DarkInput
              id="barsInput"
              type="number"
              min="1"
              max="32"
              value={barsNumber}
              onChange={(e) => setBarsNumber(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Number of notes":
        return (
          <>
            <Label htmlFor="notesInput">Number of notes</Label>
            <DarkInput
              id="notesInput"
              type="number"
              min="1"
              value={notesNumber}
              onChange={(e) => setNotesNumber(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Number of steps":
        return (
          <>
            <Label htmlFor="stepsInput">Number of steps</Label>
            <DarkInput
              id="stepsInput"
              type="number"
              min="1"
              value={stepsNumber}
              onChange={(e) => setStepsNumber(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Pauses":
        return (
          <>
            <Label htmlFor="pausesInput">Pauses</Label>
            <Select id="pausesInput" value={pauses} onChange={(e) => setPauses(e.target.value)}>
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </Select>
          </>
        );
      case "Key":
        return (
          <>
            <Label htmlFor="keyInput">Key</Label>
            <Select id="keyInput" value={key} onChange={(e) => setKey(e.target.value)}>
              {["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"].map(k => (
                <option key={k} value={k}>{k}</option>
              ))}
            </Select>
          </>
        );
      case "Scale":
        return (
          <>
            <Label htmlFor="scaleInput">Scale</Label>
            <Select id="scaleInput" value={scale} onChange={(e) => setScale(e.target.value)}>
              {["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </Select>
          </>
        );
      case "Root":
        return (
          <>
            <Label htmlFor="rootInput">Root</Label>
            <DarkInput
              id="rootInput"
              type="number"
              min="1"
              max="7"
              value={root}
              onChange={(e) => setRoot(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Population size":
        return (
          <>
            <Label htmlFor="populationInput">Population size</Label>
            <DarkInput
              id="populationInput"
              type="number"
              min="1"
              max="200"
              value={populationSize}
              onChange={(e) => setPopulationSize(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Generation Number":
        return (
          <>
            <Label htmlFor="generationInput">Number of Generations</Label>
            <DarkInput
              id="generationInput"
              type="number"
              min="1"
              max="100"
              value={numberOfGenerations}
              onChange={(e) => setNumberOfGenerations(parseInt(e.target.value, 10))}
            />
          </>
        );
      case "Fitness Choice":
        return (
          <>
            <Label htmlFor="fitnessInput">Fitness Choice</Label>
            <Select id="fitnessInput" value={fitnessChoice} onChange={(e) => setFitnessChoice(e.target.value)}>
              <option value="Automated">Automated</option>
              <option value="Feedback">Feedback</option>
            </Select>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Tooltip title={<Localized default="Auto-Scroll">auto-scroll</Localized>}>
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center' }}>
        {!showOptions && !generatedClicked && (
          <ToolbarButton onMouseDown={handleInitialClick}>
            Generate Music Idea
          </ToolbarButton>
        )}
        {showOptions && (
          <>
            {renderCurrentStep()}
            {(currentStep < steps.length - 1 && !generatedClicked) ? (
              <ToolbarButton onMouseDown={nextStep}>Next</ToolbarButton>
            ) : (
              <ToolbarButton onMouseDown={handleClick}>
                Generate
              </ToolbarButton>
            )}
            <CloseButton onMouseDown={handleCloseClick}>×</CloseButton>
          </>
        )}
        {generatedClicked && (
          <>
            {
              !startRatingClicked ? (
                <ToolbarButton onMouseDown={startRating}>
                  Start
                </ToolbarButton>
              ) : (
                <>
                  {
                    fitnessChoice === 'Feedback' ? (
                      <>
                        <Label htmlFor="ratingInput">Rating</Label>
                        <Select
                          id="ratingInput"
                          value={rating}
                          onChange={(e) => setRating(parseInt(e.target.value))}
                        >
                          {[0, 1, 2, 3, 4, 5].map((value) => (
                            <option key={value} value={value}>
                              {value}
                            </option>
                          ))}
                        </Select>
                        <ToolbarButton onMouseDown={handleClick}>
                          Send
                        </ToolbarButton>
                      </>
                    ) :
                      <>
                        <ToolbarButton onMouseDown={handleAutomatedFitnessSteps}>
                          Next
                        </ToolbarButton>
                      </>
                  }
                </>
              )
            }
          </>
        )}
      </div>
    </Tooltip>
  );
};
