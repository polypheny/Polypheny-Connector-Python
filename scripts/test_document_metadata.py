#!/usr/bin/env python3
"""Generate companion Prism Python bindings and run the live metadata tests.

The generated bindings live in a temporary directory. This neither overwrites
the installed Prism package nor changes the connector's release dependencies.
"""

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prism-api", required=True, type=Path, help="Checkout of the companion Polypheny-Prism-API revision")
    parser.add_argument("--mongo", action="store_true", help="Also test indexes using a live MongoDB replica set")
    arguments = parser.parse_args()
    api_root = arguments.prism_api.resolve()
    namespace_proto = api_root / "org/polypheny/prism/namespace_meta_responses.proto"
    if not namespace_proto.is_file():
        parser.error("--prism-api must contain org/polypheny/prism/namespace_meta_responses.proto")

    connector_root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="prism-document-metadata-") as output:
        subprocess.run([
            sys.executable, "-m", "grpc_tools.protoc", "-I", str(api_root),
            "--python_out", output,
            str(namespace_proto),
        ], check=True)
        # Overlay only this additive metadata module. Other definitions on the
        # API's main branch may differ from the released 1.9 wire protocol;
        # value serialization and version negotiation keep using that release.

        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(filter(None, [
            output, str(connector_root), environment.get("PYTHONPATH"),
        ]))
        tests = ["tests/document_metadata.py"]
        if arguments.mongo:
            tests.append("tests/document_metadata_mongo.py")
        return subprocess.call(
            [sys.executable, "-m", "pytest", "-v", *tests],
            cwd=connector_root, env=environment,
        )


if __name__ == "__main__":
    raise SystemExit(main())
