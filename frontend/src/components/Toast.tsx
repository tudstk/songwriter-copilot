import { keyframes } from "@emotion/react"
import styled from "@emotion/styled"
import * as Portal from "@radix-ui/react-portal"
import Error from "mdi-react/AlertCircleIcon"
import Warning from "mdi-react/AlertIcon"
import CheckCircle from "mdi-react/CheckCircleIcon"
import Info from "mdi-react/InformationIcon"
import { FC, useEffect, useState } from "react"
import { Theme } from "../common/theme/Theme"
import { useTheme } from "../main/hooks/useTheme"
import { ToastSeverity } from "../main/hooks/useToast"

export interface ToastProps {
  message: string
  severity: ToastSeverity
  onExited: () => void
}

const contentShow = keyframes`
  from {
    opacity: 0;
    transform: translate(0, 0.5rem) scale(0.96);
  }
  to {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
`

const contentHide = keyframes`
  from {
    opacity: 1;
    transform: translate(0, 0) scale(1);
  }
  to {
    opacity: 0;
    transform: translate(0, 0.5rem) scale(0.96);
  }
`

const Root = styled(Portal.Root)`
  position: fixed;
  bottom: 2rem;
  left: 0;
  right: 0;
  display: flex;
`

const Content = styled.div`
  margin: 0 auto;
  background: ${({ theme }) => theme.secondaryBackgroundColor};
  padding: 1rem;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  box-shadow: 0 0.5rem 3rem ${({ theme }) => theme.shadowColor};
  display: flex;
  align-items: center;

  animation: ${({ show }: { show: boolean }) =>
      show ? contentShow : contentHide}
    500ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
`

const SeverityIcon: FC<{ severity: ToastSeverity }> = ({ severity }) => {
  const theme = useTheme()
  const fill = colorForSeverity(severity, theme)
  switch (severity) {
    case "error":
      return <Error style={{ fill }} />
    case "info":
      return <Info style={{ fill }} />
    case "success":
      return <CheckCircle style={{ fill }} />
    case "warning":
      return <Warning style={{ fill }} />
  }
}

const exitDuration = 5000

export const Toast: FC<ToastProps> = ({ message, severity, onExited }) => {
  const [show, setShow] = useState(true)

  useEffect(() => {
    const timeout = setTimeout(() => setShow(false), exitDuration - 500)
    const timeout2 = setTimeout(onExited, exitDuration)
    return () => {
      clearTimeout(timeout)
      clearTimeout(timeout2)
    }
  })
  return (
    <Root>
      <Content show={show}>
        <SeverityIcon severity={severity} />
        <div style={{ width: "0.5rem" }} />
        {message}
      </Content>
    </Root>
  )
}

const colorForSeverity = (severity: ToastSeverity, theme: Theme) => {
  switch (severity) {
    case "error":
      return theme.redColor
    case "info":
      return theme.textColor
    case "success":
      return theme.greenColor
    case "warning":
      return theme.yellowColor
  }
}
