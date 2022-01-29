from typing import Dict

import boto3

from common.exceptions import CodeBuildProjectNotFound


client = boto3.client('codebuild')


class CodeBuild:

    def __init__(self, project_name: str) -> None:
        self.project = self._fetch_project(project_name)

    def _fetch_project(self, name: str) -> Dict:
        """
        Fetches CodeBuild project by name

        :param name:
        :return:
        """
        response = client.batch_get_projects(names=[name])
        if not response['projects']:
            raise CodeBuildProjectNotFound(f'CodeBuild project {name} does not exist')
        return response['projects'][0]

    def start_build(self, pull_request_number: str, commit_sha1: str) -> str:
        """
        Starts a CodeBuild build and returns its id

        :param pull_request_number:
        :param commit_sha1:
        :return:
        """
        response = client.start_build(
            projectName=self.project['name'],
            artifactsOverride={'type': 'NO_ARTIFACTS'},
            sourceVersion=f'pr/{pull_request_number}',
            environmentVariablesOverride=[
                {
                    'name': 'GIT_PR',
                    'value': str(pull_request_number),
                    'type': 'PLAINTEXT',
                },
                {
                    'name': 'GIT_COMMIT',
                    'value': str(commit_sha1),
                    'type': 'PLAINTEXT',
                }
            ],
            buildspecOverride='prcheck-buildspec.yaml'
        )
        return response['build']['id']
