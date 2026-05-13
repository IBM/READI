import re

from risk_assessment.classification.identifiers import RegexIdentifierWithSpan


class JapanDrivingLicense(RegexIdentifierWithSpan):
    _prefixes = [
        r"Japan dl#",
        r"Japan dls#",
        r"Japan driver license",
        r"Japan driver’s license",
        r"Japan drivers licenses",
        r"Japan lic#",
        r"Japanese state identification",
        r"Japanese state identification number",
        r"低所得国＃",
        r"免許証",
        r"状態ID",
        r"状態の識別",
        r"状態の識別番号",
        r"運転免許",
        r"運転免許証",
        r"運転免許証番号",
    ]

    def __init__(self) -> None:
        super().__init__(
            "JapanDrivingLicense",
            [
                re.compile(r"^(?:(?:" + r"|".join(JapanDrivingLicense._prefixes) + r")\s*)?(\d{12})$", re.I | re.U),
            ],
        )
