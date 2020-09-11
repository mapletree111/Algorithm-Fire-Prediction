DOC=main

all: pdf

dvi: ${DOC}.tex
	latex $(DOC).tex
	#bibtex $(DOC)
	latex $(DOC).tex

ps: dvi
	dvips -R -Poutline -t letter ${DOC}.dvi -o ${DOC}.ps

pdf: ps
	ps2pdf ${DOC}.ps
	rm -f ${DOC}.aux
	rm -f ${DOC}.log
	rm -f ${DOC}.dvi
	rm -f ${DOC}.out
	rm -f ${DOC}.ps
	rm -f ${DOC}.toc

clean-dvi:
	rm -f ${DOC}.aux
	rm -f ${DOC}.log
	rm -f ${DOC}.dvi
	rm -f ${DOC}.out
	rm -f ${DOC}.toc
	rm -f ${DOC}.blg
	rm -f ${DOC}.bbl

clean-ps: clean-dvi
	rm -f ${DOC}.ps

clean-pdf: clean-ps
	rm -f ${DOC}.pdf

clean: clean-pdf
