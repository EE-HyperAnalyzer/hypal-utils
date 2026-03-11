from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict

from hypal_utils.candles import Candle_OHLC


class ZoneRule(BaseModel, ABC):
    model_config = ConfigDict(
        extra="forbid",
    )

    @abstractmethod
    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: ({vars(self)})"


class ZoneRule_LESS(ZoneRule):
    value: float

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        arr = [candle.open, candle.high, candle.low, candle.close]
        return any(x < self.value for x in arr)


class ZoneRule_GREATER(ZoneRule):
    value: float

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        arr = [candle.open, candle.high, candle.low, candle.close]
        return any(x > self.value for x in arr)


class ZoneRule_AND(ZoneRule):
    lhs: ZoneRule
    rhs: ZoneRule

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return self.lhs.is_satisfied(candle) and self.rhs.is_satisfied(candle)


class ZoneRule_OR(ZoneRule):
    lhs: ZoneRule
    rhs: ZoneRule

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return self.lhs.is_satisfied(candle) or self.rhs.is_satisfied(candle)


class ZoneRule_NOT(ZoneRule):
    rule: ZoneRule

    def is_satisfied(self, candle: Candle_OHLC) -> bool:
        return not self.rule.is_satisfied(candle)
