# Fichier des prénoms (état civil)
Paru le : 20/06/2022<br>
Le fichier des prénoms contient des données sur les prénoms attribués aux enfants nés en France entre 1900 et 2021. Ces données sont disponibles au niveau France et par département. 
## Téléchargement
Les fichiers proposés en téléchargement recensent les naissances et non pas les personnes vivantes une année donnée. Ils sont proposés dans deux formats (DBASE et CSV). Pour utiliser ces fichiers volumineux, il est recommandé d'utiliser un gestionnaire de bases de données ou un logiciel statistique. Le fichier au niveau national peut être ouvert à partir de certains tableurs. Le fichier au niveau départemental est en revanche trop volumineux (3,7 millions de lignes) pour pouvoir être consulté avec un tableur, il est donc proposé dans une version allégée avec les naissances depuis 2000 uniquement.<br>
Les données sont accessibles dans :
* un **fichier de données nationales** qui contient les prénoms attribués aux enfants nés en France entre 1900 et 2021 (les données avant 2012 ne concernent que France hors Mayotte) et les effectifs par sexe associés à chaque prénom ;
* un **fichier de données départementales** qui contient les mêmes informations au niveau département de naissance ;
* un **fichier de données allégé** qui contient les informations au niveau département de naissance depuis l'année 2000.
## Documentation
### Avertissement
Le fichier des prénoms est établi à partir des seuls bulletins de naissance des personnes nées en France (métropole et départements d’outre-mer). En conséquence, l’exhaustivité n’est pas garantie sur toute la période, notamment pour les années antérieures à 1946. Les utilisateurs pourront donc constater des écarts avec le nombre annuel des naissances évalué par l'Insee. Ces écarts, importants en début de période, vont en s’amenuisant. Après 1946, ils sont peu significatifs.<br><br>
Les informations contenues dans le fichier des prénoms sont basées sur les bulletins d'état civil transmis à l’Insee par les officiers d’état civil des communes. Ces bulletins sont eux-mêmes établis à partir des déclarations des parents. L'Insee ne peut garantir que le fichier des prénoms soit exempt d'omissions ou d'erreurs.<br><br>
La refonte du processus électoral a entraîné un nombre de corrections dans la base des prénoms plus important que les années précédentes. En effet, chaque électeur est maintenant inscrit au répertoire électoral unique avec son état civil officiel (celui du Répertoire national d'identification des personnes physiques / RNIPP), des anomalies ont donc été corrigées.
### Pour comprendre
Pour chaque prénom, il est indiqué pour chaque année de naissance (de 1900 à 2021) et chaque sexe, le nombre de personnes inscrites à l'état civil sous ce prénom. Pour le fichier « DPT2021 », la précision est apportée pour chaque département.<br><br>
**Les personnes prises en compte**<br>
Le champ couvre l'ensemble des personnes nées en France hors Mayotte et enregistrées à l'état civil sur les bulletins de naissance. Les personnes nées à l'étranger sont exclues.<br><br>
**Le champ des prénoms retenus**<br>
Dans les fichiers de l’état civil, en l'occurrence les bulletins de naissance, les différents prénoms sont séparés par une espace (ou blanc). Ainsi deux prénoms séparés par un tiret constituent un seul prénom composé (exemple : Anne-Laure). Le premier prénom simple ou composé figure en début de liste, et c'est celui qui sera retenu après le traitement de la protection de l'anonymat.<br><br>
**Conditions portant sur les prénoms retenus**<br>
1. Sur la période allant de 1900 à 1945, le prénom a été attribué au moins 20 fois à des personnes de sexe féminin et/ou au moins 20 fois à des personnes de sexe masculin
2. Sur la période allant de 1946 à 2021, le prénom a été attribué au moins 20 fois à des personnes de sexe féminin et/ou au moins 20 fois à des personnes de sexe masculin
3. Pour une année de naissance donnée, le prénom a été attribué au moins 3 fois à des personnes de sexe féminin ou de sexe masculin
Les effectifs des prénoms ne remplissant pas les conditions 1 et 2 sont regroupés (pour chaque sexe et chaque année de naissance) dans un enregistrement dont le champ prénom (PREUSUEL) prend la valeur «_PRENOMS_RARES_». Les effectifs des prénoms remplissant la condition 2 mais pas la condition 3 sont regroupés (pour chaque sexe et chaque prénom) dans un enregistrement dont le champ année de naissance (ANNAIS) prend la valeur «XXXX».

**Précision pour le département de naissance**<br>
Sur toute la période, le département de naissance (variable DPT) est celui existant au moment de la naissance. Ainsi une personne née à Issy-les-Moulineaux en 1949 sera codée en 75 (Seine), et une personne née en 1971 à Issy-les-Moulineaux sera codée en 92 (Hauts-de-Seine).<br>
En effet, de par la loi n° 64-707 du 10/07/1964, il y a eu création des départements 75 (Paris), 78 (Yvelines), 91 (Essonne), 92 (Hauts-de-Seine), 93 (Seine-Saint-Denis), 94 (Val-de-Marne) et 95 (Val-d'Oise), à partir des anciens départements 75 (Seine) et 78 (Seine-et-Oise), avec une date d'effet dans le fichier au 1er janvier 1968.<br>
Un regroupement de code a été fait pour la variable DPT :
* le code DPT=20 est utilisé pour les naissances ayant eu lieu dans les deux départements 2A (Corse-du-Sud) et 2B (Haute-Corse);

Lorsque le champ année de naissance (ANNAIS) est codé «XXXX», le département de naissance (DPT) est également codé en «XX».
## Dictionnaire des variables
Le premier fichier **national** comporte 686 538 enregistrements et quatre variables décrites ci-après:
* Ce fichier est trié selon les variables SEXE, PREUSUEL, ANNAIS.
* Nom : SEXE - intitulé : sexe - Type : caractère - Longueur : 1 - Modalité : 1 pour masculin, 2 pour féminin
* Nom : PREUSUEL - intitulé : premier prénom - Type : caractère - Longueur : 25
* Nom : ANNAIS - intitulé : année de naissance - Type : caractère - Longueur : 4 - Modalité : 1900 à 2021, XXXX
* Nom : NOMBRE - intitulé : fréquence - Type : numérique - Longueur : 8*

Le second fichier **départemental** comporte 3 784 673 enregistrements et cinq variables décrites ci-après:
Ce fichier est trié selon les variables SEXE, PREUSUEL, ANNAIS, DPT.
* Nom : SEXE - intitulé : sexe - Type : caractère - Longueur : 1 - Modalité : 1 pour masculin, 2 pour féminin
* Nom : PREUSUEL - intitulé : premier prénom - Type : caractère - Longueur : 25
* Nom : ANNAIS - intitulé : année de naissance - Type : caractère - Longueur : 4 - Modalité : 1900 à 2021, XXXX
* Nom : DPT - intitulé : département de naissance - Type : caractère - Longueur : 3 - Modalité : liste des départements, XX
* Nom : NOMBRE - intitulé : fréquence - Type : numérique - Longueur : 8



