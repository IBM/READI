"""Sentence tokenizers for splitting text into sentence-level spans.

Provides a base class and concrete implementations for splitting raw text
into sentence spans, used by the entity-extraction pipeline to limit the
context window fed to individual extractors.

Classes:

- :class:`SentenceTokenizer` — abstract base; override ``span_tokenize``
  and ``sent_tokenize`` in subclasses.
- :class:`JASentenceTokenizerSimple` — regex-based tokenizer supporting
  Japanese and Latin end-of-sentence markers.
- :class:`NLTKSentenceTokenizer` — NLTK Punkt-based tokenizer with optional
  sentence grouping to respect a maximum character budget per chunk.

Note:
    A Stanza-based tokenizer was considered but is not currently implemented.
    The ``import stanza`` line is intentionally commented out as a placeholder.
"""

import re

from nltk import PunktSentenceTokenizer


class SentenceTokenizer:
    """Abstract base class for sentence tokenizers.

    Subclasses must implement :meth:`span_tokenize` and :meth:`sent_tokenize`.
    """

    def __init__(self) -> None:
        pass

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:  # type: ignore
        """Return a list of ``(start, end)`` character spans for each sentence.

        Args:
            text: Input text.

        Returns:
            List of ``(start, end)`` tuples (end is exclusive).
        """
        pass

    def sent_tokenize(self, text: str) -> list[str]:  # type: ignore
        """Return a list of sentence strings.

        Args:
            text: Input text.

        Returns:
            List of sentence strings extracted from *text*.
        """
        pass


class JASentenceTokenizerSimple(SentenceTokenizer):
    """Regex-based sentence tokenizer supporting Japanese and Latin punctuation.

    Splits text at end-of-sentence markers: ``.``, ``!``, ``?``, ``。``,
    newlines, ``？``, and ``！``.

    Attributes:
        eos_pattern: Compiled regex pattern used to detect sentence boundaries.
    """

    eos_pattern = re.compile(r"\.|\!|\?|\。|\n|\？|\！")

    def __init__(self, eos_pattern: str | None = r"\.|\!|\?|\。|\n|\？|\！") -> None:
        """Initialise the tokenizer with a custom end-of-sentence pattern.

        Args:
            eos_pattern: Regex pattern string to detect sentence boundaries.
                Pass ``None`` to keep the class-level default.
        """
        super().__init__()
        if eos_pattern:
            self.eos_pattern = re.compile(eos_pattern)

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        split_points = []

        for m in re.finditer(self.eos_pattern, text):
            split_points.append(m.start())

        split_points = sorted(split_points)

        start = 0
        for split in split_points:
            span = (start, split + 1)
            start = split + 1
            spans.append(span)
        return spans

    def sent_tokenize(self, text: str) -> list[str]:
        spans = self.span_tokenize(text)

        return [text[span[0] : span[1]] for span in spans]


class NLTKSentenceTokenizer(SentenceTokenizer):
    """NLTK Punkt-based sentence tokenizer with optional sentence grouping.

    Texts shorter than *thr* characters are returned as a single span.
    Longer texts are tokenized by NLTK's ``PunktSentenceTokenizer`` and
    optionally grouped into chunks that each stay within the *thr* character
    budget — useful when downstream models have a maximum context length.

    Attributes:
        tokenizer: The underlying NLTK Punkt sentence tokenizer.
        thr: Character length threshold below which the entire text is one span,
            and also the maximum per-group length when grouping is enabled.
        group_sentences: When True, adjacent sentences are merged until the
            group would exceed *thr* characters.
    """

    def __init__(self, group_sentences: bool = True, thr: int = 600) -> None:
        """Initialise the tokenizer.

        Args:
            group_sentences: Whether to merge short consecutive sentences into
                chunks up to *thr* characters. Defaults to True.
            thr: Character length threshold. Texts shorter than this are
                returned as a single span; grouped chunks will not exceed this
                length. Defaults to 600.
        """
        super().__init__()
        self.tokenizer = PunktSentenceTokenizer()
        self.thr = thr
        self.group_sentences = group_sentences

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:
        if len(text) < self.thr:
            return [(0, len(text))]
        spans: list[tuple[int, int]] = [(span[0], span[1]) for span in self.tokenizer.span_tokenize(text)]

        if self.group_sentences:
            span_len: list[int] = [span[1] - span[0] for span in spans]

            span_groups: list[tuple[int, int]] = []
            grouped_span = spans[0]
            grouped_span_len = span_len[0]
            for i in range(1, len(spans)):
                if grouped_span_len + span_len[i] <= self.thr:
                    grouped_span = (grouped_span[0], spans[i][1])
                    grouped_span_len = grouped_span_len + span_len[i]
                else:
                    span_groups.append(grouped_span)
                    grouped_span = spans[i]
                    grouped_span_len = span_len[i]
            span_groups.append(grouped_span)
            # assert span_groups[-1][1] == spans[-1][1], (span_groups[-1], spans[-1])
            return span_groups
        return spans

    def sent_tokenize(self, text: str) -> list[str]:
        spans = self.span_tokenize(text)

        return [text[span[0] : span[1]] for span in spans]
