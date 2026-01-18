# uv run --directory backend python -m tools.get_logs --groupid group1 | jq .

import argparse
import json
import logging

from app.config import settings
from app.services.log_service import LogsService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main(groupid: str) -> None:
    service = LogsService()
    result = service.list_logs(groupid=groupid)
    if result.data is None:
        logger.error(f"No logs found for groupid={groupid}")
        return
    print(json.dumps(result.data.items, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch logs for a given group ID.")
    parser.add_argument("--groupid", required=True, help="Group ID to fetch logs for")
    args = parser.parse_args()

    logger.info(f"ENV: {settings.ENV}")
    logger.info(f"DYNAMODB_ENDPOINT: {settings.DYNAMODB_ENDPOINT}")

    main(args.groupid)
