# uv run --directory backend python -m tools.get_users | jq .

import json
import logging

from app.config import settings
from app.services.user_service import UsersService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    result = UsersService().list_users()
    if result.data is None:
        logger.error("No data returned from list_users")
        return
    data = result.data.items
    print(json.dumps(data, indent=2))


if __name__ == "__main__":
    logger.info(f"ENV: {settings.ENV}")
    logger.info(f"DYNAMODB_ENDPOINT: {settings.DYNAMODB_ENDPOINT}")

    main()
