docker: auth backend

auth:
	docker compose build auth
	docker push narfman0/nk-auth-docker

backend:
	docker compose build backend
	docker push narfman0/nk-backend-docker
	
clean: clean-build clean-pyc clean-installer

clean-build: ## remove build artifacts
	find . -name 'build' -exec rm -rf {} +
	find . -name 'dist' -exec rm -rf {} +
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.log' -exec rm -rf {} +
	find . -name '.coverage' -exec rm -rf {} +

clean-installer:
	rm -fr frontend/output/
	rm -fr frontend/app.spec
	rm -f frontend/nk.spec
	rm -f frontend/nk.zip

clean-pyc: ## remove Python file artifacts
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.pytest_cache' -exec rm -rf {} +
	find . -name '*~' -exec rm -f {} +