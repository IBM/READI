from risk_assessment.classification.identifiers import VoterID


def test_us_voter_id():
    valid_voter_ids = [
        "voter ID number is 601506758.",
        "voter ID number is 3669524",
        "voter ID number is 4277612",
        "voter ID number is 7102685",
        " voter ID number is 423818.",
    ]
    identifier = VoterID()

    for voter_id in valid_voter_ids:
        assert identifier.is_of_this_type(voter_id), voter_id
