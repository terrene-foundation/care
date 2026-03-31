"""CLI entrypoint for CARE Assessment Kit."""

from __future__ import annotations

import sys


def main() -> None:
    """Launch the CARE API server."""
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install care-assessment-kit")
        sys.exit(1)

    from care.config import load_config

    config = load_config()
    uvicorn.run(
        "care.api.server:app",
        host=config.server.host,
        port=config.server.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
