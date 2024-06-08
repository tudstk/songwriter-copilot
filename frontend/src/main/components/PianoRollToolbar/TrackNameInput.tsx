import styled from "@emotion/styled"
import { observer } from "mobx-react-lite"
import { FC, useState } from "react"
import { useStores } from "../../hooks/useStores"
import { TrackName } from "../TrackList/TrackName"

const TrackNameWrapper = styled.span`
  font-weight: bold;
  margin-right: 2em;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 14rem;
  min-width: 3em;
`

const Input = styled.input`
  font-size: inherit;
  font-family: inherit;
  border: ${({ theme }) => theme.dividerColor} 1px solid;
  color: inherit;
  height: 2rem;
  padding: 0 0.5rem;
  box-sizing: border-box;
  border-radius: 4px;
  margin-right: 1em;
  background: #00000017;
  outline: none;
`

export const TrackNameInput: FC = observer(() => {
  const {
    pianoRollStore: { selectedTrack },
  } = useStores()

  if (selectedTrack === undefined) {
    return <></>
  }

  const [isEditing, setEditing] = useState(false)
  return (
    <>
      {isEditing ? (
        <Input
          defaultValue={selectedTrack.name ?? ""}
          ref={(c) => c?.focus()}
          // to support IME we use onKeyPress instead of onKeyDown for capture Enter
          onKeyPress={(e) => {
            if (e.key === "Enter") {
              selectedTrack.setName(e.currentTarget.value)
              setEditing(false)
            }
          }}
          onKeyDown={(e) => {
            if (e.key === "Escape") {
              setEditing(false)
            }
          }}
          onBlur={() => setEditing(false)}
        />
      ) : (
        <TrackNameWrapper onDoubleClick={() => setEditing(true)}>
          <TrackName track={selectedTrack} />
        </TrackNameWrapper>
      )}
    </>
  )
})
