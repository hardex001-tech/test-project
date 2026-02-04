import csv
import json
import logging
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, List, Optional

DEFAULT_NMAP_SCRIPTS = "rdp-vuln-ms12-020,vnc-info"
DEFAULT_NMAP_ARGS = f"-sS -Pn -sV --script {DEFAULT_NMAP_SCRIPTS}"


@dataclass
class ScanResult:
    host: str
    status: str
    protocol: str
    port: int
    state: str
    name: str
    product: str
    version: str
    extrainfo: str
    script_output: str


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def run_cewl(url: str, output_path: Path, logger: logging.Logger) -> None:
    logger.info("Generating CeWL wordlist from %s", url)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(
            ["cewl", "--lowercase", "-w", str(output_path), url],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("CeWL is not installed or not on PATH.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"CeWL failed: {exc.stderr.strip()}") from exc


def run_nmap_scan(targets: str, logger: logging.Logger) -> List[ScanResult]:
    logger.info("Starting nmap scan against %s", targets)
    try:
        import nmap  # type: ignore
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "python-nmap is not installed. Install dependencies with "
            "`pip install -r requirements.txt`."
        ) from exc

    scanner = nmap.PortScanner()
    try:
        scanner.scan(hosts=targets, arguments=DEFAULT_NMAP_ARGS)
    except nmap.PortScannerError as exc:
        raise RuntimeError(f"Nmap scan failed: {exc}") from exc

    results: List[ScanResult] = []
    for host in scanner.all_hosts():
        host_state = scanner[host].state()
        for proto in scanner[host].all_protocols():
            ports = scanner[host][proto].keys()
            for port in ports:
                port_data = scanner[host][proto][port]
                script_output = json.dumps(port_data.get("script", {}))
                results.append(
                    ScanResult(
                        host=host,
                        status=host_state,
                        protocol=proto,
                        port=int(port),
                        state=port_data.get("state", ""),
                        name=port_data.get("name", ""),
                        product=port_data.get("product", ""),
                        version=port_data.get("version", ""),
                        extrainfo=port_data.get("extrainfo", ""),
                        script_output=script_output,
                    )
                )
    logger.info("Scan complete: %s results", len(results))
    return results


def write_json(results: Iterable[ScanResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump([asdict(result) for result in results], handle, indent=2)


def write_csv(results: Iterable[ScanResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_list = list(results)
    fieldnames = [field.name for field in ScanResult.__dataclass_fields__.values()]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results_list:
            writer.writerow(asdict(result))


def write_html(results: Iterable[ScanResult], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = "\n".join(
        [
            "<tr>"
            + "".join(f"<td>{getattr(result, field)}</td>" for field in ScanResult.__dataclass_fields__)
            + "</tr>"
            for result in results
        ]
    )
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <title>Stealth Scan Results</title>
  <style>
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ccc; padding: 6px; text-align: left; }}
    th {{ background: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>Stealth Scan Results</h1>
  <table>
    <thead>
      <tr>
        {''.join(f"<th>{field}</th>" for field in ScanResult.__dataclass_fields__)}
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
</body>
</html>
"""
    output_path.write_text(html, encoding="utf-8")


def write_outputs(results: List[ScanResult], output_dir: Path, formats: Iterable[str]) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    for fmt in formats:
        if fmt == "json":
            path = output_dir / "scan_results.json"
            write_json(results, path)
        elif fmt == "csv":
            path = output_dir / "scan_results.csv"
            write_csv(results, path)
        elif fmt == "html":
            path = output_dir / "scan_results.html"
            write_html(results, path)
        else:
            raise ValueError(f"Unsupported format: {fmt}")
        written.append(path)
    return written


def validate_formats(formats: Iterable[str]) -> List[str]:
    normalized = [fmt.lower() for fmt in formats]
    allowed = {"csv", "json", "html"}
    for fmt in normalized:
        if fmt not in allowed:
            raise ValueError(f"Unsupported format: {fmt}")
    return normalized


__all__ = [
    "DEFAULT_NMAP_ARGS",
    "DEFAULT_NMAP_SCRIPTS",
    "ScanResult",
    "configure_logging",
    "run_cewl",
    "run_nmap_scan",
    "write_outputs",
    "validate_formats",
]
