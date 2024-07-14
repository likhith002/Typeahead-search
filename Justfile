set dotenv-load

# Install project dependencies
install: 
    poetry install

# Run the FastAPI development server
run: 
    uvicorn app.main:app --reload

# Run tests
test: 
    pytest

# Format code using black
format: 
    black .

# Clean up generated files
clean: 
    rm -rf __pycache__ .pytest_cache

# Run the development environment (install, run, and watch for changes)
dev: 
  just install
  just run
