from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from hypal_utils.candles.ohlc import Candle_OHLC


class Detector(BaseModel, ABC):
    model_config = ConfigDict(extra="forbid")

    name: str
    unit: str

    @abstractmethod
    def read(self) -> Candle_OHLC:
        raise NotImplementedError
