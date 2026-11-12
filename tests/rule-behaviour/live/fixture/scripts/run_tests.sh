#!/bin/bash
# Run the whole suite verbosely, as CI does. Extra arguments go to unittest.
cd "$(dirname "$0")/.." && exec python3 -m unittest -v "$@"
