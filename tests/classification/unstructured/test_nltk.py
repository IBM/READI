import nltk
from nltk.tag import PerceptronTagger
from nltk.tokenize import TreebankWordTokenizer

from risk_assessment.classification.unstructured.nltk import NLTKPoSTagger


def test_nltk_pos_tagger():
    nltk.download("averaged_perceptron_tagger")

    text = "And now for something completely different"

    tagger = NLTKPoSTagger(TreebankWordTokenizer(), PerceptronTagger())

    entities = tagger.extract(text)

    assert entities
