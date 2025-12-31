from pydantic import BaseModel, ConfigDict

from hypal_utils.detector import Detector


class ProtocolMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Ok(ProtocolMessage):
    pass


class Error(ProtocolMessage):
    reason: str


class RegisterDetectors(ProtocolMessage):
    detectors: list[Detector]
