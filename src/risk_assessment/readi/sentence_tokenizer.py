import re

from nltk import PunktSentenceTokenizer

# import stanza


class SentenceTokenizer:
    def __init__(self) -> None:
        pass

    def span_tokenize(self, text: str) -> list[tuple[int, int]]:  # type: ignore
        pass

    def sent_tokenize(self, text: str) -> list[str]:  # type: ignore
        pass


class JASentenceTokenizerSimple(SentenceTokenizer):
    eos_pattern = re.compile(r"\.|\!|\?|\。|\n|\？|\！")

    def __init__(self, eos_pattern: str | None = r"\.|\!|\?|\。|\n|\？|\！") -> None:
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
    def __init__(self, group_sentences: bool = True, thr: int = 600) -> None:
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
