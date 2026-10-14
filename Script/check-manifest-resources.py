#!/usr/bin/env python3
"""Keep the runtime resources in release and local SwiftPM manifests in sync."""

from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parent.parent
manifests = ("Package.swift", "Package.local.swift", "Package.swift.template")
expected = None

for name in manifests:
    content = (root / name).read_text()
    target = re.search(
        r'\.target\(\s*name: "GhosttyTerminal",.*?resources:\s*\[(.*?)\]',
        content,
        re.DOTALL,
    )
    if target is None:
        sys.exit(f"[-] {name}: GhosttyTerminal resources not found")
    resources = re.findall(r'\.(copy|process)\("([^"]+)"\)', target.group(1))
    required = {("copy", "Resources/Ghostty"), ("copy", "Resources/terminfo")}
    if not required.issubset(resources):
        sys.exit(f"[-] {name}: Ghostty and terminfo must both be copied")
    if len(resources) != len(set(resources)):
        sys.exit(f"[-] {name}: duplicate runtime resources")
    if expected is None:
        expected = set(resources)
    elif set(resources) != expected:
        sys.exit(f"[-] {name}: runtime resources differ from Package.swift")
    for _, path in resources:
        if not (root / "Sources/GhosttyTerminal" / path).exists():
            sys.exit(f"[-] {name}: missing resource {path}")

for path in (
    "Ghostty/shell-integration/zsh/ghostty-integration",
    "terminfo/78/xterm-ghostty",
    "terminfo/67/ghostty",
):
    if not (root / "Sources/GhosttyTerminal/Resources" / path).is_file():
        sys.exit(f"[-] required runtime resource is missing: {path}")

print("[+] runtime resources match in all three manifests")
