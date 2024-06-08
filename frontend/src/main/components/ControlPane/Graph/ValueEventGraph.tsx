import { MIDIControlEvents } from "midifile-ts"
import { observer } from "mobx-react-lite"
import React, { FC, useMemo } from "react"
import { ISize } from "../../../../common/geometry"
import { ValueEventType } from "../../../../common/helpers/valueEvent"
import { useStores } from "../../../hooks/useStores"
import LineGraphControl from "../LineGraph/LineGraph"

export type ValueEventGraphProps = ISize & {
  type: ValueEventType
}

const axisForType = (type: ValueEventType) => {
  switch (type.type) {
    case "controller":
      return [0, 0x20, 0x40, 0x60, 0x80 - 1]
    case "pitchBend":
      return [0, 0x1000, 0x2000, 0x3000, 0x4000 - 1]
  }
}

const maxValueForType = (type: ValueEventType) => {
  switch (type.type) {
    case "controller":
      return 127
    case "pitchBend":
      return 0x4000
  }
}

const labelFormatterForType = (
  type: ValueEventType,
): ((v: number) => string) => {
  switch (type.type) {
    case "controller":
      switch (type.controllerType) {
        case MIDIControlEvents.MSB_PAN:
          return (v) => (v - 0x40).toString()
        default:
          return (v) => v.toString()
      }
    case "pitchBend":
      return (v) => (v - 0x2000).toString()
    default:
      return (v) => v.toString()
  }
}

export const ValueEventGraph: FC<ValueEventGraphProps> = React.memo(
  observer(({ width, height, type }) => {
    const {
      controlStore: { controlValueEvents: events },
    } = useStores()

    const axis = useMemo(() => axisForType(type), [type])
    const maxValue = useMemo(() => maxValueForType(type), [type])
    const labelFormatter = useMemo(() => labelFormatterForType(type), [type])

    return (
      <LineGraphControl
        width={width}
        height={height}
        maxValue={maxValue}
        events={events}
        axis={axis}
        eventType={type}
        axisLabelFormatter={labelFormatter}
      />
    )
  }),
)
