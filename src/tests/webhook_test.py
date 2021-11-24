import json
import unittest
from unittest.mock import patch

from handlers import webhook_handler
from tests.data.lambda_responses import LAMBDA_EVENT_PR_CREATED


class WebhookTest(unittest.TestCase):

    @patch('common.codebuild.client')
    @patch('common.codebuild.CodeBuild._fetch_project')
    @patch('webhook.process.GitHubApp')
    def test_project_fetched(self, githubapp, _fetch_project, codebuild_client):
        githubapp.pending.return_value = None
        project_name = 'test-project'
        _fetch_project.return_value = {
            'name': project_name
        }
        build_id = '623565'
        codebuild_client.start_build.return_value = {
            'build': {
                'id': build_id
            }
        }

        commit_sha = json.loads(LAMBDA_EVENT_PR_CREATED['body'])['pull_request']['head']['sha']

        response = webhook_handler(LAMBDA_EVENT_PR_CREATED)

        githubapp.assert_called_with(repo_full_name='UserName/test-project',
                                     pr_id=1,
                                     build_id='623565',
                                     build_project_name='test-project')
        githubapp.return_value.pending.assert_called_with(commit_sha)

        self.assertEqual(200, response['statusCode'])
        self.assertEqual('application/json', response['headers']['content-type'])
