import type { AssistantMessage, ToolPart } from "@opencode-ai/sdk/v2"
import type { TuiPlugin, TuiPluginApi } from "@opencode-ai/plugin/tui"
import type { BuiltinTuiPlugin } from "../builtins"
import { createMemo, For, Show } from "solid-js"

const id = "internal:sidebar-activity"

function label(part: ToolPart): string {
  const input = (part.state.status === "pending" ? {} : (part.state.input ?? {})) as Record<string, unknown>
  const pick = (...keys: string[]) => {
    for (const k of keys) {
      const v = input[k]
      if (typeof v === "string" && v) return v
    }
    return ""
  }
  return pick("filePath", "pattern", "command", "query", "url", "prompt") || part.tool
}

function icon(part: ToolPart): string {
  switch (part.tool) {
    case "read":
      return "→"
    case "glob":
    case "grep":
      return "✱"
    case "bash":
    case "execute":
      return "$"
    case "write":
    case "edit":
      return "✎"
    case "webfetch":
    case "websearch":
      return "◈"
    default:
      return "⚙"
  }
}

function color(theme: any, part: ToolPart): any {
  switch (part.tool) {
    case "read":
    case "webfetch":
    case "websearch":
      return theme.info
    case "glob":
    case "grep":
      return theme.warning
    case "bash":
    case "execute":
      return theme.success
    default:
      return theme.text
  }
}

function View(props: { api: TuiPluginApi; session_id: string }) {
  const theme = () => props.api.theme.current
  const running = createMemo(() => {
    const msgs = props.api.state.session.messages(props.session_id)
    const last = msgs.findLast((m): m is AssistantMessage => m.role === "assistant")
    if (!last) return []
    return props.api.state
      .part(last.id)
      .filter((p): p is ToolPart => p.type === "tool" && (p.state.status === "running" || p.state.status === "pending"))
  })

  return (
    <Show when={running().length > 0}>
      <box>
        <text fg={theme().text}>
          <b>Activity</b>
        </text>
        <For each={running()}>
          {(part) => (
            <text fg={color(theme(), part)}>
              {icon(part)} {label(part)}
            </text>
          )}
        </For>
      </box>
    </Show>
  )
}

const tui: TuiPlugin = async (api) => {
  api.slots.register({
    order: 300,
    slots: {
      sidebar_content(_ctx, props) {
        return <View api={api} session_id={props.session_id} />
      },
    },
  })
}

const plugin: BuiltinTuiPlugin = {
  id,
  tui,
}

export default plugin
