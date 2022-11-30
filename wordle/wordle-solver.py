words = open("wordle\\words.txt").read().split()

guesslist = []
maxguesses = 6
wantedletters = []
uselessletters = []
correctletters = ["-"] * 5

while maxguesses:
    try:
        correctguess = input(
            "\nEnter correct letter positions (use - for other letters): "
        ).lower()
        uselessguess = input("Enter all incorrect letters without space: ").lower()
        wantedguess = input("Enter all letters of incorrect postiions: ").lower()

        correctletters = list(correctguess)
        for i in uselessguess:
            if i not in uselessletters:
                uselessletters.append(i)
        for i in wantedguess:
            if i not in wantedletters:
                wantedletters.append(i)

        subsetwanted = []
        for i in words:
            if set(wantedletters).issubset(set(i)):
                subsetwanted.append(i)
        print("First filter", subsetwanted)
        for i in uselessletters:
            for j in subsetwanted:
                if j.count(i):
                    subsetwanted.remove(j)

        print("Second filter: ", subsetwanted)

        print(correctletters)
        temp = []
        for i in range(len(correctletters)):
            for j in range(len(subsetwanted)):
                if correctletters[i] == "-":
                    continue
                else:
                    print(i, j, correctletters[i], subsetwanted[j][i])
                    if correctletters[i] == subsetwanted[j][i]:
                        temp.append(subsetwanted[j])
        subsetwanted = temp.copy()
        print("Third filter: ", subsetwanted)

    except KeyboardInterrupt:
        print("\n\nThe word was found!")
        break
    maxguesses -= 1
