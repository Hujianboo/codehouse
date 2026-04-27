# Codex Token Castles

`codehouse` is a small companion TUI for Codex. It reads local session logs
from `~/.codex/sessions/**/*.jsonl`, finds `token_count` events, and turns the
current day's token usage into identical completed castles plus one castle under
construction.

When Codex writes a new `token_count` event, the TUI does not jump straight to
the final count. It plays the newly detected tokens as a construction animation:
site prep, foundation, walls, towers, flags, windows, gate, then a completed
castle.

Completed castles are summarized as a single castle icon with `* N`, while the
next castle is shown separately as the one currently under construction.
In the live TUI, the castle keeps the ASCII shape and uses restrained color:
warm stone, small red flag accents, yellow windows, a muted gate, and green
grass at the bottom. Use
`--no-solid` for outline-only color, or `--no-color` for plain monochrome.

Crew mode shows one castle per worker in the current thread family. Subagents
use their session metadata, so a spawned explorer like `Nash` gets its own
castle next to the main Codex session.

It does not need its own database. Every launch recomputes usage from the local
Codex session files, so reopening the TUI restores the current state.

## Install

Install from GitHub:

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | sh
```

The installer downloads `codex_house.py` into `~/.local/share/codehouse` and
creates these commands in `~/.local/bin`:

```sh
codehouse
codex-house
```

If `~/.local/bin` is not in your `PATH`, the installer will offer to add it to
your shell profile. For non-interactive installs, you can opt in explicitly:

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | CODEHOUSE_UPDATE_PROFILE=1 sh
```

Install a specific branch or tag:

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | CODEHOUSE_REF=v0.1.0 sh
```

## Run

```sh
codehouse
```

Open in a separate macOS Terminal window:

```sh
codehouse --window
```

Print one snapshot:

```sh
codehouse --once
```

Useful options:

```sh
codehouse --castle-tokens 500000
codehouse --scale large
codehouse --date 2026-04-27
codehouse --refresh 0.5
codehouse --seconds-per-castle 4
codehouse --pace slow
codehouse --crew
codehouse -all
codehouse --no-color
codehouse --no-solid
```

Legacy aliases `codex-house`, `--agents`, `--all-agents`, and `--all-castles`
still work, but the friendlier commands are `codehouse`, `--crew`, and `-all`.

Run the legacy command name if you prefer:

```sh
codex-house
```
