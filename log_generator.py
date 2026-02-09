#!/usr/bin/env python3
"""Generate large log files that mimic application log formats."""

from __future__ import annotations

import argparse
import os
import random
import sys
from datetime import datetime, timezone
from typing import Iterable

DEFAULT_LEVELS = ["DEBUG", "INFO", "WARN", "ERROR"]
DEFAULT_LOGGERS = ["app", "worker", "db", "api"]
DEFAULT_USERS = ["alice", "bob", "carol", "dave"]
DEFAULT_MESSAGES = [
    "Starting up",
    "User authenticated",
    "Processing request",
    "Cache miss",
    "Cache hit",
    "Database query completed",
    "Background job enqueued",
    "Retrying request",
    "Request completed",
    "Shutting down",
]

DEFAULT_TEMPLATE = "{timestamp} [{level}] {logger} ({pid}:{thread}) {message}"


def parse_size(size_str: str) -> int:
    units = {
        "b": 1,
        "kb": 1024,
        "mb": 1024**2,
        "gb": 1024**3,
    }
    raw = size_str.strip().lower()
    for suffix, multiplier in units.items():
        if raw.endswith(suffix):
            number = raw[: -len(suffix)].strip()
            if not number:
                raise ValueError(f"Invalid size: {size_str}")
            return int(float(number) * multiplier)
    return int(raw)


def load_lines(path: str | None, fallback: Iterable[str]) -> list[str]:
    if not path:
        return list(fallback)
    with open(path, "r", encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def generate_line(template: str, rng: random.Random, ctx: dict[str, str]) -> str:
    ctx = dict(ctx)
    ctx["level"] = rng.choice(ctx["levels"]).upper()
    ctx["logger"] = rng.choice(ctx["loggers"])
    ctx["message"] = rng.choice(ctx["messages"])
    ctx["user"] = rng.choice(ctx["users"])
    ctx["thread"] = str(rng.randint(1, 128))
    ctx["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return template.format_map(ctx)


def write_logs(
    output_path: str,
    template: str,
    line_count: int | None,
    size_bytes: int | None,
    seed: int | None,
    levels: list[str],
    loggers: list[str],
    messages: list[str],
    users: list[str],
) -> None:
    rng = random.Random(seed)
    pid = str(os.getpid())
    context = {
        "pid": pid,
        "levels": levels,
        "loggers": loggers,
        "messages": messages,
        "users": users,
    }

    bytes_written = 0
    lines_written = 0

    with open(output_path, "w", encoding="utf-8") as handle:
        while True:
            if line_count is not None and lines_written >= line_count:
                break
            if size_bytes is not None and bytes_written >= size_bytes:
                break

            line = generate_line(template, rng, context)
            payload = f"{line}\n"
            handle.write(payload)
            bytes_written += len(payload.encode("utf-8"))
            lines_written += 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        required=True,
        help="Path to write the generated log file.",
    )
    size_group = parser.add_mutually_exclusive_group(required=True)
    size_group.add_argument(
        "-n",
        "--lines",
        type=int,
        help="Number of log lines to generate.",
    )
    size_group.add_argument(
        "-s",
        "--size",
        help="Target log size (e.g. 500MB, 2GB, 1000000).",
    )
    parser.add_argument(
        "-t",
        "--template",
        default=DEFAULT_TEMPLATE,
        help=(
            "Log format template using fields: timestamp, level, logger, "
            "pid, thread, message, user."
        ),
    )
    parser.add_argument(
        "--levels",
        help="Optional newline-delimited file of log levels.",
    )
    parser.add_argument(
        "--loggers",
        help="Optional newline-delimited file of logger names.",
    )
    parser.add_argument(
        "--messages",
        help="Optional newline-delimited file of messages.",
    )
    parser.add_argument(
        "--users",
        help="Optional newline-delimited file of usernames.",
    )
    parser.add_argument("--seed", type=int, help="Seed for deterministic output.")
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        size_bytes = parse_size(args.size) if args.size else None
    except ValueError as exc:
        parser.error(str(exc))
        return 2

    levels = load_lines(args.levels, DEFAULT_LEVELS)
    loggers = load_lines(args.loggers, DEFAULT_LOGGERS)
    messages = load_lines(args.messages, DEFAULT_MESSAGES)
    users = load_lines(args.users, DEFAULT_USERS)

    write_logs(
        output_path=args.output,
        template=args.template,
        line_count=args.lines,
        size_bytes=size_bytes,
        seed=args.seed,
        levels=levels,
        loggers=loggers,
        messages=messages,
        users=users,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
