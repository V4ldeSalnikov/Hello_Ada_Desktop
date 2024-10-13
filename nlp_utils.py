import spacy
from textblob import TextBlob
from spellchecker import SpellChecker  # Import pyspellchecker for Danish corrections
import random
# Load the small English model from spaCy
nlp = spacy.load("en_core_web_sm")

# Initialize Danish spell checker
danish_spellchecker = SpellChecker(language=None)  # Custom dictionary
# Add Danish words to the spell checker dictionary
DANISH_WORDS = {
    "gå", "løb", "hop", "skifte", "flyt", "springe", "højre", "venstre", "op", "ned",
    "rød", "grøn", "blå", "gul", "lilla", "orange", "pink", "sort", "hvid", "grå", "farve"
}
danish_spellchecker.word_frequency.load_words(DANISH_WORDS)

# Define possible direction and action keywords for English and Danish
DIRECTION_KEYWORDS = ["right", "left", "up", "down", "højre", "venstre", "op", "ned"]
ACTION_KEYWORDS = ["move", "go", "step", "run", "walk", "jump", "hop", "leap", "change", "gå", "løb", "hop", "skift",
                   "flyt", "springe"]

# Synonym mappings for both English and Danish
ACTION_SYNONYMS = {
    "go": "move", "step": "move", "run": "move", "walk": "move", "hop": "jump", "leap": "jump", "skifte": "change",
    "gå": "move", "flyt": "move", "løb": "run", "springe": "jump"
}

DANISH_TO_ENGLISH_DIRECTIONS = {
    "højre": "right",
    "venstre": "left",
    "op": "up",
    "ned": "down"
}

# List of colors and their RGB values (Danish and English)
COLOR_KEYWORDS = {
    "rød": (255, 0, 0), "grøn": (0, 255, 0), "blå": (0, 0, 255), "gul": (255, 255, 0), "lilla": (128, 0, 128),
    "orange": (255, 165, 0), "pink": (255, 182, 193), "sort": (0, 0, 0), "hvid": (255, 255, 255),
    "grå": (200, 200, 200),
    "red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255), "yellow": (255, 255, 0), "purple": (128, 0, 128),
    "black": (0, 0, 0), "white": (255, 255, 255), "gray": (200, 200, 200)
}


def detect_language(text):
    """
    Detects if the input is more likely Danish or English based on the presence of known Danish words.
    """
    danish_word_count = sum(1 for word in text.split() if word.lower() in DANISH_WORDS)
    return "danish" if danish_word_count > 0 else "english"


def correct_typo_danish(text):
    """
    Corrects typos in Danish using the pyspellchecker library.
    """
    corrected_words = []
    for word in text.split():
        # Correct only if the word is misspelled
        corrected_word = danish_spellchecker.correction(word)
        corrected_words.append(corrected_word)
    return " ".join(corrected_words)


def correct_typo_with_textblob(text, language):
    """
    Corrects typos based on the identified language.
    If Danish, use the custom Danish spellchecker. If English, use TextBlob.
    """
    if language == "danish":
        # Use Danish spell correction
        return correct_typo_danish(text)
    else:
        return str(TextBlob(text).correct())  # Use normal correction for English


def get_synonym_action(action):
    """
    Map synonyms (both English and Danish) to standard actions.
    """
    return ACTION_SYNONYMS.get(action, action)  # Return synonym or the action itself if no match


def translate_danish_to_english(action, direction, color):
    """
    Translates Danish action and direction to English equivalent.
    """
    if action in ACTION_SYNONYMS:  # Use synonym map for actions (both English and Danish)
        action = get_synonym_action(action)
    if direction in DANISH_TO_ENGLISH_DIRECTIONS:
        direction = DANISH_TO_ENGLISH_DIRECTIONS[direction]
    return action, direction, color


def extract_direction_action_color(doc):
    """
    Extracts direction, action, and color based on the user's input using dependency parsing and POS tagging.
    Also handles Danish inputs and maps them to English equivalents.
    """
    direction = None
    action = None
    color = None

    for token in doc:
        print(f"Token: {token.text}, Lemma: {token.lemma_}")  # Debugging to check token properties

        # Check for action in both English and Danish with synonyms
        if token.text.lower() in ACTION_KEYWORDS or token.text.lower() in ACTION_SYNONYMS:
            action = get_synonym_action(token.text.lower())
        elif token.text.lower() in DIRECTION_KEYWORDS:
            direction = token.text.lower()
        elif token.text.lower() in COLOR_KEYWORDS:
            color = token.text.lower()

    # Translate Danish directions to English if needed
    action, direction, color = translate_danish_to_english(action, direction, color)

    return action, direction, color


def normalize_command(input_text):
    """
    Normalize user input to a standard command using spaCy NLP model and spell correction.
    Handles both English and Danish inputs, with synonym handling and typo correction.
    """
    # First, detect if the input is likely Danish or English
    detected_language = detect_language(input_text)

    # Correct any typos in the input based on detected language
    corrected_text = correct_typo_with_textblob(input_text, detected_language)
    print(
        f"Original input: {input_text}, Corrected input: {corrected_text}, Language: {detected_language}")  # Debugging line

    # Now process the corrected text with spaCy
    doc = nlp(corrected_text.lower().strip())
    print(f"Tokens: {[token.text for token in doc]}")  # Debugging line to check tokens

    # Extract action, direction, and color from the user input
    action, direction, color = extract_direction_action_color(doc)

    print(f"Extracted - Action: {action}, Direction: {direction}, Color: {color}")  # Debugging line

    # Handle color change command with or without a color specified
    if action == "change" and color:
        return f"change color {color}"
    elif action == "change" and not color:
        return "change color random"

    # Handle jump command without direction
    if action == "jump":
        return "jump"

    # Handle recognized direction without an action (this ensures "left" and "right" are treated equally)
    if direction and not action:
        if direction == "left":
            return "move left"
        elif direction == "right":
            return "move right"

    # Map the extracted direction and action to predefined commands
    if action and direction:
        return f"{action} {direction}"

    # If no match is found, return an error message
    return "error: unrecognized command"
