from pydantic import BaseModel, ConfigDict


class Candle_OHLC(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    unit: str
    open: float
    high: float
    low: float
    close: float
    timestamp: int
