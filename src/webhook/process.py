from typing import Dict

from settings import logger
from common.codebuild import CodeBuild
from common.githubutils import GitHubApp


def start_codebuild_build(lambda_context: Dict) -> None:
    """
    Starts CodeBuild build and sets commit status to `pending`

    :param lambda_context:
    :return:
    """
    if lambda_context.get('pull_request') and lambda_context['action'] in ['opened', 'synchronize']:
        project_name = lambda_context['pull_request']['base']['repo']['name']

        logger.debug(f'Starting CodeBuild build for project {project_name}')

        commit_sha = lambda_context['pull_request']['head']['sha']
        pull_request_num = lambda_context['pull_request']['number']

        codebuild = CodeBuild(project_name)
        build_id = codebuild.start_build(
            pull_request_number=pull_request_num,
            commit_sha1=commit_sha,
        )

        github = GitHubApp(
            repo_full_name=lambda_context['pull_request']['base']['repo']['full_name'],
            pr_id=pull_request_num,
            build_id=build_id,
            build_project_name=project_name
        )
        github.pending(commit_sha)
