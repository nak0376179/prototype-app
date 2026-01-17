# python3 tools/get_users.py | jq .

import json
import logging

from app.config import settings
from app.services.user_service import UsersService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    result = UsersService().list_users()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    logger.info(f"ENV: {settings.ENV}")
    logger.info(f"DYNAMODB_ENDPOINT: {settings.DYNAMODB_ENDPOINT}")

    main()
