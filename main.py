#! /usr/bin/env python3
# -*-coding:Utf-8 -*

# ------------------------------------------------------
# --------------------- IMPORT -------------------------
# ------------------------------------------------------
# Import 

import os
import requests
from bs4 import BeautifulSoup
import unicodedata

# ------------------------------------------------------
# --------------------- CLASS --------------------------
# ------------------------------------------------------
# Class

class ResolveDQ:
    """
    La class permet de choisir la meilleure réponse à la question passée en paramètre.

    Paramètres
    ----------
    question :  str, par défaut ""
                C'est la question en format str
    
    r1, r2, r3, r4 : str, par défaut ""
                Ce sont les réponses en format str
    """

    def __init__(self, question="", r1="", r2="", r3="", r4=""):
        self.q = question
        self.r1 = r1[:-1].lower()
        self.r2 = r2[:-1].lower()
        self.r3 = r3[:-1].lower()
        self.r4 = r4[:-1].lower()
        listWord = ['le ', 'la ', 'les ', 'un ', 'une ', 'des ']
        for word in listWord:
            self.r1 = self.r1.replace(word, '')
            self.r2 = self.r2.replace(word, '')
            self.r3 = self.r3.replace(word, '')
            self.r4 = self.r4.replace(word, '')
        self.countr1 = 0
        self.countr2 = 0
        self.countr3 = 0
        self.countr4 = 0
        self.state = 'none'
        if self.q.find(' ne ') > -1 or self.q.find(' pas ') > -1 or self.q.find(' PAS ') > -1:
            self.neg = 1
        else:
            self.neg = 0
    
    def countstr(self,strpage):
        """
        Methode interne qui sert à compter le nbre de fois qu'apparaît les réponses
        dans la page reçu en entrée
        """

        strpage = strpage.lower()
        self.countr1 = strpage.count(self.r1)
        self.countr2 = strpage.count(self.r2)
        self.countr3 = strpage.count(self.r3)
        self.countr4 = strpage.count(self.r4)
        return (self.countr1 + self.countr2 + self.countr3 + self.countr4)

    def searchgoogle(self):
        """
        - On lance la recherche sur google
        - La méthode va d'abord retirer tous les accents et autres dans le str de la question
        - Ensuite va créer l'URL pour rechercher sur google.com
        - Après elle va récupérer le code de la page web
        - Elle va d'abord compter le nombre de fois qu'apparaît les réponses dans la partie
            réponse de google.com, s'il n'y en a pas, va prendre le premier lien wikipedia et
            va compter le nombre de fois qu'apparaît les réponses dans la page wikipedia,
            S'il n'y a pas de lien wikipedia, va chercher sur toute la page le nbre de fois
            qu'apparaît les réponses
        """

        self.q = str(unicodedata.normalize('NFKD', self.q).encode('ascii', 'ignore')) #On retire les accents
        self.q = self.q[2:]
        self.q = self.q.replace('\\n', ' ')
        strurl = 'https://www.google.com/search?q=' + self.q.replace(' ', '+')
        strurl = strurl[:-6]
        print(strurl)
        html = requests.get(strurl)
        dom = BeautifulSoup(html.text, 'lxml')
        res = dom.findAll("div", {"class": "jfp3ef"})[0]
        strpage = str(res)

        if strpage.count('https://') == 0:
            if ResolveDQ.countstr(self, strpage) != 0:
                self.state = 'réponse google'
                return

        for link in dom.find_all('a', href=True):
            if str(link['href']).count('/url?q=https://fr.wikipedia.org/wiki/'):
                strurl2 = 'https://www.google.com' + link['href']
                html = requests.get(strurl2)
                dom = BeautifulSoup(html.text, 'lxml')
                if ResolveDQ.countstr(self, str(dom.find_all())) != 0:
                    self.state = 'wikipedia'
                    return
        
        html = requests.get(strurl)
        dom = BeautifulSoup(html.text, 'lxml')
        ResolveDQ.countstr(self, str(dom.find_all()))
        self.state = 'page globale'
    
    def display(self):
        """
        La méthode va afficher les résultats après avoir fait la recherche
        ------------
        - Elle affiche la source de la recherche ("réponse google", "wikipedia", 
            "page gloable")
        - Elle va mettre en forme de pourcentage le nombre de fois que les réponses
            apparaissent
        - Va mettre en vert la réponse (prend en compte si la question est négative
            ou positive)
        """

        print('state : {}'.format(self.state))
        print('negatif = {}'.format(self.neg))
        if (self.countr1 + self.countr2 + self.countr3 + self.countr4) == 0:
            print('Pas de réponse')
        else:
            dicoR = {self.r1: self.countr1, self.r2: self.countr2, self.r3: self.countr3, self.r4: self.countr4}
            listR = [self.countr1, self.countr2, self.countr3, self.countr4]
            
            if self.neg == 0:
                listR.sort(reverse=True)
            else:
                listR.sort()
            for i in dicoR:
                if dicoR[i] == listR[0]:
                    print('\033[1m\033[32m{} = {}\033[0m'.format(i, (dicoR[i] * 100)/sum(listR)))
                else:
                    print('{} = {}'.format(i, (dicoR[i] * 100)/sum(listR)))




# ------------------------------------------------------
# ---------------------- MAIN --------------------------
# ------------------------------------------------------
# Main

# ------------------------------------------------------
# ------------ SCREEN ET ANALYSE DE L'IMAGE ------------
# ------------------------------------------------------
"""
Ici on va extraire les informations importantes de l'application
Duel Quizz. Pour cela on fait
-   On fait une capture de l'écran du pc
-   On va découper cette image en 5 parties (Question, Réponse 1,
    Réponse 2, Réponse 3, Réponse 4)
-   On met les images en négatif pour un meilleur résultat
-   On utilise l'OCR Tesseract pour extraire les textes
-   On ouvre les fichiers contenant les textes

"""

os.system('screencapture capture.png') # Fait un screenshot de l'ecran
os.system('convert -crop 632x257+1900+355 capture.png q1.png') # Coupe l'image en differente partie
os.system('convert -crop 282x52+1898+890 capture.png r1.png')
os.system('convert -crop 282x52+2238+890 capture.png r2.png')
os.system('convert -crop 292x52+1898+1140 capture.png r3.png')
os.system('convert -crop 282x52+2238+1140 capture.png r4.png')

os.system('convert r1.png -channel RGB -negate r1.png')# met les images en negatives pour un meilleur resultat
os.system('convert r2.png -channel RGB -negate r2.png')
os.system('convert r3.png -channel RGB -negate r3.png')
os.system('convert r4.png -channel RGB -negate r4.png')

os.system('tesseract q1.png Q1') # On transforme le texte png en txt
os.system('tesseract r1.png R1')
os.system('tesseract r2.png R2')
os.system('tesseract r3.png R3')
os.system('tesseract r4.png R4')

question = open('./Q1.txt', 'r') # On ouvre les fichiers contenant le texte
r1 = open('./R1.txt', 'r')
r2 = open('./R2.txt', 'r')
r3 = open('./R3.txt', 'r')
r4 = open('./R4.txt', 'r')
dq = ResolveDQ(question.read(), r1.readline(), r2.readline(), r3.readline(), r4.readline())

# ------------------------------------------------------
# ----------------- RECHERCHE REPONSE ------------------
# ------------------------------------------------------
"""
Ici on va chercher la bonne réponse en utilisant un objet
"""

#------------- Phase de test -----------
# Il faut mettre en commentaire toute la partie OCR, fermeture de fichier et activer ici
# question = 'Principalement sur quel continent se déroule le jeu "Resident Evil 5"'
# r1 = 'Afrique\n'
# r2 = 'Asie\n'
# r3 = 'Amérique du Nord\n'
# r4 = 'Europe\n'
# dq = ResolveDQ(question, r1, r2, r3, r4)
#----------------------------------------

dq.searchgoogle()
dq.display()

# ------------------------------------------------------
# ----------------- FERMETURE FICHIER ------------------
# ------------------------------------------------------
"""
Fermeture des fichiers ouverts. on place cette étape à la fin 
pour avoir la réponse le plus rapidement
"""

question.close()
r1.close()
r2.close()
r3.close()
r4.close()