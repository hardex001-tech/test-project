import argparse
import logging
from pathlib import Path

from stealth_scan.scanner import (
    configure_logging,
    run_cewl,
    run_nmap_scan,
    validate_formats,
    write_outputs,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Stealthy port scanning tool for ethical hacking labs.",
    )
    parser.add_argument("target", help="Target IP/range (e.g., 172.16.0.5 or 172.16.0.0/24)")
    parser.add_argument(
        "--output-dir",
        default="samples",
        help="Directory for scan outputs (default: samples)",
    )
    parser.add_argument(
        "--formats",
        nargs="+",
        default=["csv", "json", "html"],
        help="Output formats: csv json html (default: all)",
    )
    parser.add_argument(
        "--cewl-url",
        help="Optional web URL to crawl with CeWL for custom wordlists.",
    )
    parser.add_argument(
        "--cewl-output",
        help="Output path for CeWL wordlist (default: <output-dir>/cewl_wordlist.txt)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        help="Logging level (default: INFO)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    configure_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        formats = validate_formats(args.formats)
        output_dir = Path(args.output_dir)
        if args.cewl_url:
            cewl_output = (
                Path(args.cewl_output)
                if args.cewl_output
                else output_dir / "cewl_wordlist.txt"
            )
            run_cewl(args.cewl_url, cewl_output, logger)

        results = run_nmap_scan(args.target, logger)
        written = write_outputs(results, output_dir, formats)
    except Exception as exc:
        logger.error("Scan failed: %s", exc)
        return 1

    for path in written:
        logger.info("Wrote %s", path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
