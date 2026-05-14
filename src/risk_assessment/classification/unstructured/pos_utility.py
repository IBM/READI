from risk_assessment.classification.unstructured import Entity

_known_pos_types: dict[str, str] = {
    # Universal
    "ADJ": "ADJ",
    "ADP": "ADP",
    "ADV": "ADV",
    "AUX": "AUX",
    "CCONJ": "CCONJ",
    "DET": "DET",
    "INTJ": "INTJ",
    "NOUN": "NOUN",
    "NUM": "NUM",
    "PART": "PART",
    "PRON": "PRON",
    "PUNCT": "PUNCT",
    "SCONJ": "SCONJ",
    "SYM": "SYM",
    "VERB": "VERB",
    "X": "X",
    "DT": "DT",
    "IN": "IN",
    "CC": "CC",
    "TO": "TO",
    "JJ": "ADJ",
    "JJR": "ADJ",
    "JJS": "ADJ",
    "NN": "NOUN",
    "NNP": "NOUN",
    "NNPS": "NOUN",
    "NNS": "NOUN",
    "NPP": "NOUN",
    "RB": "ADV",
    "RBR": "ADV",
    "RBS": "ADV",
    "VB": "VERB",
    "VBD": "VERB",
    "VBG": "VERB",
    "VBN": "VERB",
    "VBP": "VERB",
    "VBZ": "VERB",
    "VRB": "VERB",
}


def part_of_speech_mapper(type: str) -> str:
    return _known_pos_types.get(type.upper(), "X")


def is_verb_or_adverb(entity: Entity) -> bool:
    intersection = entity.pos_tags & {
        "VERB",
        "ADV",
        "DT",
        "CC",
        "IN",
        "TO",
    }

    return bool(len(intersection))
