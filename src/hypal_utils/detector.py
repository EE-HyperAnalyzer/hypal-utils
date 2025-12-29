from abc import ABC, abstractmethod
from dataclasses import dataclass

from hypal_utils.candles.ohlc import Candle_OHLC


@dataclass
class Detector(ABC):
    name: str

    @abstractmethod
    def read(self) -> Candle_OHLC:
        raise NotImplementedError
