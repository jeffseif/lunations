from lunations import exporter
from lunations import loader
from lunations import trainer
from lunations import validator


def pipeline(args):
    data = loader.load_data(args)

    model = trainer.fit(args, **data["train"])
    print(model)

    validator.report(model, **data["train"], name="in sample")
    validator.report(model, **data["test"], name="out of sample")

    validator.sample(model, **data["test"])

    exporter.generate(args, model)
