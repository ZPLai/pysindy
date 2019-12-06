"""
Unit tests for feature libraries.
"""

import sys
import os

import pytest
import numpy as np
from scipy.integrate import odeint


my_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, my_path + "/../../")

from sindy.feature_library import (
    PolynomialLibrary,
    FourierLibrary,
    CustomLibrary
)


@pytest.fixture
def data_custom_library():
    library_functions = [lambda x: x, lambda x: x ** 2, lambda x: 0 * x]
    function_names = [lambda s: str(s), lambda s: str(s) + "^2", lambda s: "0"]

    return CustomLibrary(
        library_functions=library_functions,
        function_names=function_names
    )


@pytest.fixture
def data_lorenz():
    def lorenz(z, t):
        return [
            10 * (z[1] - z[0]),
            z[0] * (28 - z[2]) - z[1],
            z[0] * z[1] - 8 / 3 * z[2],
        ]

    t = np.linspace(0, 5, 100)
    x0 = [8, 27, -7]
    x = odeint(lorenz, x0, t)

    return x, t


def test_form_custom_library():
    library_functions = [lambda x: x, lambda x: x ** 2, lambda x: 0 * x]
    function_names = [
        lambda s: str(s), lambda s: "{}^2".format(s), lambda s: "0"
    ]

    CustomLibrary(
        library_functions=library_functions,
        function_names=function_names
    )


def test_bad_parameters():
    with pytest.raises(ValueError):
        PolynomialLibrary(degree=-1)
    with pytest.raises(ValueError):
        PolynomialLibrary(degree=1.5)
    with pytest.raises(ValueError):
        PolynomialLibrary(
            include_interaction=False,
            interaction_only=True
        )
    with pytest.raises(ValueError):
        FourierLibrary(n_frequencies=-1)
    with pytest.raises(ValueError):
        FourierLibrary(n_frequencies=-1)
    with pytest.raises(ValueError):
        FourierLibrary(n_frequencies=2.2)
    with pytest.raises(ValueError):
        FourierLibrary(include_sin=False, include_cos=False)
    with pytest.raises(ValueError):
        library_functions = [lambda x: x, lambda x: x ** 2, lambda x: 0 * x]
        function_names = [
            lambda s: str(s),
            lambda s: "{}^2".format(s),
        ]
        CustomLibrary(
            library_functions=library_functions, function_names=function_names
        )


@pytest.mark.parametrize(
    "library", [
        PolynomialLibrary(),
        FourierLibrary(),
        pytest.lazy_fixture('data_custom_library')
    ]
)
def test_fit_transform(data_lorenz, library):
    x, t = data_lorenz
    library.fit_transform(x)


@pytest.mark.parametrize(
    "library, shape",
    [
        (PolynomialLibrary(), 10),
        (FourierLibrary(), 6),
        (pytest.lazy_fixture('data_custom_library'), 9)
    ],
)
def test_output_shape(data_lorenz, library, shape):
    x, t = data_lorenz
    y = library.fit_transform(x)
    expected_shape = (x.shape[0], shape)
    assert y.shape == expected_shape