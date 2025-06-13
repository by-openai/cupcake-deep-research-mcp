import json
import logging
from pathlib import Path
from fastmcp.server import FastMCP

RECORDS = json.loads(Path(__file__).with_name("records.json").read_text())
LOOKUP = {r["id"]: r for r in RECORDS}

logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


def create_server():
    mcp = FastMCP(name="Cupcake MCP", instructions="Search cupcake orders", log_level="DEBUG")

    @mcp.tool()
    async def search(query: str, top_n: int = 10, recency_days: int | None = None):
        """
        Search for cupcake orders – keyword match.
        """
        logger.info(f"SEARCH {query=}")
        toks = query.lower().split()
        ids = []
        for r in RECORDS:
            hay = " ".join(
                [
                    r.get("title", ""),
                    r.get("text", ""),
                    " ".join(r.get("metadata", {}).values()),
                ]
            ).lower()
            if any(t in hay for t in toks):
                ids.append(r["id"])
        return {"results": [{"id": i} for i in ids]}

    @mcp.tool()
    async def fetch(id: str):
        """
        Fetch a cupcake order by ID.
        """
        logger.info(f"FETCH {id=}")
        if id not in LOOKUP:
            raise ValueError("unknown id")
        return LOOKUP[id]

    return mcp


if __name__ == "__main__":
    create_server().run(transport="sse", host="127.0.0.1", port=8090, log_level="DEBUG")
