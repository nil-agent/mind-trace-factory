from mind_trace_factory.models import GroundTruth, Proposition


def build_ground_truth() -> GroundTruth:
    return GroundTruth(
        propositions=[
            Proposition("G01", "Maya generally trusts Noah.", "relationship"),
            Proposition("G02", "Maya and Noah strongly disagreed three days ago.", "world_fact"),
            Proposition("G03", "Maya knows Noah sometimes forgets administrative details.", "belief"),
            Proposition("G04", "Noah told Maya yesterday that he personally checked the attendee list and she was on it.", "observation"),
            Proposition("G05", "The strategy meeting happened without Maya.", "observation"),
            Proposition("G06", "Maya did not receive a calendar invitation.", "observation"),
            Proposition("G07", "Maya does not know whether Noah intentionally excluded her.", "unknown", required_in_story=False),
            Proposition("G08", "Maya does not know whether Priya influenced the outcome.", "unknown", required_in_story=False),
            Proposition("A01", "A simple-forgetfulness explanation should become less plausible after Maya recalls Noah checked the list.", "answer_key", required_in_story=False),
            Proposition("A02", "Intentional exclusion may become more plausible but should remain uncertain.", "answer_key", required_in_story=False),
            Proposition("A03", "Maya has insufficient evidence to blame Priya.", "answer_key", required_in_story=False),
        ]
    )
