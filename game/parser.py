"""
Natural language command parser for The Forgotten Depths.
Handles Infocom-style verb-noun commands with synonym resolution.
"""

DIRECTION_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "u": "up", "d": "down",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
}

DIRECTIONS = {
    "north", "south", "east", "west", "up", "down",
    "northeast", "northwest", "southeast", "southwest",
}

VERB_SYNONYMS = {
    "look": "look",
    "l": "look",
    "examine": "examine",
    "x": "examine",
    "inspect": "examine",
    "study": "examine",
    "search": "examine",
    "take": "take",
    "get": "take",
    "grab": "take",
    "pick": "take",
    "drop": "drop",
    "discard": "drop",
    "put": "drop",
    "leave": "drop",
    "inventory": "inventory",
    "i": "inventory",
    "use": "use",
    "apply": "use",
    "open": "open",
    "unlock": "open",
    "close": "close",
    "shut": "close",
    "push": "push",
    "press": "push",
    "pull": "pull",
    "yank": "pull",
    "turn": "turn",
    "rotate": "turn",
    "twist": "turn",
    "spin": "turn",
    "read": "read",
    "talk": "talk",
    "speak": "talk",
    "ask": "talk",
    "say": "say",
    "go": "go",
    "walk": "go",
    "move": "go",
    "run": "go",
    "climb": "climb",
    "tie": "tie",
    "attach": "tie",
    "insert": "insert",
    "place": "place",
    "set": "set",
    "light": "light",
    "fill": "fill",
    "pour": "fill",
    "help": "help",
    "hint": "hint",
    "quit": "quit",
    "exit": "quit",
    "q": "quit",
    "save": "save",
    "load": "load",
    "restore": "load",
    "score": "score",
    "wait": "wait",
    "z": "wait",
    "listen": "listen",
    "smell": "smell",
    "touch": "touch",
    "feel": "touch",
    "taste": "taste",
    "eat": "eat",
    "drink": "drink",
    "jump": "jump",
    "swim": "swim",
    "enter": "enter",
    "step": "step",
}

ARTICLES = {"the", "a", "an", "some", "my"}
PREPOSITIONS = {"on", "in", "with", "to", "at", "from", "into", "onto", "under", "behind", "through", "across"}
FILLER = {"up", "down"}  # "pick up" -> take


class ParsedCommand:
    def __init__(self, verb=None, noun=None, prep=None, obj=None, raw=""):
        self.verb = verb
        self.noun = noun
        self.prep = prep
        self.obj = obj
        self.raw = raw

    def __repr__(self):
        return f"Cmd({self.verb} {self.noun or ''} {self.prep or ''} {self.obj or ''})".strip()


def parse(raw_input):
    raw = raw_input.strip().lower()
    if not raw:
        return ParsedCommand(raw=raw)

    tokens = raw.split()

    # Single direction shortcut
    if len(tokens) == 1:
        word = tokens[0]
        expanded = DIRECTION_ALIASES.get(word, word)
        if expanded in DIRECTIONS:
            return ParsedCommand(verb="go", noun=expanded, raw=raw)

    # Strip articles
    tokens = [t for t in tokens if t not in ARTICLES]
    if not tokens:
        return ParsedCommand(raw=raw)

    # Resolve verb
    first = tokens[0]
    verb = VERB_SYNONYMS.get(first)

    if verb is None:
        expanded = DIRECTION_ALIASES.get(first, first)
        if expanded in DIRECTIONS:
            return ParsedCommand(verb="go", noun=expanded, raw=raw)
        return ParsedCommand(raw=raw)

    tokens = tokens[1:]

    # "go north" style
    if verb == "go" and tokens:
        dir_word = DIRECTION_ALIASES.get(tokens[0], tokens[0])
        if dir_word in DIRECTIONS:
            return ParsedCommand(verb="go", noun=dir_word, raw=raw)
        return ParsedCommand(verb="go", noun=" ".join(tokens), raw=raw)

    # Handle "pick up X" -> take X
    if verb == "take" and tokens and tokens[0] in FILLER:
        tokens = tokens[1:]

    # Handle "look at X" -> examine X
    if verb == "look" and tokens and tokens[0] in ("at", "around", "in", "inside"):
        if tokens[0] == "around":
            return ParsedCommand(verb="look", raw=raw)
        verb = "examine"
        tokens = tokens[1:]

    # Handle "talk to X"
    if verb == "talk" and tokens and tokens[0] == "to":
        tokens = tokens[1:]

    if not tokens:
        return ParsedCommand(verb=verb, raw=raw)

    # Find preposition to split noun and indirect object
    # e.g., "use key on door" -> verb=use, noun=key, prep=on, obj=door
    prep_idx = None
    for i, t in enumerate(tokens):
        if t in PREPOSITIONS and i > 0:
            prep_idx = i
            break

    if prep_idx is not None:
        noun = " ".join(tokens[:prep_idx])
        prep = tokens[prep_idx]
        obj = " ".join(tokens[prep_idx + 1:]) if prep_idx + 1 < len(tokens) else None
        return ParsedCommand(verb=verb, noun=noun, prep=prep, obj=obj, raw=raw)

    noun = " ".join(tokens)
    return ParsedCommand(verb=verb, noun=noun, raw=raw)
