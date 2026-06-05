from apps.backend.incidents import review_incident_response


def test_review_response_marks_partial_gas_drill():
    review = review_incident_response("gas.critical", ["inspect_sensor", "evacuate", "bogus"])

    assert review["status"] == "partial"
    assert review["completed_checklist"] == ["evacuate", "inspect_sensor"]
    assert [item["id"] for item in review["missed_checklist"]] == ["ventilate"]
    assert review["unknown_checklist"] == ["bogus"]
    assert review["completion_ratio"] == 0.67
    assert review["score_label"] == "Partial response"
    assert review["next_best_action"] == "Open ventilation or windows"


def test_review_response_handles_not_started_response():
    review = review_incident_response("gas.critical", [])

    assert review["status"] == "not_started"
    assert review["completed_checklist"] == []
    assert [item["id"] for item in review["missed_checklist"]] == ["evacuate", "ventilate", "inspect_sensor"]
    assert review["unknown_checklist"] == []
    assert review["completion_ratio"] == 0.0
    assert review["score_label"] == "Not started"
    assert review["next_best_action"] == "Move people away from the room"


def test_review_response_marks_complete_gas_drill():
    review = review_incident_response("gas.critical", ["inspect_sensor", "ventilate", "evacuate"])

    assert review["status"] == "complete"
    assert review["completed_checklist"] == ["evacuate", "ventilate", "inspect_sensor"]
    assert review["missed_checklist"] == []
    assert review["unknown_checklist"] == []
    assert review["completion_ratio"] == 1.0
    assert review["score_label"] == "Response complete"
    assert review["next_best_action"] == "Response complete"
