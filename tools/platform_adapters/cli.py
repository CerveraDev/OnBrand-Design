from __future__ import annotations

import argparse
from pathlib import Path

from .contract import PLATFORMS, run, write_json
from .install import install
from .parity import evaluate


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explicit OnBrand platform adapters")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "emit", "parity"):
        command = commands.add_parser(name)
        command.add_argument("--request", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--explicit", action="store_true", help="HUMAN invocation attestation")
        if name == "parity":
            command.add_argument("--cache-package", type=Path)
        else:
            command.add_argument("--platform", choices=PLATFORMS, required=True)
    command = commands.add_parser("install")
    command.add_argument("--project", required=True)
    command.add_argument("--platform", choices=("codex", "claude"), required=True)
    command.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "install":
            for path in install(args.project, args.platform, args.workspace):
                print(path)
        elif args.command == "parity":
            report = evaluate(args.request, args.output, explicit=args.explicit, cache_package=args.cache_package)
            write_json(args.output / "parity-report.json", report)
            print(f"Parity passed={report['passed']} aggregate={report['aggregate_score']}")
            return 0 if report["passed"] else 4
        else:
            result = run(args.request, args.platform, args.output, explicit=args.explicit, build=args.command == "build")
            print(result.package_dir if result else args.output / "campaign.runtime.json")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"Adapter failed: {exc}")
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
