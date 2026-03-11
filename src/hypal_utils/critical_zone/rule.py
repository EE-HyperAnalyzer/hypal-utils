from typing import Literal

from pydantic import BaseModel, ConfigDict

from hypal_utils.candles import Candle_OHLC


class ZoneRule(BaseModel):
    type: Literal["NOP"] = "NOP"
    model_config = ConfigDict(
        extra="forbid",
    )

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return False


class ZoneRule_LESS(ZoneRule):
    type: Literal["LESS"] = "LESS"
    value: float

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        arr = [candle.open, candle.high, candle.low, candle.close]
        return any(x < self.value for x in arr)


class ZoneRule_GREATER(ZoneRule):
    type: Literal["GREATER"] = "GREATER"
    value: float

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        arr = [candle.open, candle.high, candle.low, candle.close]
        return any(x > self.value for x in arr)


class ZoneRule_AND(ZoneRule):
    type: Literal["AND"] = "AND"
    lhs: ZoneRule
    rhs: ZoneRule

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return self.lhs.is_satisfied(candle) and self.rhs.is_satisfied(candle)


class ZoneRule_OR(ZoneRule):
    type: Literal["OR"] = "OR"
    lhs: ZoneRule
    rhs: ZoneRule

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return self.lhs.is_satisfied(candle) or self.rhs.is_satisfied(candle)


class ZoneRule_NOT(ZoneRule):
    type: Literal["NOT"] = "NOT"
    rule: ZoneRule

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return not self.rule.is_satisfied(candle)
