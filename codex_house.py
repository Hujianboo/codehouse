#!/usr/bin/env python3
"""A tiny TUI that turns local Codex token usage into castles."""

from __future__ import annotations

import argparse
import curses
import json
import os
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_HOUSE_TOKENS = 500_000
DEFAULT_REFRESH_SECONDS = 0.25
DEFAULT_SECONDS_PER_HOUSE = 10.0
SCALE_HOUSE_TOKENS = {
    "small": 100_000,
    "normal": DEFAULT_HOUSE_TOKENS,
    "large": 1_000_000,
}
PACE_SECONDS_PER_HOUSE = {
    "slow": 18.0,
    "normal": DEFAULT_SECONDS_PER_HOUSE,
    "fast": 4.0,
}

COMPLETE_HOUSE = [
    "       |>>>             |>>>       ",
    "       |                |          ",
    "    [__|__]          [__|__]       ",
    "    |  [] |__________| []  |       ",
    "    |     |  []  []  |     |       ",
    "    |_____|__________|_____|       ",
    "    |#####|   ____   |#####|       ",
    "   /______|__|    |__|______\\      ",
    "  /____________________________\\    ",
    "       /_/              \\_\\        ",
]

PARTIAL_HOUSES = [
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "  ............................    ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "   /______          ______\\       ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "                                  ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "                                  ",
        "    |     |__________|     |      ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "    [_____]          [_____]      ",
        "    |     |__________|     |      ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "                                  ",
        "                                  ",
        "    [__|__]          [__|__]      ",
        "    |     |__________|     |      ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "       |                |         ",
        "       |                |         ",
        "    [__|__]          [__|__]      ",
        "    |     |__________|     |      ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "       |>>>             |>>>      ",
        "       |                |         ",
        "    [__|__]          [__|__]      ",
        "    |     |__________|     |      ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "       |>>>             |>>>      ",
        "       |                |         ",
        "    [__|__]          [__|__]      ",
        "    |  [] |__________| []  |      ",
        "    |     |          |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "       |>>>             |>>>      ",
        "       |                |         ",
        "    [__|__]          [__|__]      ",
        "    |  [] |__________| []  |      ",
        "    |     |  []  []  |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|          |#####|      ",
        "   /______|__________|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "       |>>>             |>>>      ",
        "       |                |         ",
        "    [__|__]          [__|__]      ",
        "    |  [] |__________| []  |      ",
        "    |     |  []  []  |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|   ____   |#####|      ",
        "   /______|__|    |__|______\\     ",
        "  /____________________________\\  ",
        "                                  ",
    ],
    [
        "       |>>>             |>>>      ",
        "       |                |         ",
        "    [__|__]          [__|__]      ",
        "    |  [] |__________| []  |      ",
        "    |     |  []  []  |     |      ",
        "    |_____|__________|_____|      ",
        "    |#####|   ____   |#####|      ",
        "   /______|__|    |__|______\\     ",
        "  /____________________________\\  ",
        "       /_/              \\_\\       ",
    ],
]


@dataclass(frozen=True)
class AgentUsage:
    agent_id: str
    label: str
    role: str | None
    parent_thread_id: str | None
    is_subagent: bool
    started_at: datetime | None
    by_day: dict[str, int]
    latest_total: int
    latest_event_time: datetime | None


@dataclass(frozen=True)
class UsageSnapshot:
    by_day: dict[str, int]
    agents: list[AgentUsage]
    latest_session_tokens: int
    latest_session_path: Path | None
    latest_session_id: str | None
    latest_root_thread_id: str | None
    latest_event_time: datetime | None
    scanned_at: datetime


@dataclass
class FileState:
    position: int = 0
    previous_total: int = 0
    latest_total: int = 0
    latest_time: datetime | None = None
    mtime_ns: int = 0
    buffer: str = ""
    session_id: str | None = None
    label: str | None = None
    role: str | None = None
    parent_thread_id: str | None = None
    is_subagent: bool = False
    started_at: datetime | None = None


@dataclass
class BuildAnimation:
    current_tokens: float | None = None
    start_tokens: float = 0.0
    target_tokens: int = 0
    started_at: float = 0.0
    duration: float = 0.0

    def value(self, now: float) -> float:
        if self.current_tokens is None:
            return float(self.target_tokens)
        if self.duration <= 0:
            return float(self.target_tokens)

        progress = min(1.0, max(0.0, (now - self.started_at) / self.duration))
        return self.start_tokens + (self.target_tokens - self.start_tokens) * progress

    def update(self, target_tokens: int, house_tokens: int, seconds_per_house: float, now: float) -> float:
        if self.current_tokens is None:
            self.current_tokens = float(target_tokens)
            self.start_tokens = float(target_tokens)
            self.target_tokens = target_tokens
            self.started_at = now
            self.duration = 0.0
            return self.current_tokens

        current = self.value(now)
        if target_tokens < current:
            self.current_tokens = float(target_tokens)
            self.start_tokens = float(target_tokens)
            self.target_tokens = target_tokens
            self.started_at = now
            self.duration = 0.0
            return self.current_tokens

        if target_tokens != self.target_tokens:
            delta = target_tokens - current
            self.start_tokens = current
            self.target_tokens = target_tokens
            self.started_at = now
            houses = delta / max(1, house_tokens)
            self.duration = min(30.0, max(0.75, houses * seconds_per_house))

        self.current_tokens = self.value(now)
        return self.current_tokens


def parse_timestamp(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone()
    except ValueError:
        return None


def token_total_from_line(line: str) -> tuple[datetime | None, int | None]:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None, None

    payload = obj.get("payload") or {}
    if payload.get("type") != "token_count":
        return None, None

    usage = ((payload.get("info") or {}).get("total_token_usage") or {})
    total = usage.get("total_tokens")
    if not isinstance(total, int):
        return None, None

    return parse_timestamp(obj.get("timestamp")), total


def session_meta_from_line(line: str) -> dict | None:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None
    if obj.get("type") != "session_meta":
        return None
    payload = obj.get("payload")
    return payload if isinstance(payload, dict) else None


def iter_session_files(codex_home: Path) -> list[Path]:
    sessions_dir = codex_home / "sessions"
    if not sessions_dir.exists():
        return []
    return sorted(sessions_dir.glob("**/*.jsonl"))


class UsageTracker:
    def __init__(self, codex_home: Path, discovery_interval: float = 2.0) -> None:
        self.codex_home = codex_home
        self.discovery_interval = discovery_interval
        self.by_day: dict[str, int] = defaultdict(int)
        self.by_agent_day: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.files: dict[Path, FileState] = {}
        self.latest_session_tokens = 0
        self.latest_session_path: Path | None = None
        self.latest_session_id: str | None = None
        self.latest_event_time: datetime | None = None
        self.next_discovery = 0.0

    def scan(self) -> UsageSnapshot:
        now = time.monotonic()
        if now >= self.next_discovery:
            self.discover_files()
            self.next_discovery = now + self.discovery_interval

        for path, state in list(self.files.items()):
            self.scan_file(path, state)

        return UsageSnapshot(
            by_day=dict(self.by_day),
            agents=self.agent_usages(),
            latest_session_tokens=self.latest_session_tokens,
            latest_session_path=self.latest_session_path,
            latest_session_id=self.latest_session_id,
            latest_root_thread_id=self.root_thread_id(self.latest_session_id),
            latest_event_time=self.latest_event_time,
            scanned_at=datetime.now().astimezone(),
        )

    def discover_files(self) -> None:
        for path in iter_session_files(self.codex_home):
            self.files.setdefault(path, FileState())

    def agent_key(self, path: Path, state: FileState) -> str:
        return state.session_id or path.stem

    def root_thread_id(self, session_id: str | None) -> str | None:
        if session_id is None:
            return None
        states_by_id = {
            state.session_id: state
            for state in self.files.values()
            if state.session_id
        }
        current = session_id
        seen: set[str] = set()
        while current and current not in seen:
            seen.add(current)
            state = states_by_id.get(current)
            if not state or not state.parent_thread_id:
                return current
            current = state.parent_thread_id
        return current or session_id

    def agent_label(self, agent_id: str, state: FileState | None) -> str:
        if state is None:
            return f"Agent {agent_id[-4:]}"
        if state.label:
            return state.label
        if state.is_subagent:
            return f"Agent {agent_id[-4:]}"
        return "Main"

    def agent_usages(self) -> list[AgentUsage]:
        states_by_id = {
            state.session_id: state
            for state in self.files.values()
            if state.session_id
        }
        agents: list[AgentUsage] = []
        for agent_id, by_day in self.by_agent_day.items():
            state = states_by_id.get(agent_id)
            agents.append(
                AgentUsage(
                    agent_id=agent_id,
                    label=self.agent_label(agent_id, state),
                    role=state.role if state else None,
                    parent_thread_id=state.parent_thread_id if state else None,
                    is_subagent=state.is_subagent if state else False,
                    started_at=state.started_at if state else None,
                    by_day=dict(by_day),
                    latest_total=state.latest_total if state else 0,
                    latest_event_time=state.latest_time if state else None,
                )
            )
        return sorted(
            agents,
            key=lambda agent: (
                agent.parent_thread_id is not None,
                agent.label.lower(),
                agent.agent_id,
            ),
        )

    def scan_file(self, path: Path, state: FileState) -> None:
        try:
            stat = path.stat()
        except OSError:
            return

        if stat.st_size < state.position:
            state.position = 0
            state.previous_total = 0
            state.latest_total = 0
            state.latest_time = None
            state.buffer = ""
            state.session_id = None
            state.label = None
            state.role = None
            state.parent_thread_id = None
            state.is_subagent = False
            state.started_at = None

        if stat.st_size == state.position and stat.st_mtime_ns == state.mtime_ns:
            return

        try:
            with path.open(errors="ignore") as handle:
                handle.seek(state.position)
                chunk = handle.read()
                state.position = handle.tell()
        except OSError:
            return

        state.mtime_ns = stat.st_mtime_ns
        if not chunk:
            return

        text = state.buffer + chunk
        if text.endswith(("\n", "\r")):
            lines = text.splitlines()
            state.buffer = ""
        else:
            lines = text.splitlines()
            state.buffer = lines.pop() if lines else text

        for line in lines:
            meta = session_meta_from_line(line)
            if meta is not None:
                self.apply_session_meta(meta, path, state)
                continue

            event_time, total = token_total_from_line(line)
            if event_time is None or total is None:
                continue

            delta = max(0, total - state.previous_total)
            if delta:
                day = event_time.strftime("%Y-%m-%d")
                self.by_day[day] += delta
                self.by_agent_day[self.agent_key(path, state)][day] += delta
            state.previous_total = max(state.previous_total, total)
            state.latest_total = total
            state.latest_time = event_time

            if self.latest_event_time is None or event_time > self.latest_event_time:
                self.latest_event_time = event_time
                self.latest_session_tokens = total
                self.latest_session_path = path
                self.latest_session_id = self.agent_key(path, state)

    def apply_session_meta(self, meta: dict, path: Path, state: FileState) -> None:
        session_id = meta.get("id")
        state.session_id = session_id if isinstance(session_id, str) else path.stem
        timestamp = meta.get("timestamp")
        state.started_at = parse_timestamp(timestamp) if isinstance(timestamp, str) else None

        nickname = meta.get("agent_nickname")
        role = meta.get("agent_role")
        state.label = nickname if isinstance(nickname, str) and nickname else None
        state.role = role if isinstance(role, str) and role else None

        source = meta.get("source")
        spawn = None
        if isinstance(source, dict):
            subagent = source.get("subagent")
            if isinstance(subagent, dict):
                maybe_spawn = subagent.get("thread_spawn")
                if isinstance(maybe_spawn, dict):
                    spawn = maybe_spawn

        if spawn:
            parent = spawn.get("parent_thread_id")
            state.parent_thread_id = parent if isinstance(parent, str) else None
            state.is_subagent = True
            nickname = spawn.get("agent_nickname")
            role = spawn.get("agent_role")
            if isinstance(nickname, str) and nickname:
                state.label = nickname
            if isinstance(role, str) and role:
                state.role = role


def scan_usage(codex_home: Path) -> UsageSnapshot:
    tracker = UsageTracker(codex_home)
    return tracker.scan()


def house_counts(tokens: int, house_tokens: int) -> tuple[int, int, float]:
    completed = tokens // house_tokens
    remainder = tokens % house_tokens
    progress = remainder / house_tokens if house_tokens else 0
    return completed, remainder, progress


def partial_house(progress: float) -> list[str]:
    if progress <= 0:
        return PARTIAL_HOUSES[0]
    index = min(len(PARTIAL_HOUSES) - 1, int(progress * len(PARTIAL_HOUSES)))
    return PARTIAL_HOUSES[index]


def progress_bar(progress: float, width: int = 24) -> str:
    progress = min(1.0, max(0.0, progress))
    filled = int(progress * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def format_int(value: int) -> str:
    return f"{value:,}"


def render_castle_plain(art: list[str]) -> list[str]:
    return art


def render_plain(snapshot: UsageSnapshot, day: str, house_tokens: int) -> str:
    tokens = snapshot.by_day.get(day, 0)
    completed, remainder, progress = house_counts(tokens, house_tokens)
    lines = [
        "Codex Token Castles",
        f"Date: {day}",
        f"Today: {format_int(tokens)} tokens",
        f"Castles: {completed} complete, {format_int(remainder)}/{format_int(house_tokens)} tokens toward next",
        "",
    ]
    art = COMPLETE_HOUSE if completed else partial_house(progress)
    lines.extend(render_castle_plain(art))
    return "\n".join(lines)


def agent_title(agent: AgentUsage, disambiguate_main: bool = False) -> str:
    if disambiguate_main and not agent.is_subagent and agent.label == "Main":
        if agent.started_at:
            return f"Main {agent.started_at.strftime('%H:%M')}"
        return f"Main {agent.agent_id[-4:]}"
    if agent.role:
        return f"{agent.label} {agent.role}"
    return agent.label


def agent_root_id(agent_id: str, agents_by_id: dict[str, AgentUsage]) -> str:
    current = agent_id
    seen: set[str] = set()
    while current not in seen:
        seen.add(current)
        agent = agents_by_id.get(current)
        if not agent or not agent.parent_thread_id:
            return current
        current = agent.parent_thread_id
    return current


def selected_agents(snapshot: UsageSnapshot, day: str, all_castles: bool) -> list[AgentUsage]:
    agents = [agent for agent in snapshot.agents if agent.by_day.get(day, 0) > 0]
    if all_castles:
        selected = agents
    else:
        root_id = snapshot.latest_root_thread_id
        agents_by_id = {agent.agent_id: agent for agent in agents}
        selected = [
            agent
            for agent in agents
            if root_id is None or agent_root_id(agent.agent_id, agents_by_id) == root_id
        ]

    return sorted(
        selected,
        key=lambda agent: (
            agent.is_subagent,
            agent.label.lower(),
            agent.agent_id,
        ),
    )


def render_agents_plain(snapshot: UsageSnapshot, day: str, house_tokens: int, all_castles: bool) -> str:
    agents = selected_agents(snapshot, day, all_castles)
    scope = "all worker castles" if all_castles else "current crew"
    lines = [
        "Codex Token Castles",
        f"Date: {day}",
        f"View: {scope}",
    ]
    if not agents:
        lines.append("No token usage for this view.")
        return "\n".join(lines)

    for agent in agents:
        tokens = agent.by_day.get(day, 0)
        completed, remainder, _ = house_counts(tokens, house_tokens)
        lines.append(
            f"- {agent_title(agent, all_castles)}: {format_int(tokens)} tokens, {completed} castles + {format_int(remainder)}/{format_int(house_tokens)}"
        )
    return "\n".join(lines)


def addstr_safe(screen: curses.window, y: int, x: int, text: str, attr: int = 0) -> None:
    height, width = screen.getmaxyx()
    if y < 0 or y >= height or x >= width:
        return
    available = max(0, width - x - 1)
    if available:
        screen.addstr(y, x, text[:available], attr)


def setup_colors(enabled: bool = True, solid: bool = True) -> dict[str, int]:
    colors = {
        "enabled": 0,
        "solid": 1 if solid else 0,
        "title": curses.A_BOLD,
        "border": curses.A_DIM,
        "text": 0,
        "stone": 0,
        "stone_fill": 0,
        "flag": curses.A_BOLD,
        "window": curses.A_BOLD,
        "gate": curses.A_BOLD,
        "ground": curses.A_DIM,
        "progress": curses.A_BOLD,
        "muted": curses.A_DIM,
    }
    if not enabled:
        return colors
    try:
        if not curses.has_colors():
            return colors
        curses.start_color()
        try:
            curses.use_default_colors()
            background = -1
        except curses.error:
            background = curses.COLOR_BLACK

        def color(xterm: int, fallback: int) -> int:
            return xterm if curses.COLORS >= 256 else fallback

        stone_fill_bg = color(221, curses.COLOR_YELLOW) if solid else background
        ground_bg = color(34, curses.COLOR_GREEN) if solid else background

        pair_specs = {
            "text": (1, color(30, curses.COLOR_CYAN), background),
            "flag": (2, color(160, curses.COLOR_RED), background),
            "window": (3, color(214, curses.COLOR_YELLOW), background),
            "gate": (4, color(30, curses.COLOR_CYAN), background),
            "ground": (9, color(34, curses.COLOR_GREEN), ground_bg),
            "progress": (10, color(35, curses.COLOR_GREEN), background),
            "border": (11, color(30, curses.COLOR_CYAN), background),
            "stone": (12, color(221, curses.COLOR_YELLOW), background),
            "stone_fill": (13, color(236, curses.COLOR_BLACK), stone_fill_bg),
        }
        for _, (pair_id, foreground, pair_background) in pair_specs.items():
            curses.init_pair(pair_id, foreground, pair_background)

        colors.update(
            {
                "enabled": 1,
                "solid": 1 if solid else 0,
                "title": curses.color_pair(10) | curses.A_BOLD,
                "border": curses.color_pair(11),
                "text": curses.color_pair(1),
                "flag": curses.color_pair(2) | curses.A_BOLD,
                "window": curses.color_pair(3) | curses.A_BOLD,
                "gate": curses.color_pair(4) | curses.A_BOLD,
                "ground": curses.color_pair(9),
                "stone": curses.color_pair(12) | curses.A_BOLD,
                "stone_fill": curses.color_pair(13) if solid else curses.color_pair(12),
                "progress": curses.color_pair(10) | curses.A_BOLD,
                "muted": curses.A_DIM,
            }
        )
    except curses.error:
        return colors
    return colors


def addch_safe(screen: curses.window, y: int, x: int, char: str, attr: int = 0) -> None:
    height, width = screen.getmaxyx()
    if y < 0 or y >= height or x < 0 or x >= width - 1:
        return
    screen.addch(y, x, char, attr)


def castle_fill_ranges(text: str) -> list[tuple[int, int]]:
    non_space = [index for index, char in enumerate(text) if char != " "]
    if not non_space:
        return []
    if "|>>>" in text:
        return []
    if text.strip() and set(text.strip()) == {"|"}:
        return []
    if "...." in text or "____________________________" in text or "__________" in text:
        return [(non_space[0], non_space[-1])]

    ranges: list[tuple[int, int]] = []
    start = non_space[0]
    previous = non_space[0]
    for index in non_space[1:]:
        if index - previous > 8:
            ranges.append((start, previous))
            start = index
        previous = index
    ranges.append((start, previous))
    return ranges


def exact_ranges(text: str, needle: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            break
        ranges.append((index, index + len(needle) - 1))
        start = index + len(needle)
    return ranges


def in_ranges(index: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start <= index <= end for start, end in ranges)


def gate_ranges(text: str) -> list[tuple[int, int]]:
    ranges = exact_ranges(text, "____")
    gate_base = text.find("|__|    |__|")
    if gate_base != -1:
        ranges.append((gate_base + 3, gate_base + 10))
    return ranges


def draw_castle_line(
    screen: curses.window,
    y: int,
    x: int,
    text: str,
    colors: dict[str, int],
    base_attr: int = 0,
) -> None:
    fill_ranges = castle_fill_ranges(text)
    window_ranges = exact_ranges(text, "[]")
    gate_parts = gate_ranges(text)

    for column, char in enumerate(text):
        attr = base_attr
        draw_char = char
        if in_ranges(column, window_ranges):
            attr |= colors["window"]
        elif in_ranges(column, gate_parts):
            attr |= colors["gate"]
        elif char == ">" or ("|>>>" in text and char == "|"):
            attr |= colors["flag"]
        elif char == "." or "/_/" in text or "\\_\\" in text:
            attr |= colors["ground"]
        elif char == " " and in_ranges(column, fill_ranges):
            attr |= colors["stone_fill"]
        elif char != " ":
            attr |= colors["stone"]
        elif in_ranges(column, fill_ranges):
            attr |= colors["stone_fill"]

        addch_safe(screen, y, x + column, draw_char, attr)


def draw_house(
    screen: curses.window,
    y: int,
    x: int,
    art: list[str],
    attr: int = 0,
    colors: dict[str, int] | None = None,
) -> None:
    for row, text in enumerate(art):
        if colors:
            draw_castle_line(screen, y + row, x, text, colors, attr)
        else:
            addstr_safe(screen, y + row, x, text, attr)


def draw_box(
    screen: curses.window,
    y: int,
    x: int,
    width: int,
    height: int,
    title: str,
    colors: dict[str, int],
) -> None:
    if width < 4 or height < 3:
        return
    top = "+" + "-" * (width - 2) + "+"
    addstr_safe(screen, y, x, top, colors["border"])
    for row in range(1, height - 1):
        addstr_safe(screen, y + row, x, "|", colors["border"])
        addstr_safe(screen, y + row, x + width - 1, "|", colors["border"])
    addstr_safe(screen, y + height - 1, x, top, colors["border"])
    if title:
        addstr_safe(screen, y, x + 2, f" {title} ", colors["title"])


def draw_house_panel(
    screen: curses.window,
    y: int,
    x: int,
    width: int,
    title: str,
    art: list[str],
    caption: str,
    attr: int = 0,
    colors: dict[str, int] | None = None,
) -> None:
    colors = colors or setup_colors()
    house_width = max(len(line) for line in art)
    height = len(art) + 5
    draw_box(screen, y, x, width, height, title, colors)
    house_x = x + max(1, (width - house_width) // 2)
    house_y = y + 2
    draw_house(screen, house_y, house_x, art, attr, colors)
    caption_x = x + max(2, (width - len(caption)) // 2)
    addstr_safe(screen, y + height - 2, caption_x, caption, colors["progress"])


def last_days(day: str, count: int = 7) -> list[str]:
    today = datetime.strptime(day, "%Y-%m-%d").date()
    return [
        (today.toordinal() - offset)
        for offset in range(count - 1, -1, -1)
    ]


def ordinal_to_day(ordinal: int) -> str:
    return datetime.fromordinal(ordinal).strftime("%Y-%m-%d")


def draw_agents_tui(
    screen: curses.window,
    args: argparse.Namespace,
    snapshot: UsageSnapshot,
    day: str,
    colors: dict[str, int],
    animations: dict[str, BuildAnimation],
) -> None:
    now = time.monotonic()
    agents = selected_agents(snapshot, day, args.all_castles)
    actual_total = sum(agent.by_day.get(day, 0) for agent in agents)

    screen.erase()
    height, width = screen.getmaxyx()
    scope = "all worker castles" if args.all_castles else "current crew"
    addstr_safe(screen, 0, 0, "Codex Crew Castles", colors["title"])
    addstr_safe(
        screen,
        1,
        0,
        f"{day}  {scope}  {len(agents)} castles  actual {format_int(actual_total)} tokens",
        colors["text"],
    )
    addstr_safe(
        screen,
        2,
        0,
        f"Each panel is one worker castle    scanned {snapshot.scanned_at.strftime('%H:%M:%S')}    q to quit",
        colors["muted"],
    )
    if snapshot.latest_event_time:
        addstr_safe(
            screen,
            3,
            0,
            f"Last event: {snapshot.latest_event_time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
            colors["muted"],
        )

    if not agents:
        addstr_safe(screen, 5, 0, "No token usage found for this view yet.", colors["muted"])
        return

    panel_top = 5
    panel_height = len(COMPLETE_HOUSE) + 5
    art_width = max(len(line) for line in COMPLETE_HOUSE)
    min_panel_width = art_width + 2
    gap = 3
    columns = 1
    if width >= min_panel_width * 3 + gap * 2:
        columns = 3
    elif width >= min_panel_width * 2 + gap:
        columns = 2
    panel_width = max(min_panel_width, (width - gap * (columns - 1)) // columns)
    panel_width = min(44, panel_width)

    visible = 0
    for index, agent in enumerate(agents):
        row = index // columns
        column = index % columns
        y = panel_top + row * (panel_height + 1)
        x = column * (panel_width + gap)
        if y + panel_height >= height:
            break

        target_tokens = agent.by_day.get(day, 0)
        display_tokens = int(
            animations.setdefault(agent.agent_id, BuildAnimation()).update(
                target_tokens,
                args.house_tokens,
                args.seconds_per_house,
                now,
            )
        )
        completed, remainder, progress = house_counts(display_tokens, args.house_tokens)
        title = agent_title(agent, args.all_castles)
        caption = f"* {completed}  {int(progress * 100):3d}%"
        draw_house_panel(
            screen,
            y,
            x,
            panel_width,
            title,
            partial_house(progress),
            caption,
            curses.A_DIM if remainder == 0 else 0,
            colors=colors,
        )
        detail = f"{format_int(target_tokens)} tokens"
        addstr_safe(screen, y + panel_height - 3, x + 2, detail, colors["muted"])
        visible += 1

    if visible < len(agents):
        addstr_safe(screen, height - 2, 0, f"+ {len(agents) - visible} more castles", colors["muted"])


def draw_tui(screen: curses.window, args: argparse.Namespace) -> None:
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    screen.nodelay(True)
    colors = setup_colors(not args.no_color, args.solid)
    tracker = UsageTracker(args.codex_home)
    animation = BuildAnimation()
    agent_animations: dict[str, BuildAnimation] = {}

    while True:
        snapshot = tracker.scan()
        day = args.date or datetime.now().strftime("%Y-%m-%d")
        if args.crew:
            draw_agents_tui(screen, args, snapshot, day, colors, agent_animations)
            screen.refresh()
            key = screen.getch()
            if key in (ord("q"), ord("Q"), 27):
                break
            time.sleep(args.refresh)
            continue

        target_tokens = snapshot.by_day.get(day, 0)
        now = time.monotonic()
        display_tokens = int(
            animation.update(
                target_tokens,
                args.house_tokens,
                args.seconds_per_house,
                now,
            )
        )
        completed, remainder, progress = house_counts(display_tokens, args.house_tokens)
        pending_tokens = max(0, target_tokens - display_tokens)

        screen.erase()
        height, width = screen.getmaxyx()
        title_attr = colors["title"]

        addstr_safe(screen, 0, 0, "Codex Token Castles", title_attr)
        addstr_safe(
            screen,
            1,
            0,
            f"{day}  actual {format_int(target_tokens)} tokens  |  building {format_int(display_tokens)} tokens",
            colors["text"],
        )
        addstr_safe(
            screen,
            2,
            0,
            f"{completed} castles + {format_int(remainder)}/{format_int(args.house_tokens)}  {progress_bar(progress)} {int(progress * 100):3d}% of next castle",
            colors["progress"],
        )
        addstr_safe(
            screen,
            3,
            0,
            f"Queued build: {format_int(pending_tokens)} tokens    latest session: {format_int(snapshot.latest_session_tokens)}    scanned {snapshot.scanned_at.strftime('%H:%M:%S')}    q to quit",
            colors["muted"],
        )

        if snapshot.latest_event_time:
            addstr_safe(
                screen,
                4,
                0,
                f"Last event: {snapshot.latest_event_time.strftime('%Y-%m-%d %H:%M:%S %Z')}",
                colors["muted"],
            )

        summary_parts = []
        for ordinal in last_days(day):
            item_day = ordinal_to_day(ordinal)
            day_tokens = snapshot.by_day.get(item_day, 0)
            day_castles = day_tokens // args.house_tokens
            summary_parts.append(f"{item_day[5:]}:{day_castles}")
        addstr_safe(
            screen,
            6,
            0,
            "Last 7 days castles " + "  ".join(summary_parts),
            colors["text"],
        )

        panel_top = 8
        panel_height = len(COMPLETE_HOUSE) + 5
        art_width = max(len(line) for line in COMPLETE_HOUSE)
        min_panel_width = art_width + 2
        if width >= min_panel_width * 2 + 3:
            panel_width = min(44, (width - 3) // 2)
            draw_house_panel(
                screen,
                panel_top,
                0,
                panel_width,
                "Completed",
                COMPLETE_HOUSE,
                f"* {completed}",
                colors=colors,
            )
            draw_house_panel(
                screen,
                panel_top,
                panel_width + 3,
                panel_width,
                "Now Building",
                partial_house(progress),
                f"{int(progress * 100):3d}%",
                curses.A_DIM if remainder == 0 else 0,
                colors=colors,
            )
        else:
            panel_width = max(min_panel_width, width - 1)
            draw_house_panel(
                screen,
                panel_top,
                0,
                panel_width,
                "Completed",
                COMPLETE_HOUSE,
                f"* {completed}",
                colors=colors,
            )
            if panel_top + panel_height + 1 < height:
                draw_house_panel(
                    screen,
                    panel_top + panel_height + 1,
                    0,
                    panel_width,
                    "Now Building",
                    partial_house(progress),
                    f"{int(progress * 100):3d}%",
                    curses.A_DIM if remainder == 0 else 0,
                    colors=colors,
                )

        screen.refresh()
        key = screen.getch()
        if key in (ord("q"), ord("Q"), 27):
            break
        time.sleep(args.refresh)


def open_terminal_window(argv: list[str]) -> int:
    script = Path(__file__).resolve()
    forwarded = [arg for arg in argv if arg != "--window"]
    command = " ".join([shell_quote(sys.executable), shell_quote(str(script)), *map(shell_quote, forwarded)])
    apple_script = f'tell application "Terminal" to do script {json.dumps(command)}'
    subprocess.run(["osascript", "-e", apple_script], check=False)
    return 0


def shell_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codehouse",
        description="Show local Codex token usage as castles.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser(),
        help="Codex home directory. Defaults to CODEX_HOME or ~/.codex.",
    )
    parser.add_argument(
        "--date",
        help="Day to show in YYYY-MM-DD. Defaults to today in the local timezone.",
    )
    parser.add_argument(
        "--castle-tokens",
        "--house-tokens",
        dest="house_tokens",
        type=int,
        default=None,
        help=f"Tokens required for one complete castle. Defaults to {DEFAULT_HOUSE_TOKENS}.",
    )
    parser.add_argument(
        "--scale",
        choices=sorted(SCALE_HOUSE_TOKENS),
        default="normal",
        help="Castle size preset. Defaults to normal.",
    )
    parser.add_argument(
        "--refresh",
        type=float,
        default=DEFAULT_REFRESH_SECONDS,
        help=f"Refresh interval in seconds. Defaults to {DEFAULT_REFRESH_SECONDS:g}.",
    )
    parser.add_argument(
        "--seconds-per-castle",
        "--seconds-per-house",
        dest="seconds_per_house",
        type=float,
        default=None,
        help=f"Animation speed for newly detected tokens. Defaults to {DEFAULT_SECONDS_PER_HOUSE:g} seconds per castle.",
    )
    parser.add_argument(
        "--pace",
        choices=sorted(PACE_SECONDS_PER_HOUSE),
        default="normal",
        help="Animation pace preset. Defaults to normal.",
    )
    parser.add_argument("--once", action="store_true", help="Print one snapshot and exit.")
    parser.add_argument(
        "--crew",
        action="store_true",
        help="Show one castle per worker in the current Codex crew.",
    )
    parser.add_argument(
        "-all",
        dest="all_castles",
        action="store_true",
        help="Show every worker/session castle for the selected day.",
    )
    parser.add_argument("--all-castles", dest="all_castles", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--agents", dest="crew", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--all-agents", dest="all_castles", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--window",
        action="store_true",
        help="Open the TUI in a separate macOS Terminal window.",
    )
    parser.add_argument("--no-color", action="store_true", help="Disable TUI colors.")
    parser.add_argument(
        "--no-solid",
        action="store_false",
        dest="solid",
        help="Use colored outlines without solid castle fills.",
    )
    parser.set_defaults(solid=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.house_tokens is None:
        args.house_tokens = SCALE_HOUSE_TOKENS[args.scale]
    if args.house_tokens <= 0:
        parser.error("--castle-tokens must be greater than 0")
    if args.refresh <= 0:
        parser.error("--refresh must be greater than 0")
    if args.seconds_per_house is None:
        args.seconds_per_house = PACE_SECONDS_PER_HOUSE[args.pace]
    if args.seconds_per_house <= 0:
        parser.error("--seconds-per-castle must be greater than 0")
    if args.all_castles:
        args.crew = True
    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            parser.error("--date must use YYYY-MM-DD")

    if args.window:
        return open_terminal_window(argv)

    if args.once or not sys.stdout.isatty():
        day = args.date or datetime.now().strftime("%Y-%m-%d")
        snapshot = scan_usage(args.codex_home)
        if args.crew:
            print(render_agents_plain(snapshot, day, args.house_tokens, args.all_castles))
        else:
            print(render_plain(snapshot, day, args.house_tokens))
        return 0

    curses.wrapper(draw_tui, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
