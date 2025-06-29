install:
	pip install -r requirements.txt

parse:
	python parser.py

enrich:
	python enrich_with_polish_names.py

all: install parse enrich

clean:
	rm -f cache.json failed.json failed_enrichment.json toxic.json safe.json enrichment.log

.PHONY: install parse enrich all clean
