import json
import unittest
from unittest.mock import patch

from cloudwatchevent.process import _repo_url_to_full_name, _get_env_value, watch_codebuild_state_change
from common.exceptions import RequiredEnvVarsNotSet, UnsupportedBuildStatus


CODEBUILD_BUILD_INFO = {
            'detail': {
                'additional-information': {
                    'environment': {
                        'environment-variables': [
                            {
                                'name': 'test1',
                                'value': 'value1'
                            },
                            {
                                'name': 'test2',
                                'value': 'value3'
                            }
                        ]
                    }
                }
            }
        }


class CwEventHandlerTest(unittest.TestCase):

    def test__repo_url_to_full_name(self):
        url = 'https://github.com/UserName/test-codebuild.git'
        repo = _repo_url_to_full_name(url)
        self.assertEqual('UserName/test-codebuild', repo)

    def test__get_env_value(self):
        value = _get_env_value('test1', CODEBUILD_BUILD_INFO)
        self.assertEqual('value1', value)

    def test__get_env_value_failure(self):
        self.assertRaises(RequiredEnvVarsNotSet, lambda: _get_env_value('un-existent', CODEBUILD_BUILD_INFO))

    @patch('cloudwatchevent.process.GitHubApp')
    def test_watch_codebuild_state_change(self, githubapp):
        with open('src/tests/data/cw-event-build-failed.json') as f:
            cw_event = json.loads(f.read())

        watch_codebuild_state_change(cw_event)

        githubapp.assert_called_with(repo_full_name='UserName/test-codebuild',
                                     build_id='c9d89e33-107d-4213-aa56-9e411d88ec3c',
                                     build_project_name='codebuild-evaluation',
                                     pr_id=1)
        githubapp.return_value.failure.assert_called_with('5a892213349f7d78497f6db3479711936908147a')

    def test_watch_codebuild_state_change_unsupported(self):
        with open('src/tests/data/cw-event-build-unsupported.json') as f:
            cw_event = json.loads(f.read())

        self.assertRaises(UnsupportedBuildStatus, lambda: watch_codebuild_state_change(cw_event))
