# A slightly more readable version of wordle-curses

import curses, random, time
from dictionary import defnsyn

words = open("words.txt", "r").read().split("\n")
colorPairBindings = {"c": 2, "w": 3, "n": 7, "u": 6}
completionMessages = [
    "",
    "Genius!",
    "Unbelievable!",
    "Splendid!",
    "Amazing!",
    "Great!",
    "Good!"
]

# Draw one row of the board
# Generates new row + colours alphabets in
def writeWord(s, word, remark, y):
    s.addstr(y, 0, "│ │ │ │ │ │\n├─┼─┼─┼─┼─┤")
    for i, (letter, color) in enumerate(zip(word, remark)):
        s.addstr(
            y,
            i * 2 + 1,
            letter.upper(),
            curses.color_pair(colorPairBindings[color]),
        )

# Score a word
def score(guess, word, alphabet):
    res = [" "] * 5
    counts = [0] * 26

    # First process correct letters
    for i, c in enumerate(guess):
        if c == word[i]: #checking if guess letter corresponds to letter of the same index in chosen word
            charIndex = ord(c) - 97 # 97 corresponds to a - gives alphabet number. (eg. h = 8)
            counts[charIndex] += 1
            res[i] = "c"  # correct spot
            alphabet[charIndex] = "c"

    # Then handle wrong and nonpresent letters
    for i, c in enumerate(guess):
        if c != word[i]:
            charIndex = ord(c) - 97
            counts[charIndex] += 1
            if c in word and word.count(c) >= counts[charIndex]: # if freq of letters in guess lesser than freq in word
                res[i] = "w"  # wrong spot
                if alphabet[charIndex] != "c":
                    alphabet[charIndex] = "w"
            else:
                res[i] = "n"  # not in word
                alphabet[charIndex] = "n"

    return "".join(res), alphabet

# Render current board
# Updates alphabet use state + renders colours of guesses
def render(s, guesses, alphabet):
    s.addstr(0, 0, "=== WORDLE ===", curses.color_pair(2))
    for i, c in enumerate(alphabet):
        s.addstr(
            1 + int(i // 7),
            (i % 7) * 2,
            chr(65 + i),
            curses.color_pair(colorPairBindings[c]),
        )
    s.addstr(6, 0, "╭─┬─┬─┬─┬─╮")
    for i, (w, r) in enumerate(guesses):
        writeWord(s, w, r, i * 2 + 7)
    s.addstr(len(guesses) * 2 + 10, 0, "             ")

# Accept word from user input
def getWord(s, y):
    word = ""
    while True:
        writeWord(s, word, "u" * len(word), y) # u = default blue colour
        k = s.getch()
        if k == 8: # backspace
            word = word[:-1]
        elif k == 27: # esc
            exit()
        elif chr(k) == "\n" and len(word) == 5:
            return word
        elif chr(k).isalpha() and len(word) < 5:
            word += chr(k)

# Run one game of Wordle
def run(s):
    s.clear()
    word = random.choice(words) #chosen word
    print("Chosen word: ", word)
    defn, synonyms = defnsyn(word)
    guesses = [] # stores each guess and its result
    alphabet = ["u"] * 26 # current status of each letter whether used or not
    # c = correct positon, w = correct letter but not position, n = wrong letter, u = not used
    # "ccccc" means all letters are in correct spot
    while not (len(guesses)) or (guesses[-1][1] != "ccccc" and len(guesses) < 6):
        render(s, guesses, alphabet) # Update current state of board from start
        guess = getWord(s, len(guesses) * 2 + 7).lower()
        if not (guess in words): # Check if given word is valid
            s.addstr(len(guesses) * 2 + 10, 0, "INVALID WORD", curses.color_pair(1))
            s.refresh()
            time.sleep(1)
            continue
        res, alphabet = score(guess, word, alphabet)
        guesses.append([guess, res])
    render(s, guesses, alphabet) #Renders final board

    # Ending spiel
    s.addstr(len(guesses) * 2 + 6, 0, "╰─┴─┴─┴─┴─╯")
    if guesses[-1][1] != "ccccc":
        s.addstr(len(guesses) * 2 + 8, 0, "No more tries - the word was " + word.upper())
    else:
        s.addstr(
            len(guesses) * 2 + 8,
            0,
            completionMessages[len(guesses)]
        )
    if defn and synonyms:
        s.addstr(len(guesses) * 2 + 9, 0, word+": ", curses.color_pair(2))
        synonyms = ", ".join(synonyms)
        s.addstr(len(guesses) * 2 + 9, 8, defn)
        s.addstr(len(guesses) * 2 + 10, 0, "Some synonyms: ", curses.color_pair(2))
        s.addstr(len(guesses) * 2 + 10, 16, synonyms)
    s.addstr(len(guesses) * 2 + 11, 0, "[esc] to quit, [enter] to play again", curses.color_pair(3))

# Main function
def main(s):
    # Initialize colors
    for p in [
        (1, curses.COLOR_RED),
        (2, curses.COLOR_GREEN),
        (3, curses.COLOR_YELLOW),
        (7, curses.COLOR_WHITE),
        (6, curses.COLOR_CYAN),
    ]:
        curses.init_pair(p[0], p[1], curses.COLOR_BLACK)
    # Run game
    while True:
        run(s)
        if s.getch() == 27: # esc
            break

if __name__ == "__main__":
    curses.wrapper(main)