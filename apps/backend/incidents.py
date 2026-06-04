from __future__ import annotations

from typing import Final, TypedDict

from pydantic import BaseModel, Field

MAX_RESPONSE_TEXT_LENGTH: Final = 500


class ChecklistItem(TypedDict):
    id: str
    label: str


class ResponseGuidance(TypedDict):
    summary: str
    recommended_action: str
    checklist: list[ChecklistItem]


class AlertResponsePayload(BaseModel):
    checklist: list[str] = Field(default_factory=list)
    note: str = Field(default="", max_length=MAX_RESPONSE_TEXT_LENGTH)
    evidence: str = Field(default="", max_length=MAX_RESPONSE_TEXT_LENGTH)


GUIDANCE_BY_CODE: Final[dict[str, ResponseGuidance]] = {
    "gas.critical": {
        "summary": "Critical gas level detected",
        "recommended_action": "Evacuate, ventilate the room, and inspect the gas sensor before re-entry.",
        "checklist": [
            {"id": "evacuate", "label": "Move people away from the room"},
            {"id": "ventilate", "label": "Open ventilation or windows"},
            {"id": "inspect_sensor", "label": "Check the gas sensor and wiring"},
        ],
    },
    "gas.warning": {
        "summary": "Gas level warning",
        "recommended_action": "Ventilate the room and watch for a rising gas trend.",
        "checklist": [
            {"id": "ventilate", "label": "Ventilate the room"},
            {"id": "inspect_sensor", "label": "Check the gas sensor position"},
        ],
    },
    "temperature.critical": {
        "summary": "Critical temperature detected",
        "recommended_action": "Remove heat sources and confirm the room is safe before re-entry.",
        "checklist": [
            {"id": "remove_heat", "label": "Remove or isolate heat source"},
            {"id": "inspect_room", "label": "Inspect the affected room"},
            {"id": "check_sensor", "label": "Confirm the temperature sensor reading"},
        ],
    },
    "temperature.warning": {
        "summary": "Temperature warning",
        "recommended_action": "Check airflow and confirm the temperature trend.",
        "checklist": [
            {"id": "check_airflow", "label": "Check room airflow"},
            {"id": "check_sensor", "label": "Confirm the temperature sensor reading"},
        ],
    },
}

FALLBACK_GUIDANCE: Final[ResponseGuidance] = {
    "summary": "Investigate alert",
    "recommended_action": "Inspect the affected area and confirm the sensor is reporting accurately.",
    "checklist": [
        {"id": "inspect_area", "label": "Inspect the affected area"},
        {"id": "check_sensor", "label": "Check the reporting sensor"},
    ],
}


def guidance_for_code(code: str) -> ResponseGuidance:
    return GUIDANCE_BY_CODE.get(code, FALLBACK_GUIDANCE)


def clean_response_text(value: str) -> str:
    return value.strip()[:MAX_RESPONSE_TEXT_LENGTH]
