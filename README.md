# lunations

A library for forecasting lunar phases

## Why make a lunation library?

Every (roughly) twenty-nine and a half days, the moon encircles the earth and also completes one full spin on its axis.  This journey takes it from new moon, through waxing crescent phase and waxing gibbous phase, to full moon, through waning gibbous phase and waning crescent phase, and back to new moon.  Each of these cycles is called a lunation or a [synodic month](https://en.wikipedia.org/wiki/Lunar_month#Synodic_month).  Because lunations vary in their duration between [~29.2 and ~29.9 days](https://individual.utoronto.ca/kalendis/lunar/index.htm#vary), it can be tricky to determine the current lunar phase or to anticipate that of a future date.  The `USNO` maintained [an API](http://aa.usno.navy.mil/data/) which provided exactly this information, but since that was taken down in October 2019 there is no longer a reliable online source for lunar phases.  **We need an offline library which can determine current and upcoming lunar phases**.

## OK, so how can we determine current and upcoming lunar phases?

Well, first we need data which tabulates lunar phases.  From that, we can train a forecasting model and use that to generate the timestamps for lunar phases 1000 years into the future.  With those timestamps, the lunar phase can be determined from a simple lookup.

Although the `USNO` API was taken down a github'er managed to [snapshot its data](https://github.com/CraigChamberlain/moon-data) beforehand.  After some simple bash munging, that data looks like this:

```
timezonetz,lunar_phase
1700-01-05T10:30:00+00,2
1700-01-12T03:34:00+00,3
1700-01-20T04:20:00+00,0
1700-01-28T05:13:00+00,1
1700-02-03T21:05:00+00,2
1700-02-10T18:59:00+00,3
1700-02-18T23:33:00+00,0
1700-02-26T16:37:00+00,1
1700-03-05T07:38:00+00,2
```

The next step in our model pipeline is to grab just the new moons (i.e., `lunar_phase=0`) and convert the date times of their occurrences to epoch timestamps (e.g., `2020-08-19T02:42:00` becomes `1597804920`).  Then we assign each of these a lunation number (e.g., `0` for `1700-01-20T04:20:00`, `1` for `1700-02-18T23:33:00`).

Our model takes the lunation number as its sole input (i.e., feature) and epoch timestamps as its labels.  Training and test sets are created by splitting the data by "now" so that we regress on the past and validate on the future.  Once we have a model which can satisfactorily forecast lunations, we can generate predictions between the years 1 and 10000 CE and stow them away.

## What does the forecast model look like?

Our forecast model takes lunations as its sole feature and epoch timestamps as its label.  Knowing that lunations are fairly periodic, we begin by fitting a linear regression; the result is: `y ~ 2551442.8159269537 x - 8518684463.92163`, which corresponds to an offset of `1700-01-20 02:45:36` and a period of `29.531 days`.  These align well with the first new moon that occurs in the dataset and the average period of a synodic month.  The residual is somewhat periodic and varies between `-6 hours` and `+6 hours`.

The lunar orbit is slightly eccentric (i.e., elliptical), which causes the moon to speed up when it is nearest the earth and slow down when it is furthest.  As the earth orbits the sun, this eccentricity can point towards the sun or away from it (or sideways).  The earth also has eccentricity in its orbit which can interact too.  Each of these mechanisms (and more) contribute periodic variations to the lunation duration.  So our next stage is to fit a Fourier to the residual.

The resulting spectrogram shows two prominent peaks which partially overlap and which span a fairly wide bandwidth.  In other words, there are distinct harmonics in the residual, but they don't neatly conform to sinusoids.  Rather than greedily select the strongest k (in magnitude) harmonics, we try to grab the Fourier harmonic from just the tips of these two harmonic peaks.  We do this by:

1. isolating the peaks within the spectrograms
1. fitting a Gaussian to each peak
1. extracting their centers and heights (i.e., frequency and magnitude)
1. interpolating their phases

The result of this compressed model is:

- a primary harmonic of magnitude `3.52 hours` and a `13.95 lunations` period
- a secondary harmonic of magnitude `1.66 hours` and a `12.36 lunations` period
- much smaller harmonics that we decided to drop

The primary and secondary harmonics appear to span the period of the cycle of [the lunar orbital perigee](https://individual.utoronto.ca/kalendis/lunar/index.htm#vary).  Perhaps this duplicity is related to our use of Fourier series to fit something which is actually elliptical?  Future work could be to transform the residual to account for the expected elliptical periodicity and fitting on that, rather than blindly throwing a Fourier series at it.

## How good is the forecast?

The model is fitted on 3966 historical lunations from `1700-01-20` through `2020-08-19` and presents a mean absolute error of `6 hours` and a bias of `-8 seconds`.  When evaluated on 763 lunations in the future (and not within the training set) through `2082-04-28`, it presents a mean absolute error of `5.3 hours` and a bias of `-108 seconds`.  For example, the first new moon in June 2030 occurs at `6:21 AM` and our model predicts that it will occur at `4:39 AM`, which is an error of around two hours.

## How does the library work?

### Forecasting as a python package

1. Install the package: `pip install -e git://github.com/jeffseif/lunations.git#egg=lunations`
1. Import it: `import lunations`
1. Run it `lunations.forecast_for_current_timestamp()`

### Forecasting from the command-line

```bash
> make forecast
# Build a fresh image
sha256:26d6bb109d35971879578e17afcf68bc769824041655cc2d20d85aaaaafbc693
# Stop and remove container
# Run a fresh container
d27e85d967855b712349cd49d014bf047cbe4bac4ef1a683864e2e2792bf8347
{'current_timestamp': datetime.datetime(2020, 8, 28, 22, 0, 35, 349153), 'next_new_moon': datetime.datetime(2020, 9, 17, 11, 20, 20, 984441), 'previous_new_moon': datetime.datetime(2020, 8, 19, 0, 3, 45, 487658), 'nearest_full_moon': datetime.datetime(2020, 9, 2, 17, 42, 3, 236050), 'is_blue_moon': False, 'nearest_full_moon_name': 'Corn Moon', 'phase_fraction': 0.336427372751769, 'illumination_fraction': 0.7583701801043545, 'current_phase': 'Waxing Gibbous', 'next_phase': 'Waning Gibbous', 'previous_phase': 'Waxing Crescent'}
```

### Retraining the model

```bash
> make retrain
# Build a fresh image
sha256:a9b22c80631ff15060477b01e82529bb838890ea6da1b641c55c6435d0ae472d
# Stop and remove container
# Run a fresh container
2f77a8630c0caaf550e8c67443f9a2707fe3c7dc7efff2a474fa18472e5cd80b
> Loading data from /code/lunations.csv.gz
> Extracted 4729 new moons
> Splitting test/train data into 3966/763
> Linear model

Offset = 1700-01-20 02:45:36.078370
Period = 29.531 days

> Compressed harmonic model

#0 = 3.52 hours at 13.95 lunations
#1 = 1.66 hours at 12.36 lunations

> Validation report: in sample

- Evaluating 3966 lunations
- Between 1700-01-20 04:20:00 and 2020-08-19 02:42:00
- MAE: 6.0h
- bias: -8s

> Validation report: out of sample

- Evaluating 763 lunations
- Between 2020-09-17 11:00:00 and 2082-04-28 02:03:00
- MAE: 5.3h
- bias: -108s

> Sampling lunation 4086

- Predicted: 2030-06-01 04:38:59.891833
- Observed : 2030-06-01 06:21:00

> Exporting 123672 lunations to /code/lunations.json.gz
```
