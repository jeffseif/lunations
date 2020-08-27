import bisect
import datetime
import enum
import gzip
import json
import math

from lunations import PATH_TO_LUNATIONS_DATA_JSON


class LunarPhase(int, enum.Enum):
    WAXING_CRESCENT = 0
    WAXING_GIBBOUS = 1
    WANING_GIBBOUS = 2
    WANING_CRESCENT = 3

    def __str__(self):
        words = self.name.split('_')
        return ' '.join(word.capitalize() for word in words)


NEXT_PHASE = {
    this_phase: next_phase
    for this_phase in LunarPhase
    for next_phase in LunarPhase
    if next_phase.value - this_phase.value in (1, -3)
}
PREVIOUS_PHASE = {
    this_phase: prev_phase
    for this_phase in LunarPhase
    for prev_phase in LunarPhase
    if this_phase.value - prev_phase.value in (1, -3)
}


def get_phase_from_progress(progress):
    if progress < 0.25:
        return LunarPhase.WAXING_CRESCENT
    elif progress <= 0.5:
        return LunarPhase.WAXING_GIBBOUS
    elif progress <= 0.75:
        return LunarPhase.WANING_GIBBOUS
    else:
        return LunarPhase.WANING_CRESCENT


def get_illumination_from_progress(progress):
    return (1 - math.cos(progress * 2 * math.pi)) / 2


class FullMoon(str, enum.Enum):
    # https://skyandtelescope.org/astronomy-resources/native-american-full-moon-names/
    JAN = 'wolf'
    FEB = 'snow'
    MAR = 'worm'
    APR = 'pink'
    MAY = 'flower'
    JUN = 'strawberry'
    JUL = 'buck'
    AUG = 'sturgeon'
    SEP = 'corn'
    OCT = 'hunters'
    NOV = 'beaver'
    DEC = 'cold'

    BLUE = 'blue'

    def __str__(self):
        return f'{self.value.capitalize():s} Moon'

    @classmethod
    def from_timestamp(cls, timestamp):
        dt = datetime.datetime.fromtimestamp(timestamp)
        month = dt.strftime('%b')
        return cls[month.upper()]


def is_blue_moon(previous_new_moon, full_moon):
    previous_full_moon = full_moon - 2 * (full_moon - previous_new_moon)
    return FullMoon.from_timestamp(full_moon) == FullMoon.from_timestamp(previous_full_moon)


def lookup(args):
    with gzip.open(PATH_TO_LUNATIONS_DATA_JSON, 'rt') as f:
        new_moons = json.loads(f.read())

    index = bisect.bisect_left(new_moons, args.forecast_epoch_timestamp)
    previous_new_moon = new_moons[index - 1]
    next_new_moon = new_moons[index]
    progress = (args.forecast_epoch_timestamp - previous_new_moon) / (next_new_moon - previous_new_moon)
    current_phase = get_phase_from_progress(progress)
    next_phase = NEXT_PHASE[current_phase]
    previous_phase = PREVIOUS_PHASE[current_phase]
    illumination = get_illumination_from_progress(progress)
    nearest_full_moon = previous_new_moon + (next_new_moon - previous_new_moon) / 2
    nearest_full_moon_name = FullMoon.BLUE if is_blue_moon(previous_new_moon, nearest_full_moon) else FullMoon.from_timestamp(nearest_full_moon)

    print({
        'current_phase': str(current_phase),
        'illumination': illumination,
        'nearest_full_moon':  datetime.datetime.fromtimestamp(nearest_full_moon),
        'nearest_full_moon_name':  str(nearest_full_moon_name),
        'next_new_moon': datetime.datetime.fromtimestamp(next_new_moon),
        'next_phase': str(next_phase),
        'previous_new_moon': datetime.datetime.fromtimestamp(previous_new_moon),
        'previous_phase': str(previous_phase),
        'progress': progress,
    })
