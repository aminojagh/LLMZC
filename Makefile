run:
	uv run python src/assistant.py $(ARGS)
chat:
	uv run streamlit run src/app.py
network:
	docker network inspect monitoring >/dev/null 2>&1 || docker network create monitoring
postgres: network
	docker start -a course-assistant-pg 2>/dev/null || docker run -it \
		--name course-assistant-pg \
		--network monitoring \
		-e POSTGRES_USER=user \
		-e POSTGRES_PASSWORD=password \
		-e POSTGRES_DB=course_assistant \
		-p 5432:5432 \
		-v pgdata:/var/lib/postgresql/data \
		postgres:17