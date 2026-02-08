from pydantic import BaseModel, ConfigDict

from hypal_utils.candles import Candle_OHLC


class SensorData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    axis: str
    sensor: str
    source: str
    candle: Candle_OHLC
    timestamp: int
