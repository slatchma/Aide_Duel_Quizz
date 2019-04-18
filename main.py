#! /usr/bin/env python
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
    Documentation de la class en cours
    """

    def __init__(self, question, r1, r2, r3, r4):
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
        Documentation de la method en cours
        """

        strpage = strpage.lower()
        self.countr1 = strpage.count(self.r1)
        self.countr2 = strpage.count(self.r2)
        self.countr3 = strpage.count(self.r3)
        self.countr4 = strpage.count(self.r4)
        return (self.countr1 + self.countr2 + self.countr3 + self.countr4)

    def searchgoogle(self):
        """
        Documentation de la method en cours
        """

        self.q = str(unicodedata.normalize('NFKD', self.q).encode('ascii', 'ignore')) #On retire les accents
        self.q = self.q[2:]
        self.q = self.q.replace('\\n', ' ')
        strurl = 'https://www.google.com/search?q=' + self.q.replace(' ', '+')
        strurl = strurl[:-6]
        print(strurl)
        html = requests.get(strurl)
        dom = BeautifulSoup(html.text, 'lxml')
        res = dom.findAll("div", {"class": "g"})[0]
        strpage = str(res)

        if strpage.count('https://') == 0:
            if ResolveDQ.countstr(self, strpage) != 0:
                self.state = 'dans le petit carré'
                return

        for link in dom.find_all('a', href=True):
            if str(link['href']).count('/url?q=https://fr.wikipedia.org/wiki/'):
                strurl2 = 'https://www.google.com' + link['href']
                html = requests.get(strurl2)
                dom = BeautifulSoup(html.text, 'lxml')
                if ResolveDQ.countstr(self, str(dom.find_all())) != 0:
                    self.state = 'dans le wikipedia'
                    return
        
        html = requests.get(strurl)
        dom = BeautifulSoup(html.text, 'lxml')
        ResolveDQ.countstr(self, str(dom.find_all()))
        self.state = 'page globale'
    
    def display(self):
        """
        Documentation de la method en cours
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

#------------ OCR - OK ------------------
# os.system('screencapture capture.png') # Fait un screenshot de l'ecran
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
# ---------------------------------------------

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

# ---------------------------------------------
question.close() # On ferme les fichiers, on les places à la fin pour avoir la réponse le plus rapidement
r1.close()
r2.close()
r3.close()
r4.close()