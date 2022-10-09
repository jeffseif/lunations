import bisect
import cmath
import datetime
import math

import numpy
from scipy.optimize import curve_fit


def harmonic_model(x, harmonics):
    return sum(
        (abs(coef) * math.cos(2 * math.pi * freq * x + cmath.phase(coef)))
        for freq, coef in harmonics
    )


class LinearPlusHarmonicPeakModel:
    def __init__(self, a_and_b, freqs_and_coefs):
        self.a_and_b = a_and_b.astype(float).tolist()
        self.freqs_and_coefs = freqs_and_coefs

    def str_iter(self):
        a, b = self.a_and_b
        yield "> Linear model"
        yield ""
        yield f"Offset = {datetime.datetime.fromtimestamp(b)}"
        yield f"Period = {a / 86400:.3f} days"
        yield ""

        yield "> Compressed harmonic model"
        yield ""
        for i, (f, c) in enumerate(self.freqs_and_coefs):
            yield f"#{i:d} = {abs(c)/3600:.2f} hours at {1 / f:.2f} lunations"
        yield ""

    def __str__(self):
        return "\n".join(self.str_iter())

    def predict(self, x):
        return linear_model(x, *self.a_and_b) + harmonic_model(x, self.freqs_and_coefs)


def gaussian(x, A, mu, sigma):
    return A * numpy.exp(-((x - mu) ** 2) / (2 * sigma**2))


def fit_peaks(x, y, number_of_peaks):
    mag, phase = numpy.abs(y), numpy.angle(y)

    def merge_index_into_peaks(index, peaks):
        for peak in peaks:
            for jndex in peak:
                if abs(index - jndex) == 1:
                    peak.append(index)
                    return
        peaks.append([index])
        return

    peaks = []
    for index in reversed(numpy.argsort(mag)):
        merge_index_into_peaks(index, peaks)

    peaks = list(map(sorted, peaks))[:number_of_peaks]

    for peak in peaks:
        p, _ = curve_fit(gaussian, x[peak], mag[peak])
        peak_x = p[1]
        peak_mag = gaussian(peak_x, *p)
        i = bisect.bisect_left(x[peak], peak_x)
        j = (x[peak][i] - peak_x) / (x[peak][i] - x[peak][i - 1])
        peak_phase = phase[peak][i - 1] + j * (phase[peak][i] - phase[peak][i - 1])

        peak_y = peak_mag * math.sin(peak_phase) + 1j * peak_mag * math.cos(peak_phase)

        yield (peak_x, peak_y)


def linear_model(x, a, b):
    return a * x + b


def fit(args, dt, x, y):
    a_and_b, _ = curve_fit(linear_model, x, y)

    residual = y - linear_model(x, *a_and_b)
    freqs_and_coefs = list(
        fit_peaks(
            numpy.fft.fftfreq(len(x)),
            numpy.fft.rfft(residual) / len(x),
            args.harmonic_peaks,
        ),
    )

    return LinearPlusHarmonicPeakModel(a_and_b, freqs_and_coefs)
