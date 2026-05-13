from risk_assessment.classification.identifiers import JapanAddress


def test_example_from_standard():
    # https://www.japan-guide.com/e/e2224.html
    # https://www.realestate-tokyo.com/living-in-tokyo/japan-info/japanese-address/
    # https://www.upu.int/UPU/media/upu/PostalEntitiesFiles/addressingUnit/jpnEn.pdf
    addresses: list[str] = [
        """2338 Magatake
Zaou-machi
Katta-gun, MIYAGI
989-0851 JAPAN""",  # rural
        """10-23, Mitsugi 1-chome
Musashi-Murayama-shi, TOKYO
231-0012 JAPAN""",  # in city
        """2-17-10, Aioicho
Naka-ku, YOKOHAMA
231-0012 JAPAN""",  # compressed
        """10-23, Kotobukicho
Chuo-ku, NIIGATA
951-8073 JAPAN""",  # city and prefecture are the same
        """JAPAN 112-0001 TOKYO Bunkyo-Ku Hakusan 4-Chome 3-2""",
        """4-3-2, Hakusan
Bunkyo-ku, TOKYO
112-0001
JAPAN""",
        """4-3-2, Hakusan
Bunkyo-ku, TOKYO
〒 112-0001
JAPAN""",
    ]

    identifier = JapanAddress()

    for address in addresses:
        assert identifier.is_of_this_type(address), address


def test_rwd():
    identifier = JapanAddress()

    for address in [
        "〒905-0003 沖縄県名護市旭川７６８",
    ]:
        assert identifier.is_of_this_type(address), address
