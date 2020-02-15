import os
import random

class ThreeWords:

    def __init__(self, file:str):
        self.load(file)

    def load(self, file:str):
        with open(file) as f:
            self.wordslist = f.read().lower().replace(".", '').replace("\n",
                                                                ' ').split(" ")

    def threewords(self):
        index = random.randrange(0, len(self.wordslist), 3)
        threeWord = [
            self.wordslist[index+n]
            for n in range(3)
            ]
        return(' '.join(threeWord).title().strip() + '.')

    def metawords(self):
        randomWords = random.sample(set(self.wordslist),3)
        return(' '.join(randomWords).title().strip() + '.')

    def getIndex(self, threewords):
        indexList = []
        for n in threewords.lower().replace('.','').split(" "):
            indexList.append(self.wordslist.index(n))
        return(indexList)

    def loadIndex(self, indexList):
        randomWords = ''
        for n in indexList:
            randomWords += self.wordslist[n] + ' '
        return(randomWords.strip() + '.')

    def permute(self, threewords):
        wordsList = threewords.lower().replace('.','').split(" ")
        permutationList = []
