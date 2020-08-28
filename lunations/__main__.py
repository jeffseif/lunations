import argparse
import datetime

from lunations import DEFAULT_HARMONIC_PEAKS
from lunations import forecaster
from lunations import modeler


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Model

    model_parser = subparsers.add_parser('model', help='Model lunations')
    model_parser.add_argument('--path-to-csv-input', required=True, type=str)
    model_parser.add_argument('--harmonic-peaks', default=DEFAULT_HARMONIC_PEAKS, required=False, type=int)
    model_parser.add_argument('--path-to-json-output', required=True, type=str)
    model_parser.set_defaults(func=modeler.pipeline)

    # Forecast

    forecast_parser = subparsers.add_parser('forecast', help='Lookup lunations')
    forecast_parser.add_argument('--forecast-epoch-timestamp', default=datetime.datetime.now().timestamp(), type=float)
    forecast_parser.set_defaults(func=forecaster.cli)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
