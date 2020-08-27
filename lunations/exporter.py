import gzip
import json

from lunations import MAX_LUNATION
from lunations import MIN_LUNATION


def generate(args, model):
    print(
        f'> Exporting {MAX_LUNATION - MIN_LUNATION + 1:d} lunations '
        f'to {args.path_to_json_output:s}'
    )
    with gzip.open(args.path_to_json_output, 'wt') as f:
        f.write(json.dumps(list(map(model.predict, range(MIN_LUNATION, MAX_LUNATION)))))
