FRIENDLY_PDF_NAME=opis.pdf
MAIN_PDF=description.pdf
MAIN_TEX=description.tex
OUTPUT_DIR=aux

TEXES := $(MAIN_TEX) $(wildcard *.tex) $(wildcard ./include/*.tex) $(wildcard ./tasks/*.tex)

.PHONY: all
all: $(MAIN_PDF)

$(MAIN_PDF): $(TEXES)
	mkdir -p $(OUTPUT_DIR)
	pdflatex -output-directory=$(OUTPUT_DIR) -interaction scrollmode $(MAIN_TEX) | texlogfilter
	cp ./$(OUTPUT_DIR)/$(MAIN_PDF) ./$(FRIENDLY_PDF_NAME)

.PHONY: clean
clean:
	@rm -r $(OUTPUT_DIR) 2>/dev/null
	@rm $(MAIN_PDF) 2>/dev/null
