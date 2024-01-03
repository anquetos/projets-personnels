# NASA Astronomy Picture of the Day (APOD)<br>Création d'un jeu de données

Ce projet est réalisé dans un cadre pédagogique afin d'acquérir de nouvelles compétences.

## Présentation

Chaque jour depuis juin 1995, sur son site [*Astronomy Picture of the Day*](https://apod.nasa.gov/apod/), la NASA présente une image différente de notre univers accompagnée d'une brève explication rédigée par un astronome professionnel.

Les métadonnées associées à chaque image sont accessibles *via* l'API dédiée mise à diposition sur le portail [NASA Open APIs](https://api.nasa.gov/).

**Ce sont ces métadonnées qui serviront de base de travail dans la suite de ce projet.**

## Objectif du projet

L'objectif principal est de construire un *dataset* en récupérant des données grâce à l'API.
Ces données seront ensuite traitées en 3 étapes :
1. Nettoyage des textes et uniformisation des données présentes.
2. Enrichissement des données relatives aux images (format, dimensions, etc.) en extrayant les données EXIF de ces dernières.
3. Enrichissement des données liées aux textes explicatifs en utilsant des méthodes de ***Natural Language Processing* (NLP)** grâce à la librairie **SpaCy**.

## Requêtes

Une clé personnelle est nécessaire pour effectuer les requêtes. Pour en récupérer une, il faut faire une demande sur le portail des API.
> Dans le code présenté dans le cadre de ce projet, et pour des raisons de confidentialité, ma clé personnelle sera lue depuis le fichier `api_key.json` qui contient les informations sous la forme ci-dessous.
>```python
>{
>    "api_key": "YOUR_API_KEY"
>}
>``` 