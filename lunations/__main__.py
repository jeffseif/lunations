import argparse

from lunations import DEFAULT_HARMONIC_PEAKS
from lunations import exporter
from lunations import loader
from lunations import trainer
from lunations import validator


parser = argparse.ArgumentParser()
parser.add_argument('--path-to-csv-input', required=True, type=str)
parser.add_argument('--harmonic-peaks', default=DEFAULT_HARMONIC_PEAKS, required=False, type=int)
parser.add_argument('--path-to-json-output', required=True, type=str)
args = parser.parse_args()

data = loader.load_data(args)
model = trainer.fit(args, **data['train'])
print(model)
validator.report(model, **data['train'], name='in sample')
validator.report(model, **data['test'], name='out of sample')
validator.sample(model, **data['test'])
exporter.generate(args, model)
