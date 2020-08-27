import datetime

import numpy


def dt64_to_str(dt64):
    if isinstance(dt64, numpy.datetime64):
        dt64 = dt64.astype(float) / 1e9

    return str(
        datetime
        .datetime
        .utcfromtimestamp(dt64)
    )


def _validate_iter(model, dt, x, y, name):
    residual = y.copy() - numpy.array(list(map(model.predict, x)))

    yield f'> Validation report: {name:s}'
    yield ''
    yield f'- Evaluating {len(residual):d} lunations'
    yield f'- Between {dt64_to_str(dt.min()):s} and {dt64_to_str(dt.max()):s}'
    yield f'- MAE: {numpy.abs(residual / 3600).mean():.1f}h'
    yield f'- bias: {residual.mean():+.0f}s'
    yield ''


def report(*args, **kwargs):
    print('\n'.join(_validate_iter(*args, **kwargs)))


def _sample_iter(model, dt, x, y, index=120):
    yield f'> Sampling lunation {x[index]:d}'
    yield ''
    yield f'- Predicted: {dt64_to_str(model.predict(x[index])):s}'
    yield f'- Observed : {dt64_to_str(y[index]):s}'
    yield ''


def sample(*args, **kwargs):
    print('\n'.join(_sample_iter(*args, **kwargs)))
