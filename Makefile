include .env

VERSION := $(shell git describe --tags)

all: push

.PHONY: manifest
manifest:
	podman manifest create ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAMESPACE}/${PROJECT_NAME}:latest || true

.PHONY: build
build: manifest
	#podman build -t ${PROJECT_NAME} .
	podman build --platform linux/amd64,linux/arm64 --manifest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/floyd/${PROJECT_NAME}:latest .
	podman build --platform linux/amd64,linux/arm64 --manifest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/floyd/${PROJECT_NAME}:${VERSION} .

.PHONY: push
push: build login
	podman manifest push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/floyd/${PROJECT_NAME}:latest
	podman manifest push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/floyd/${PROJECT_NAME}:${VERSION}
	@git-cliff -u
	@echo "version: ${VERSION}"

.PHONY: login
login:
	aws ecr get-login-password --profile ${AWS_PROFILE} --region ${AWS_REGION} | podman login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
