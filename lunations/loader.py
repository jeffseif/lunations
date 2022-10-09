import bisect
import datetime

import numpy
import pandas


def load_data(args):
    print(f"> Loading data from {args.path_to_csv_input:s}")

    df = pandas.read_csv(args.path_to_csv_input)
    new_moons = df[df.lunar_phase == 0].sort_values(by="timezonetz").reset_index()
    timezonetz = new_moons.timezonetz.astype("datetime64")
    epochs = timezonetz.astype("int64").apply(lambda x: x / 1e9).to_numpy().copy()
    lunations = numpy.array(range(len(epochs)))
    timezonetz = timezonetz.to_numpy()

    print(f"> Extracted {len(epochs):d} new moons")

    split_value = int(datetime.datetime.now().timestamp())
    split_index = bisect.bisect_left(epochs, split_value)

    print(
        "> Splitting test/train data into "
        f"{split_index:d}/{len(epochs) - split_index:d}",
    )

    return {
        "train": {
            "dt": timezonetz[:split_index],
            "x": lunations[:split_index],
            "y": epochs[:split_index],
        },
        "test": {
            "dt": timezonetz[split_index:],
            "x": lunations[split_index:],
            "y": epochs[split_index:],
        },
    }
