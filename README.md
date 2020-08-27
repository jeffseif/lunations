# lunations

A library for forecasting lunar phases

## Why make a lunation library?

Every (roughly) twenty-nine and a half days, the moon encircles the earth and also completes one full spin on its axis.  It begins this journey at new moon and moves through waxing crescent phase and waxing gibbous phase, passes full moon, and then moves through waning gibbous and waning crescent phases on its return to new moon.  Each of these cycles is called a lunation or a [synodic month](https://en.wikipedia.org/wiki/Lunar_month#Synodic_month).  Because lunations vary in their duration between [~29.2 and ~29.9 days](https://individual.utoronto.ca/kalendis/lunar/index.htm#vary), it can be tricky to determine the current lunar pahse or to anticipate that of a future date.  The `USNO` maintained [an API](http://aa.usno.navy.mil/data/) which provided exactly this information, but since that was taken down in October 2019 there is no longer a reliable online service to provide this information.  **We need an offline library to determine current and upcoming lunar phases**.

## How do we determine current and upcoming lunar phases?

Well, first we need data to train a forecasting model upon.  And with such a model, we can generate the timestamps for lunar phases 1000 years into the future.  From these forecasts and a timestamp of interest, the lunar phase can be determined from a simple lookup.

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

The next step in our model pipeline is to grab just the new moons (i.e., `lunar_phase=0`) and convert the date times of their occurrences to epoch timestamps (e.g., `2020-08-19T02:42:00` becomes `1597804920`).  Then we assign each of these a lunation number (e.g., `0` for `1700-01-20T04:20:00`, `1` for `1700-02-18T23:33:00`).  Our model takes the lunation number as its sole input (i.e., feature) and epoch timestamps as its labels.  Training and test sets are created by splitting the data by "now" so that we regress on the past and validate on the future.  Once we have a model which can satisfactorily forecast lunations, we can generate predictions between the years 1 and 10000 CE and stow them away.

## How do we forecast lunations?

Our model takes lunations as its sole feature and epoch timestamps as its label.  Knowing that lunations are fairly periodic, we begin by fitting a linear regression; the result is: `y ~ 2551442.8159269537 x - 8518684463.92163`, which corresponds to an offset of `1700-01-20 02:45:36` and a period of `29.531 days`.  These align well with the first new moon that occurs in the dataset and the average period of a synodic month.

The lunar orbit is slightly eccentric (i.e., elliptical), which causes the moon to speed up when it is nearest the earth and slow down when it is furthest.  As the earth orbits the sun, this eccentricity can point towards the sun or away from it (or sideways).  The earth also has eccentricity in its orbit which can interact too.  Each of these mechanisms (and more) contribute periodicity to the lunation duration.  So our next stage is to fit a Fourier to the residual.

The resulting spectrogram shows two prominent peaks which partially overlap and which span a fairly wide bandwidth.  In other words, there are distinct harmonics in the residual, but they don't neatly conform to sinusoids.  Rather than greedily select the strongest k (in magnitude) harmonics, we try to grab the Fourier harmonic from just the tips of these two harmonic peaks.  We do this by:

1. isolating the peaks within the spectrograms
1. fitting a Gaussian to each peak
1. extracting their centers and heights (i.e., frequency and magnitude)
1. interpolating their phases

The result of this compressed model is:

- a primary harmonic of magnitude `3.52 hours` and a `13.95 lunations` period
- a secondary harmonic of magnitude `1.66 hours` and a `12.36 lunations` period

These seem to span the period of the cycle of [the lunar orbital perigee](https://individual.utoronto.ca/kalendis/lunar/index.htm#vary).  Perhaps this duplicity is related to our use of Fourier series to fit something which is actually elliptical?

## How good is the forecast?

The model is fitted on 3966 historical lunations from `1700-01-20` through `2020-08-19` and presents a mean absolute error of `6 hours` and a bias of `-8 seconds`.  When evaluated on 763 lunations in the future through `2082-04-28`, it presents a mean absolute error of `5.3 hours` and a bias of `-108 seconds`.  For example, the first new moon in June 2030 occurs at `6:21 AM` and our model predicts that it will occur at `4:39 AM`, which is an error of around two hours.
