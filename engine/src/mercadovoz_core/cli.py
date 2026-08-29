from __future__ import annotations

import argparse
import json
from datetime import timedelta

from .api import MercadoVozCore
from .context import ContextSession


def _print(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="mercadovoz-core")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parse_command = subparsers.add_parser("parse", aliases=["interpret"])
    parse_command.add_argument("text")

    session_command = subparsers.add_parser("session")
    session_command.add_argument("text")
    session_command.add_argument(
        "--context",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Explicit context value; repeat for more keys.",
    )

    correct_command = subparsers.add_parser("correct")
    correct_command.add_argument("text")
    correct_command.add_argument("correction")

    confirm_command = subparsers.add_parser("confirm")
    confirm_command.add_argument("text")
    confirm_command.add_argument("--idempotency-key", required=True)

    reject_command = subparsers.add_parser("reject")
    reject_command.add_argument("text")
    reject_command.add_argument("--reason", required=True)

    args = parser.parse_args()
    core = MercadoVozCore()

    if args.command in {"parse", "interpret"}:
        _print(core.interpret(args.text))
        return
    if args.command == "session":
        context = ContextSession()
        for item in args.context:
            if "=" not in item:
                parser.error("--context must use KEY=VALUE")
            key, value = item.split("=", 1)
            context.set(key, value, source="cli_explicit", ttl=timedelta(minutes=15))
        _print(core.interpret(args.text, context))
        return

    proposal = core.propose(args.text)
    proposal_id = proposal["proposal_id"]
    if args.command == "correct":
        _print(core.correct(proposal_id, args.correction))
    elif args.command == "confirm":
        _print(core.confirm(proposal_id, args.idempotency_key))
    else:
        _print(core.reject(proposal_id, args.reason))


if __name__ == "__main__":
    main()
