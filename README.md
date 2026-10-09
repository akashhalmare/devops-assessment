# DevOps Assessment: Assignment 1

A small Flask service with automated tests, a container image build, optional OIDC-based Amazon ECR publishing, and Kubernetes manifests prepared for a future Amazon EKS deployment. CI uses GitHub-hosted runners; Docker and Kubernetes are not required on the Windows development laptop.

## Architecture

- `app/` contains the Flask application factory and routes.
- `GET /` returns `Hello from DevOps Assessment`.
- `GET /health` returns `{"status":"healthy"}` for health checks.
- `tests/` contains pytest endpoint tests.
- The GitHub Actions workflow tests the app and builds the image on GitHub-hosted runners. Publishing to ECR is a separate, manual, opt-in job.
- `k8s/` contains a Deployment and internal ClusterIP Service. The Deployment image is supplied through the `ECR_IMAGE_URI` placeholder.

## Local setup (Windows, Python 3.11)

From the repository folder, create and activate a virtual environment, then install the small project dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the development server:

```powershell
python run.py
```

Visit `http://127.0.0.1:5000/` or `http://127.0.0.1:5000/health`. The local server is Flask's development server; the container uses Gunicorn.

## Verification

Run the endpoint tests locally after installing the requirements:

```powershell
python -m pytest
```

On every push and pull request, GitHub Actions installs the requirements, runs pytest, and builds (but does not publish) the Docker image on a GitHub-hosted runner. Review the Actions run for the result. No local Docker installation is needed.

## Optional ECR publishing

Publishing is disabled by default. Before enabling it, an administrator must create the ECR repository and configure a GitHub OIDC identity provider and IAM role in AWS. This project does not create those AWS resources.

Configure these GitHub repository variables:

- `AWS_ROLE_ARN`: IAM role ARN trusted for this repository's GitHub OIDC identity.
- `AWS_REGION`: AWS region containing the ECR repository.
- `ECR_REPOSITORY`: existing ECR repository name.

Grant the role only the ECR push permissions required for that repository (`ecr:GetAuthorizationToken`, `ecr:BatchCheckLayerAvailability`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`, and `ecr:PutImage`). Its trust policy should constrain the audience to `sts.amazonaws.com` and the subject to this repository's `refs/heads/main`. Do not configure long-lived AWS access keys in GitHub.

To publish later, run the `CI/CD` workflow manually from the `main` branch and set `publish_to_ecr` to `true`. The image is tagged with the commit SHA. The workflow only assumes the AWS role in this explicitly requested publish job.

## Future EKS deployment (not performed)

Creating an EKS cluster and its supporting networking and compute can incur charges. Do not proceed until the AWS budget and resource costs are understood; no AWS resources have been created as part of Assignment 1.

After an EKS cluster exists, its worker-node IAM role can pull from the ECR repository, and `kubectl` is configured for it:

1. Publish an image to the pre-existing ECR repository using the optional workflow above.
2. In PowerShell, set the full ECR image URI, render the Deployment template to a temporary file, and apply both manifests:

	```powershell
	$env:ECR_IMAGE_URI = "<account-id>.dkr.ecr.<region>.amazonaws.com/devops-assessment:<commit-sha>"
	$deployment = (Get-Content .\k8s\deployment.yaml -Raw).Replace('${ECR_IMAGE_URI}', $env:ECR_IMAGE_URI)
	$rendered = Join-Path $env:TEMP 'devops-assessment-deployment.yaml'
	Set-Content -Path $rendered -Value $deployment -Encoding utf8
	kubectl apply -f $rendered
	kubectl apply -f .\k8s\service.yaml
	kubectl rollout status deployment/devops-assessment
	```

3. Verify the service without provisioning a public load balancer:

	```powershell
	kubectl port-forward service/devops-assessment 8080:80
	```

	Then check `http://127.0.0.1:8080/` and `http://127.0.0.1:8080/health`. The Service is `ClusterIP`; it is not internet-facing.
