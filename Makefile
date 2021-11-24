VENV_DIR = venv
BUCKET_NAME ?= ""
STACK_S3_PREFIX ?= "codebuild-notifications-github"
CFN_STACK_NAME ?= "codebuild-notifications-github"
GITHUB_ACCESS_TOKEN ?= ""

build:
	sam build --debug

package: build
	sam package \
		--template-file .aws-sam/build/template.yaml \
		--output-template-file .aws-sam/build/packaged.yaml \
		--s3-bucket $(BUCKET_NAME) \
		--s3-prefix $(STACK_S3_PREFIX) \
		--force-upload

deploy: package
	sam deploy \
		--template-file .aws-sam/build/packaged.yaml \
		--capabilities CAPABILITY_IAM \
		--s3-bucket $(BUCKET_NAME) \
		--s3-prefix $(STACK_S3_PREFIX) \
		--stack-name $(CFN_STACK_NAME) \
		--no-fail-on-empty-changeset \
		--parameter-overrides ParameterKey=GitHubAccessToken,ParameterValue=$(GITHUB_ACCESS_TOKEN)

venv-init:
	python3 -m venv $(VENV_DIR)
	$(VENV_DIR)/bin/pip install -r requirements-dev.txt

code-style: venv-init
	$(VENV_DIR)/bin/flake8 ./src --exclude=.pyc,__init__.py,src/tests --max-line-length=120
	$(VENV_DIR)/bin/mypy ./src --python-executable=$(VENV_DIR)/bin/python --exclude=src/tests
	$(VENV_DIR)/bin/safety check --full-report

test: code-style
	PYTHONPATH=`pwd`/src $(VENV_DIR)/bin/python -m unittest discover src/tests -p *_test.py
