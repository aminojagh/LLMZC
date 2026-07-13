run:
	uv run python src/assistant.py $(ARGS)
chat:
	uv run streamlit run src/app.py