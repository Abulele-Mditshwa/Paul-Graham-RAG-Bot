# RAG Q&A System Makefile

.PHONY: help install setup ingest index evaluate query clean test

help:
	@echo "Available commands:"
	@echo "  install    - Install dependencies"
	@echo "  setup      - Setup AWS resources and run full pipeline"
	@echo "  ingest     - Scrape and chunk Paul Graham essays"
	@echo "  index      - Create OpenSearch index and embed documents"
	@echo "  evaluate   - Run evaluation on test queries"
	@echo "  query      - Start interactive query mode"
	@echo "  clean      - Clean up data and AWS resources"
	@echo "  test       - Run basic functionality tests"

install:
	pip install -r requirements.txt

setup: install ingest index
	@echo "✅ Setup complete! You can now run queries."

ingest:
	python src/ingest.py

index:
	python src/index.py

evaluate:
	python src/evaluate.py

query:
	python src/query.py --interactive

clean:
	rm -rf data/
	@echo "⚠️  Note: AWS resources (OpenSearch collection) not automatically deleted"
	@echo "   Use AWS Console or CLI to delete the collection if needed"

test:
	python src/query.py --query "What does Paul Graham say about startups?" --top-k 3

# Development commands
dev-install:
	pip install -e .
	pip install pytest black flake8

format:
	black src/
	
lint:
	flake8 src/

# Quick demo
demo:
	@echo "Running quick demo..."
	python src/query.py --query "What does Paul Graham say about learning programming?"
	python src/query.py --query "How to get startup ideas?"
	python src/query.py --query "What makes a good essay?"