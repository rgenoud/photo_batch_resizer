# Photo Batch Resizer

Les logiciels de retouche d'images permettent de redimensionner des photos, mais c'est souvent une par une...

Ce logiciel permet de redimenssionner toutes les images contenues dans un répertoire vers un autre, en une seule fois
et surtout en utilisant tous les processeurs disponibles (donc x fois plus vite).

Il y a une version GUI, en python.

Elle a besoin du paquet python-pyexiv2 et python-wxgtk3.0

sudo apt-get install python-pyexiv2 python-wxgtk3.0

La version non-GUI est un simple makefile utilisant convert (sudo apt-get install imagemagick)
