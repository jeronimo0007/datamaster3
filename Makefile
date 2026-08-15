# Alvos — Docker local, Azure e AWS (mesma stack). Sem VPS/k3s.
.PHONY: help up-local deploy-azure deploy-aws

TF_AZURE ?= infrastructure/terraform/apresentacao
TF_AWS ?= infrastructure/terraform/aws

help:
	@echo "Targets:"
	@echo "  up-local       - docker compose (demo engenharia de dados)"
	@echo "  deploy-azure   - terraform Azure (mesma stack: Kafka, Mongo, lake)"
	@echo "  deploy-aws     - terraform AWS (S3 + ECS: Kafka/Mongo/Airflow/API)"
	@echo "Docs: readme.md | docs/VISAO_GESTAO.md"

up-local:
	bash scripts/up-local.sh

deploy-azure:
	cd $(TF_AZURE) && terraform init -upgrade && terraform plan && terraform apply

deploy-aws:
	cd $(TF_AWS) && terraform init -upgrade && terraform plan && terraform apply
