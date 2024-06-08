import styled from "@emotion/styled"
import * as Popover from "@radix-ui/react-popover"
import { ReactNode } from "react"
import { Checkbox } from "../../../../components/Checkbox"
import { Localized } from "../../../../components/Localized"
import { NumberPicker } from "./NumberPicker"

export interface QuantizePopupProps {
  value: number
  values: number[]
  triplet: boolean
  dotted: boolean
  trigger: ReactNode
  onChangeValue: (value: number) => void
  onChangeTriplet: (value: boolean) => void
  onChangeDotted: (value: boolean) => void
}

const Container = styled.div`
  background: ${({ theme }) => theme.secondaryBackgroundColor};
  border: 1px solid ${({ theme }) => theme.backgroundColor};
  box-shadow: 0 1rem 3rem ${({ theme }) => theme.shadowColor};
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  display: flex;
  position: relative;
  top: 1rem;
  left: 0.25rem;

  &::before {
    content: "";
    width: 1rem;
    height: 1rem;
    background: ${({ theme }) => theme.secondaryBackgroundColor};
    position: absolute;
    top: -0.5rem;
    left: calc(50% - 1rem);
    transform: rotate(45deg);
  }

  .button-up {
    margin-bottom: -0.4rem;
  }

  .button-down {
    margin-top: -0.1rem;
  }
`

const Right = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin-left: 1rem;
`

export function QuantizePopup({
  value = 8,
  values,
  triplet,
  dotted,
  onChangeValue,
  onChangeTriplet,
  onChangeDotted,
  trigger,
}: QuantizePopupProps) {
  const prevValue = () => {
    const index = Math.max(values.indexOf(value) - 1, 0)
    return values[index]
  }
  const nextValue = () => {
    const index = Math.min(values.indexOf(value) + 1, values.length - 1)
    return values[index]
  }

  return (
    <Popover.Root>
      <Popover.Trigger asChild>{trigger}</Popover.Trigger>
      <Popover.Portal>
        <Popover.Content>
          <Container>
            <NumberPicker
              value={value}
              prevValue={prevValue}
              nextValue={nextValue}
              onChange={onChangeValue}
            />
            <Right>
              <Checkbox
                onCheckedChange={(state) => onChangeTriplet(state === true)}
                checked={triplet}
                label={<Localized default="Triplet">triplet</Localized>}
                style={{ marginBottom: "0.5rem" }}
              />
              <Checkbox
                onCheckedChange={(state) => onChangeDotted(state === true)}
                checked={dotted}
                label={<Localized default="Dotted">dotted</Localized>}
              />
            </Right>
          </Container>
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  )
}
