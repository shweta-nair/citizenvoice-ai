"""
CitizenVoice AI - Text Preprocessing Utilities

Note on NLTK: rather than depending on nltk.download() at runtime (which
requires internet access and can fail silently on locked-down machines),
this module implements lightweight, dependency-free cleaning + tokenization
+ keyword extraction. NLTK is still listed in requirements.txt and can be
swapped in for stemming/lemmatization if desired, but the pipeline does not
require it to function.
"""

import re
from collections import Counter

# A compact stopword list covering common English function words plus a few
# call-transcript filler words (executive/citizen boilerplate).
STOPWORDS = set("""
a an the and or but if while is are was were be been being have has had
do does did doing this that these those i you he she it we they me him her
us them my your his its our their to of in on at for with as by from up down
out about into over under again further then once here there when where why
how all any both each few more most other some such no nor not only own same
so than too very s t can will just don should now ll ve re d m o
hello hi good morning afternoon evening calling call please thank thanks
yes no okay ok regarding issue area today help executive citizen helpline
support team
""".split())

CALL_BOILERPLATE_PATTERN = re.compile(
    r"(support executive:|citizen:)", re.IGNORECASE
)


def strip_speaker_labels(text):
    """Remove 'Support Executive:' / 'Citizen:' labels, keep the spoken content."""
    text = CALL_BOILERPLATE_PATTERN.sub(" ", text)
    return text


def clean_text(text):
    """Lowercase, strip speaker labels, remove punctuation/digits, collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = strip_speaker_labels(text)
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text):
    cleaned = clean_text(text)
    tokens = [t for t in cleaned.split() if t not in STOPWORDS and len(t) > 2]
    return tokens


def preprocess_for_vectorizer(text):
    """Returns a cleaned, stopword-free string ready for TF-IDF vectorization."""
    return " ".join(tokenize(text))


def extract_keywords(text, top_n=8):
    """Simple frequency-based keyword extraction from a single transcript."""
    tokens = tokenize(text)
    if not tokens:
        return []
    counts = Counter(tokens)
    return [w for w, _ in counts.most_common(top_n)]


def extract_corpus_keywords(texts, top_n=20):
    """Aggregate keyword frequency across many transcripts (for dashboard charts)."""
    counter = Counter()
    for t in texts:
        counter.update(tokenize(t))
    return counter.most_common(top_n)


LOCATION_WORDS = {
    "ernakulam", "thiruvananthapuram", "kozhikode", "thrissur", "alappuzha",
    "kannur", "kottayam", "palakkad", "idukki", "wayanad",
}


def extract_locations(text):
    tokens = set(clean_text(text).split())
    return sorted(tokens.intersection(LOCATION_WORDS))
