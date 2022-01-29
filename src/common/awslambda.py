import traceback
from typing import Dict, Callable

from settings import logger
from common.exceptions import CodeBuildProjectNotFound


def lambda_response(function: Callable, request: Dict) -> Dict:
    http_status_code = 200
    try:
        function(request)
    except CodeBuildProjectNotFound as e:
        logger.debug(str(e))
        http_status_code = 404
    except Exception:
        http_status_code = 500
        traceback.print_exc()
    return {
        'statusCode': http_status_code,
        'headers': {
            'content-type': 'application/json'
        },
        'body': '',
    }
