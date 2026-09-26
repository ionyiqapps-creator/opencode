import { useTheme } from "../context/theme"
import { TextAttributes } from "@opentui/core"

export interface TodoItemProps {
  status: string
  content: string
}

export function TodoItem(props: TodoItemProps) {
  const { theme } = useTheme()
  const done = () => props.status !== "pending"

  return (
    <box flexDirection="row" gap={0}>
      <text
        flexShrink={0}
        attributes={done() ? TextAttributes.BOLD : undefined}
        style={{
          fg: done() ? theme.success : theme.textMuted,
        }}
      >
        [{props.status === "completed" ? "✓" : props.status === "in_progress" ? "•" : " "}]{" "}
      </text>
      <text
        flexGrow={1}
        wrapMode="word"
        attributes={props.status === "in_progress" ? TextAttributes.BOLD : undefined}
        style={{
          fg: done() ? theme.success : theme.textMuted,
        }}
      >
        {props.content}
      </text>
    </box>
  )
}
