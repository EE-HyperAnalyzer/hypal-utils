from pydantic import BaseModel, ConfigDict


class Candle_OHLC(BaseModel):
    model_config = ConfigDict(extra="forbid")

    open: float
    high: float
    low: float
    close: float
