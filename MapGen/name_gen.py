#!/usr/bin/env python3

import random

class Region:
    """docstring for Region."""
    def __init__(self,location = None):
        random.seed()
        self.name = generate_name()
        self.location = location
        self.cities = []

    def regional_name(self):
        # regional_name = generate_name() # self.name[:3] + generate_name()[3:]

        return generate_name()

def generate_name():
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    wordlist = []

    with open ("words", 'r') as fo:
        for word in fo:
            if len(word) < 5:
                continue
            else:
                wordlist.append(word.strip())

    namelength = random.randrange(4)
    pref = random.choice(wordlist)[0:3]
    pref = pref[0].upper() + pref[1:3]

    if random.random() > 0.5:
        suff = random.choice(wordlist)[-3:]
    else:
        suff = random.choice(wordlist)[:3]

    for i in range(namelength):
        pref = pref + random.choice(alphabet)

    name = pref + suff

    return name

if __name__ == '__main__':
    r = Region()
    print([r.regional_name() for _ in range(5)])
    #print(generate_name())
