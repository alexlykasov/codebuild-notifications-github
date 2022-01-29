import boto3
from github import Github
from github.Commit import Commit

import settings


sm_client = boto3.client('secretsmanager')


class GitHubApp:

    def __init__(self, repo_full_name: str, build_id: str, build_project_name: str, pr_id: int) -> None:
        g = Github(login_or_token=self._get_sm_secret())
        self.repo = g.get_repo(full_name_or_id=repo_full_name)
        self.commits = self.repo.get_pull(pr_id).get_commits()
        self.build_id = build_id
        self.build_project_name = build_project_name

    def pending(self, commit_sha: str) -> None:
        self._set_status(commit_sha, 'pending', '**checking PR**')

    def success(self, commit_sha: str) -> None:
        self._set_status(commit_sha, 'success', 'looks good')

    def failure(self, commit_sha: str) -> None:
        self._set_status(commit_sha, 'failure', '**failure**')

    def _set_status(self, commit_sha: str, state: str, description: str) -> None:
        commit = self._get_commit(commit_sha)
        commit.create_status(
            state=state,
            target_url=f'https://console.aws.amazon.com/codebuild/home?region='
                       f'{settings.REGION}#/builds/{self.build_project_name}:{self.build_id}/view/new',
            description=description
        )

    def _get_sm_secret(self) -> str:
        response = sm_client.get_secret_value(SecretId=settings.SM_PARAMETER_ACCESS_TOKEN)
        return response['SecretString']

    def _get_commit(self, commit_sha: str) -> Commit:
        for i in self.commits:
            if i.sha == commit_sha:
                return i
        raise Exception(f'Commit {commit_sha} not found')
