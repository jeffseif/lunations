import bisect
import dataclasses
import datetime
import enum
import gzip
import json
import math

import pkg_resources

PATH_TO_LUNATIONS_DATA_JSON = pkg_resources.resource_filename(
    __name__,
    "../dat/lunations.json.gz",
)


class LunarPhase(int, enum.Enum):
    WAXING_CRESCENT = 0
    WAXING_GIBBOUS = 1
    WANING_GIBBOUS = 2
    WANING_CRESCENT = 3

    def __str__(self):
        words = self.name.split("_")
        return " ".join(word.capitalize() for word in words)

    @classmethod
    def from_float(cls, flt):
        index = int(flt * len(cls))
        for each in cls:
            if each.value == index:
                return each


class FullMoon(str, enum.Enum):
    # https://skyandtelescope.org/astronomy-resources/native-american-full-moon-names/
    JAN = "wolf"
    FEB = "snow"
    MAR = "worm"
    APR = "pink"
    MAY = "flower"
    JUN = "strawberry"
    JUL = "buck"
    AUG = "sturgeon"
    SEP = "corn"
    OCT = "hunters"
    NOV = "beaver"
    DEC = "cold"

    BLUE = "blue"

    def __str__(self):
        return f"{self.value.capitalize():s} Moon"

    @classmethod
    def fromtimestamp(cls, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        month = dt.strftime("%b")
        return cls[month.upper()]


@dataclasses.dataclass
class Forecast:

    current_timestamp: datetime.datetime
    next_new_moon: datetime.datetime
    previous_new_moon: datetime.datetime
    nearest_full_moon: datetime.datetime
    is_blue_moon: bool
    nearest_full_moon_name: str
    phase_fraction: float
    illumination_fraction: float
    current_phase: str
    next_phase: str
    previous_phase: str

    @classmethod
    def from_new_moons(cls, current_timestamp, new_moons):
        index = bisect.bisect_left(new_moons, current_timestamp)
        next_new_moon = new_moons[index]
        previous_new_moon = new_moons[index - 1]

        nearest_full_moon = previous_new_moon + (next_new_moon - previous_new_moon) / 2
        previous_full_moon = nearest_full_moon - 2 * (
            nearest_full_moon - previous_new_moon
        )
        is_blue_moon = FullMoon.fromtimestamp(
            nearest_full_moon,
        ) == FullMoon.fromtimestamp(previous_full_moon)
        nearest_full_moon_name = (
            FullMoon.BLUE if is_blue_moon else FullMoon.fromtimestamp(nearest_full_moon)
        )

        phase_fraction = (current_timestamp - previous_new_moon) / (
            next_new_moon - previous_new_moon
        )
        illumination_fraction = (1 - math.cos(phase_fraction * 2 * math.pi)) / 2

        current_phase = LunarPhase.from_float(phase_fraction)
        next_phase = cls.get_next_phase(current_phase)
        previous_phase = cls.get_previous_phase(current_phase)

        return cls(
            current_timestamp=datetime.datetime.fromtimestamp(current_timestamp),
            next_new_moon=datetime.datetime.fromtimestamp(next_new_moon),
            previous_new_moon=datetime.datetime.fromtimestamp(previous_new_moon),
            nearest_full_moon=datetime.datetime.fromtimestamp(nearest_full_moon),
            is_blue_moon=is_blue_moon,
            nearest_full_moon_name=str(nearest_full_moon_name),
            phase_fraction=phase_fraction,
            illumination_fraction=illumination_fraction,
            current_phase=str(current_phase),
            next_phase=str(next_phase),
            previous_phase=str(previous_phase),
        )

    @classmethod
    def from_path_to_json(cls, current_timestamp, path_to_json):
        with gzip.open(path_to_json, "rt") as f:
            return cls.from_new_moons(current_timestamp, json.loads(f.read()))

    @staticmethod
    def get_next_phase(this_phase):
        for next_phase in LunarPhase:
            if next_phase.value - this_phase.value in (+1, -3):
                return next_phase

    @staticmethod
    def get_previous_phase(this_phase):
        for previous_phase in LunarPhase:
            if this_phase.value - previous_phase.value in (1, -3):
                return previous_phase


def forecast_for_current_timestamp(current_timestamp=None):
    if current_timestamp is None:
        current_timestamp = datetime.datetime.now().timestamp()
    return dataclasses.asdict(
        Forecast.from_path_to_json(
            current_timestamp=current_timestamp,
            path_to_json=PATH_TO_LUNATIONS_DATA_JSON,
        ),
    )


def cli(args):
    print(
        forecast_for_current_timestamp(current_timestamp=args.forecast_epoch_timestamp),
    )
