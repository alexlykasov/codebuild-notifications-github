# codebuild-notifications-github

This is a serverless application (AWS SAM) that listens to new pull requests in GitHub, runs unit tests and other
type of code checks, and sets GitHub commit status to pending, failed, or success.

## How to deploy and use:

1. Install AWS SAM and python
1. `make deploy`
1. Navigate to AWS Cloudformation, and check the WebhookEndpoint output variable in the new stack
1. Configure this endpoint to be webhook in GitHub: `Which events would you like to trigger this webhook?` --> 
`Let me select individual events.` --> select `Pushed` and `Pull requests`
1. Create a GitHub user. It will be used to set commit statuses in your GitHub repositories.
1. In the GitHub user settings navigate to `Developer settings` --> `Personal access tokens` --> `Generate new token`.
Select options `repo` and `workflow`, click `Generate token`.
1. Navigate to AWS SecretsManager and select the secret created by the SAM stack (`codebuild-access-token` by default).
Edit the secret and save the GitHub user token as plain text there.
1. Create CodeBuild build with the same name as the repo you want to be checking.
1. In the repository settings, grant the newly created user with write permissions.
1. Create a new pull request. It will trigger the build. Build instructions should be placed to `prcheck-buildspec.yaml`
file.
