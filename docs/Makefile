TEXES := $(wildcard *.tex)
FILES := $(TEXES:%.tex=./pdfs/%.pdf)
./pdfs/%.pdf: %.tex
	pdflatex -output-directory=aux $<
	mv ./aux/$(basename $<).pdf ./pdfs/

all: $(FILES)


.PHONY: all
