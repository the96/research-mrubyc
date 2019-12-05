TEX=graph

function maketex() {
    cat <<EOF
\documentclass[a4j]{jarticle}
\usepackage{graphicx}
\newcommand{\graph}[1]{\includegraphics[bb=0 0 864 576, width=.5\hsize]{#1}}
\begin{document}
EOF

    odd=0
    for i in *.png
    do
	if [ $odd = 1 ]
	then
	    echo '\graph{'$i'}\\\\'
	else
	    echo '\graph{'$i'}'
	fi
	odd=$(((odd+1)%2))
    done

cat <<EOF
\end{document}
EOF
}

maketex > $TEX.tex
platex $TEX.tex
dvipdfmx $TEX.dvi

