

start: 
	- @cd deployments && docker compose up

build:
	- @cd deployments && docker compose build