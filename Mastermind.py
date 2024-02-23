import itertools
import numpy as np
import json
import matplotlib.pyplot as plt


def showentropy(df):
    plt.figure(figsize=(20, 8))
    ax = plt.axes()
    ax.bar(df.keys(), df.values())

    for key in df.keys():
        plt.text(key, df[key], round(df[key], 2))

    plt.show()


def codemaster(code, guess):
    reply = []
    newcode = list(code)
    tempguess = list(guess)
    for i in range(4):
        if code[i] == guess[i]:
            newcode.remove(code[i])
            tempguess.remove(code[i])
            reply.append(8)
    for peg in newcode.copy():
        if peg in tempguess:
            reply.append(7)
            tempguess.remove(peg)

    while len(reply) != 4:
        reply.append(9)

    return tuple(sorted(reply))


class Mastermind:
    mapping = {1: "red", 2: "green", 3: "blue", 4: "yellow", 5: "white", 6: "black"}
    response = {7: "white", 8: "black", 9: "none"}

    basepermutations = set(itertools.product(mapping.keys(), repeat=4))
    allpermutations = basepermutations.copy()
    allresults = list(itertools.combinations_with_replacement(response.keys(), 4))

    codeentropy = {}

    df = None

    def __init__(self):
        f = open("firstmove.json", "r")
        self.df = json.load(f)
        f.close()

    def filtered(self, guess, result):
        allpossibleresults = set(itertools.permutations(result))
        newpermutations = set()
        for r in allpossibleresults:
            temppermutations = self.allpermutations.copy()
            loose = {}
            loosei = {}
            imposvalue = {}
            imposi = {}
            stickyi = {}
            colorv = {}
            for i in range(4):
                if r[i] == 7:
                    loosei[i] = guess[i]
                    if guess[i] not in loose.keys():
                        loose[guess[i]] = 1
                    else:
                        loose[guess[i]] += 1
                    if guess[i] not in colorv.keys():
                        colorv[guess[i]] = 1
                    else:
                        colorv[guess[i]] += 1

                if r[i] == 8:
                    stickyi[i] = guess[i]
                    if guess[i] not in colorv.keys():
                        colorv[guess[i]] = 1
                    else:
                        colorv[guess[i]] += 1

                if r[i] == 9:
                    imposi[i] = guess[i]
                    if guess[i] not in imposvalue.keys():
                        imposvalue[guess[i]] = 1
                    else:
                        imposvalue[guess[i]] += 1

            for code in temppermutations.copy():
                for peg in colorv.keys():
                    if colorv[peg] > code.count(peg):
                        temppermutations.discard(code)
                        break

                if code not in temppermutations:
                    continue

                for peg in imposvalue.keys():
                    # It is 9
                    if (guess.count(peg) - imposvalue[peg]) < code.count(peg):
                        temppermutations.discard(code)
                        break

                if code not in temppermutations:
                    continue

                for i in imposi.keys():
                    # If it is not 9 it would be a 7 or an 8
                    if code[i] == imposi[i]:
                        temppermutations.discard(code)
                        break

                if code not in temppermutations:
                    continue

                for i in stickyi.keys():
                    if code[i] != stickyi[i]:
                        temppermutations.discard(code)
                        break

                if code not in temppermutations:
                    continue

                for i in loosei.keys():
                    if code[i] == loosei[i]:
                        temppermutations.discard(code)
                        break

                if code not in temppermutations:
                    continue

                for peg in loose.keys():
                    if code.count(peg) < loose[peg]:
                        temppermutations.discard(code)
                        break

            newpermutations.update(temppermutations)

        return newpermutations

    def entropy(self, permutation):
        """
        To do this, We have to go through all possible results that this guess can take, and then see by how much our
        sample size is reduced given that new information.
        """
        total = 0
        for result in self.allresults:
            p = len(self.filtered(permutation, result)) / len(self.allpermutations)
            # print('probs', p)
            if p != 0:
                x = p * np.log2(p)
                total -= x
        # print(total)
        # print(permutation, p*np.log2(p))
        return total

    def makeguess(self, result=None):
        """
        Everytime we make a guess, we try to find the guess that will maximise the expected information that we will get
        In other words, minimising uncertainty.
        """
        if result is None:
            bestguess = []
            mentropy = max(self.df.values())
            for g in self.df.keys():
                if self.df[g] == mentropy:
                    bestguess.append(g)
            return eval(np.random.choice(bestguess))

        guesses = {}
        # count = 1
        for permutation in self.allpermutations:
            # count+=1
            guesses[str(permutation)] = self.entropy(permutation)

        # print(guesses)
        self.codeentropy = guesses

        bestguess = []
        mentropy = max(guesses.values())
        if mentropy == 0:
            for g in self.allpermutations:
                if guesses[str(g)] == mentropy:
                    bestguess.append(str(g))
        else:
            for g in guesses.keys():
                if guesses[g] == mentropy:
                    bestguess.append(g)

        tempguess = np.random.choice(bestguess)
        while tempguess not in self.allpermutations:
            if len(bestguess) == 1:
                break
            bestguess.remove(tempguess)
            tempguess = np.random.choice(bestguess)

        return eval(tempguess)

    def pprint(self, guess, result):
        if result is None:
            showentropy(self.df)
            print(guess, "Expected information:", self.df[str(guess)])
        else:
            showentropy(self.codeentropy)
            print(self.codeentropy)
            print(guess, "Expected information:", self.codeentropy[str(guess)])

    def game(self):
        result = None
        self.allpermutations = self.basepermutations.copy()
        countguess = 0
        currinfo = 0
        maxinfo = -np.log2(1 / len(self.basepermutations))
        while result != (8, 8, 8, 8):
            print("Current information:", currinfo)
            print("Current uncertainty:", maxinfo - currinfo)

            guess = self.makeguess(result)
            self.pprint(guess, result)
            countguess += 1

            result = tuple(sorted(eval(input())))
            print("Result:", result)
            setsize = len(self.allpermutations)
            self.allpermutations = self.filtered(guess, result)

            inforec = -np.log2(len(self.allpermutations) / setsize)
            currinfo += inforec
            print("Information received:", inforec)
        return countguess

    def firstmove(self):
        guesses = {}
        count = 1
        for permutation in self.allpermutations:
            print(count)
            count += 1
            guesses[str(permutation)] = self.entropy(permutation)

        showentropy(guesses)
        return guesses

    def evaluate(self):
        allgamedata = {}
        for c in self.basepermutations:
            self.allpermutations = self.basepermutations.copy()
            print(c, end=" ")

            guess = self.makeguess(None)
            result = codemaster(c, guess)
            count = 1
            while result != (8, 8, 8, 8):
                self.allpermutations = self.filtered(guess, result)

                guess = self.makeguess(result)

                result = codemaster(c, guess)
                count += 1

            allgamedata[c] = count
            print(count)

        return allgamedata

game = Mastermind()
game.game()