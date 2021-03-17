import os
import sys
import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG, handlers=[logging.StreamHandler(sys.stdout)])
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('github.Requester').setLevel(logging.INFO)

logger = logging.getLogger()

load_dotenv()


REGION = os.getenv('REGION')

SM_PARAMETER_ACCESS_TOKEN = "codebuild-access-token"
