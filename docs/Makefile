FRIENDLY_PDF=opis.pdf
MAIN_PDF=description.pdf
MAIN_TEX=description.tex
OUTPUT_DIR=aux

TEXES := $(MAIN_TEX) $(wildcard *.tex) $(wildcard ./include/*.tex) $(wildcard ./tasks/*.tex)

.PHONY: all
all: $(FRIENDLY_PDF)

$(FRIENDLY_PDF): $(TEXES)
	mkdir -p $(OUTPUT_DIR)
	pdflatex -output-directory=$(OUTPUT_DIR) -interaction scrollmode $(MAIN_TEX) | texlogfilter
	cp ./$(OUTPUT_DIR)/$(MAIN_PDF) ./$(FRIENDLY_PDF)

.PHONY: clean
clean:
	@rm -r $(OUTPUT_DIR) 2>/dev/null || exit 0
	@rm $(FRIENDLY_PDF) 2>/dev/null || exit 0
