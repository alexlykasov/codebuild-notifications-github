import json
from typing import Dict, List

from settings import logger
from webhook.process import start_codebuild_build
from cloudwatchevent.process import watch_codebuild_state_change
from common import awslambda


def webhook_handler(event: Dict, *args: List, **kwargs: Dict) -> Dict:
    logger.debug('Received new lambda event')
    api_gateway_request_body = json.loads(event['body'])
    return awslambda.lambda_response(start_codebuild_build, api_gateway_request_body)


def codebuild_event_handler(event: Dict, *args: List, **kwargs: Dict) -> None:
    logger.debug('Received new lambda event')
    watch_codebuild_state_change(event)
