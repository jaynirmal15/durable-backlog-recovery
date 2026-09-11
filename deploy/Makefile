# Operator commands for the E-series boundary runner.
#
# The instance is STOPPED whenever runs are not executing. Stopped, only the
# 50 GB gp3 volume bills (about $4/month); running, it is about $0.34/hr.
#
#   make up        create the instance (one time)
#   make start     start it before a campaign
#   make status    is it running, and what does it cost right now
#   make sync      push the repo to the box
#   make ssh       shell in
#   make stop      stop it -- DO THIS WHEN THE CAMPAIGN PAUSES
#   make fetch     pull results back
#   make destroy   tear everything down

TF      := terraform -chdir=ec2
PROFILE ?= medialab
REGION  ?= us-east-1
KEY     ?= ~/.ssh/rhc-ec2
REPO    := $(abspath ..)

IID = $(shell $(TF) output -raw instance_id 2>/dev/null)
IP  = $(shell aws ec2 describe-instances --profile $(PROFILE) --region $(REGION) \
        --instance-ids $(IID) --query 'Reservations[0].Instances[0].PublicIpAddress' --output text 2>/dev/null)

.PHONY: key up start stop status ssh sync fetch destroy guard-running

key:
	@test -f $(KEY) || ssh-keygen -t ed25519 -N '' -f $(KEY) -C rhc-runner
	@echo "key: $(KEY)"

up: key
	$(TF) init -input=false
	$(TF) apply -input=false \
	  -var "allowed_ssh_cidr=$$(curl -s https://checkip.amazonaws.com | tr -d '\n')/32" \
	  -var "budget_notify_email=$(EMAIL)"

start:
	aws ec2 start-instances --profile $(PROFILE) --region $(REGION) --instance-ids $(IID) >/dev/null
	aws ec2 wait instance-running --profile $(PROFILE) --region $(REGION) --instance-ids $(IID)
	@echo "running at $(IP); waiting for sshd"
	@until ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5 -i $(KEY) ubuntu@$(IP) true 2>/dev/null; do sleep 5; done
	@echo "ready"

stop:
	aws ec2 stop-instances --profile $(PROFILE) --region $(REGION) --instance-ids $(IID) >/dev/null
	aws ec2 wait instance-stopped --profile $(PROFILE) --region $(REGION) --instance-ids $(IID)
	@echo "stopped -- billing is now the volume only"

status:
	@aws ec2 describe-instances --profile $(PROFILE) --region $(REGION) --instance-ids $(IID) \
	  --query 'Reservations[0].Instances[0].{state:State.Name,type:InstanceType,ip:PublicIpAddress,since:LaunchTime}' \
	  --output table

ssh:
	ssh -i $(KEY) ubuntu@$(IP)

# git-tracked files only: never ship the local results/ or bin/ to the box.
sync:
	cd $(REPO) && git ls-files -z | rsync -az --files-from=- --from0 \
	  -e "ssh -i $(KEY)" ./ ubuntu@$(IP):rhc/
	@echo "synced $(shell cd $(REPO) && git ls-files | wc -l | tr -d ' ') tracked files"

fetch:
	rsync -az -e "ssh -i $(KEY)" ubuntu@$(IP):rhc/results/ $(REPO)/results/
	@echo "results pulled"

destroy:
	$(TF) destroy -input=false \
	  -var "allowed_ssh_cidr=0.0.0.0/32" -var "budget_notify_email=$(EMAIL)"
