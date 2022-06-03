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

WGSL_GRAMMAR = grammar/src/grammar.json
ANALYZE_SCRIPT=analyze/lalr.py
ANALYZER = $(ANALYZE_SCRIPT) analyze/Grammar.py

# Compute LALR(1) parse table
.PHONY: lalr
lalr: $(ANALYZER) $(WGSL_GRAMMAR)
	python3 $(ANALYZE_SCRIPT) -lalr grammar/src/grammar.json

# Unit tests for the grammar analyzer
.PHONY: analyze_test
analyze_test: $(ANALYZER)
	python3 analyze/test.py 2>&1

# Profile generation
.PHONY: profile
profile : lalr.wgsl.profile
lalr.wgsl.profile: $(ANALYZER) $(WGSL_GRAMMAR)
	python3 -m cProfile -o lalr.wgsl.profile $(ANALYZE_SCRIPT) -lalr grammar/src/grammar.json

# Compute LR(1) item sets
.PHONY: lr
lr: $(ANALYZER) $(WGSL_GRAMMAR)
	python3 $(ANALYZE_SCRIPT) -lr grammar/src/grammar.json

# Compute LL(1) parse table
.PHONY: ll
ll: $(ANALYZER) $(WGSL_GRAMMAR)
	python3 $(ANALYZE_SCRIPT) -ll grammar/src/grammar.json

.PHONY: lalr_simple
lalr_simple: $(ANALYZER) analyze/test/firsts.json
	python3 $(ANALYZE_SCRIPT) -lalr analyze/test/firsts.json

.PHONY: lalr_star
lalr_star: $(ANALYZER) analyze/test/star.json
	python3 $(ANALYZE_SCRIPT) -lalr analyze/test/star.json

# Example 4.42 from Dragon book
.PHONY: lalr_442
lalr_442: $(ANALYZER) analyze/test/ex442.json
	python3 $(ANALYZE_SCRIPT) -lalr analyze/test/ex442.json

