FROM --platform=linux/amd64 python:3.10-slim  
ENV PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  VENV_PATH="/code/.venv"

ENV PATH="/bin:$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
ENV $(cat .env | grep -v '^#' | xargs)
WORKDIR /code



COPY pyproject.toml /code/pyproject.toml
COPY ./app /code/app 
COPY ./README.md /code/README.md
RUN pip install poetry==1.5.1

RUN poetry install

# Expose port (adjust if needed)
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000","--reload"]
# CMD ["sleep","10000"]


