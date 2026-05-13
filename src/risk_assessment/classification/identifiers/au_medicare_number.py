from risk_assessment.classification.identifiers import Identifier


class AustralianMedicareNumber(Identifier):
    checksum_weights = [1, 3, 7, 9, 1, 3, 7, 9]

    def is_of_this_type(self, text: str) -> bool:
        text = text.strip()
        text = text.replace(" ", "")
        if len(text) != 10:
            return False
        if not text.isnumeric():
            return False
        if int(text[0]) not in {2, 3, 4, 5, 6}:
            return False

        checksum = 0
        for item, weight in zip(text[:-2], self.checksum_weights, strict=False):
            checksum += int(item) * weight

        check_digit = checksum % 10
        if check_digit != int(text[8]):
            return False

        return True
