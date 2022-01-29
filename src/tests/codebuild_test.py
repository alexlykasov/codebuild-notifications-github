import unittest
from unittest.mock import patch

from common.codebuild import CodeBuild
from common.exceptions import CodeBuildProjectNotFound


class CodebuildTest(unittest.TestCase):

    @patch('common.codebuild.client')
    def test_project_fetched(self, codebuild_client):
        project_id = '1234-34556-1223-1234'
        project_name = 'project-name'

        codebuild_client.batch_get_projects.return_value = {
            'projects': [{
                    'id': project_id
                }
            ]
        }

        cb = CodeBuild(project_name)

        codebuild_client.batch_get_projects.assert_called_with(names=[project_name])
        self.assertEqual(project_id, cb.project['id'])

    @patch('common.codebuild.client')
    def test_project_fetch_failed(self, codebuild_client):
        codebuild_client.batch_get_projects.return_value = {
            'projects': []
        }
        self.assertRaises(CodeBuildProjectNotFound, lambda: CodeBuild('test'))

    @patch('common.codebuild.client')
    @patch('common.codebuild.CodeBuild._fetch_project')
    def test_start_build(self, _fetch_project, codebuild_client):
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

        cb = CodeBuild(project_name)
        cb_build_id = cb.start_build('1', 'commit-sha')

        self.assertEqual(build_id, cb_build_id)
        codebuild_client.start_build.assert_called_with(
            projectName=project_name,
            artifactsOverride={'type': 'NO_ARTIFACTS'},
            sourceVersion=f'pr/1',
            environmentVariablesOverride=[
                {
                    'name': 'GIT_PR',
                    'value': '1',
                    'type': 'PLAINTEXT',
                },
                {
                    'name': 'GIT_COMMIT',
                    'value': 'commit-sha',
                    'type': 'PLAINTEXT',
                }
            ],
            buildspecOverride='prcheck-buildspec.yaml'
        )
