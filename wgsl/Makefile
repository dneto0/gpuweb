.PHONY: all clean

all: index.html grammar/grammar.js test

clean:
	rm -f index.html index.pre.html grammar/grammar.js

index.pre.html: index.bs
	DIE_ON=everything bash ../tools/invoke-bikeshed.sh index.pre.html index.bs

index.html: index.pre.html
	bash ../tools/add-git-head-to-bikeshed-header.sh index.pre.html > index.html

grammar/grammar.js: index.bs extract-grammar.py
	python3 ./extract-grammar.py index.bs grammar/grammar.js

online:
	curl https://api.csswg.org/bikeshed/ -F file=@index.bs -F output=err
	curl https://api.csswg.org/bikeshed/ -F file=@index.bs -F force=1 > index.html

grammar/src/grammar.json : grammar/grammar.js

.PHONY: test
test: analyze_test

ANALYZE_SCRIPT=analyze/lalr.py

# Unit tests for the grammar analyzer
.PHONY: analyze_test
analyze_test:
	python3 analyze/test.py

# Analyze example 4.17 from the Dragon Book
# "Compilers: Principles, Techniques, and Tools",
# Aho, Sethi, and Ullman, 1986
.PHONY: analyze_dragon
dragon:
	python3 $(ANALYZE_SCRIPT)  analyze/test/ex417.json

# Analyze first and follow sets for a simplified WGSL grammar
.PHONY: analyze_first
analyze_first:
	python3 $(ANALYZE_SCRIPT)  analyze/test/firsts.json

# Analyze the WGSL grammar
.PHONY: analyze
analyze: grammar/src/grammar.json
	python3 $(ANALYZE_SCRIPT)  grammar/src/grammar.json

# Example 4.42 from Dragon book
.PHONY: analyze_442
analyze_442: grammar/src/grammar.json
	python3 $(ANALYZE_SCRIPT) -lalr analyze/test/ex442.json

# Profile an abbreviated computation of LALR(1) item sets
.PHONY: profile
profile: grammar/src/grammar.json
	python3 -m cProfile -o lalrstats.wgsl $(ANALYZE_SCRIPT) -lalr grammar/src/grammar.json -limit 100

# Compute LR(1) item sets
.PHONY: lr
lr: grammar/src/grammar.json
	python3 $(ANALYZE_SCRIPT) -lr grammar/src/grammar.json

# Compute LALR(1) item sets
.PHONY: lalr
lalr: grammar/src/grammar.json
	python3 $(ANALYZE_SCRIPT) -lalr grammar/src/grammar.json
