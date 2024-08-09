docker: auth backend

auth:
	docker compose build auth
	docker push narfman0/nk-auth-docker

backend:
	docker compose build backend
	docker push narfman0/nk-backend-docker