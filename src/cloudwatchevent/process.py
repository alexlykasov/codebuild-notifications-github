from typing import Dict

from common.exceptions import UnsupportedBuildStatus, RequiredEnvVarsNotSet
from common.githubutils import GitHubApp
from settings import logger


def _repo_url_to_full_name(github_url: str) -> str:
    """
    Converts this `https://github.com/UserName/test-codebuild.git`
    into this `UserName/test-codebuild`

    :param github_url:
    :return:
    """
    return github_url.replace('https://github.com/', '').replace('.git', '')


def _get_env_value(key: str, event: Dict) -> str:
    """
    Retrieves environment variable from CodeBuild event

    :param key:
    :param event:
    :return:
    """
    variables = event['detail']['additional-information']['environment']['environment-variables']
    for i in variables:
        if i['name'] == key:
            return i['value']
    raise RequiredEnvVarsNotSet(f'Build does not have required env variable {key}')


def watch_codebuild_state_change(lambda_event: Dict) -> None:
    """
    Updates GitHub commit status based on CodeBuild build status

    :param lambda_event:
    :return:
    """
    build_status = lambda_event['detail']['build-status']
    if build_status not in ["FAILED", "STOPPED", "SUCCEEDED"]:
        raise UnsupportedBuildStatus(f'We do not notify GiHub about {build_status} build status')

    pull_request_id = _get_env_value('GIT_PR', lambda_event)
    commit_sha = _get_env_value('GIT_COMMIT', lambda_event)
    project_name = lambda_event['detail']['project-name']
    build_id = lambda_event['detail']['build-id'].split(':')[-1]

    github = GitHubApp(
        repo_full_name=_repo_url_to_full_name(lambda_event['detail']['additional-information']['source']['location']),
        build_id=build_id,
        build_project_name=project_name,
        pr_id=int(pull_request_id)
    )

    if build_status == 'SUCCEEDED':
        github.success(commit_sha)
        logger.info(f'Build {project_name}:{build_id} succeeded')
    else:
        github.failure(commit_sha)
        logger.info(f'Build {project_name}:{build_id} failed with status {build_status}')
