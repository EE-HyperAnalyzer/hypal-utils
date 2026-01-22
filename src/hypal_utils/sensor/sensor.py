import time
from dataclasses import dataclass

from hypal_utils.candles.ohlc import Candle_OHLC
from hypal_utils.detector import Detector
from hypal_utils.sensor.data import SensorData


@dataclass
class Sensor:
    name: str
    source: str
    detectors: tuple[Detector, ...]

    def read(self) -> SensorData:
        values: tuple[Candle_OHLC, ...] = tuple(
            detector.read() for detector in self.detectors
        )
        return SensorData(
            name=self.name,
            source=self.source,
            values=values,
            timestamp=int(time.time()),
        )
