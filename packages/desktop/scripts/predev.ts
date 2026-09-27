import { $ } from "bun"
import { downloadCliToResources } from "./utils"

// ponytail: free tier gates on client version, dev branch would report 0.0.0-dev
process.env.OPENCODE_VERSION ??= "1.18.32"

await $`bun run install-electron`

await $`bun ./scripts/copy-icons.ts ${process.env.OPENCODE_CHANNEL ?? "dev"}`

await $`cd ../opencode && bun script/build-node.ts`
await downloadCliToResources()
