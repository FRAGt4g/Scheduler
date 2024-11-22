import time
import numpy as np #type: ignore
import matplotlib.pyplot as plt #type: ignore
from scipy.optimize import curve_fit #type: ignore
from typing import Callable


def graph_time_complexity(function: Callable, input_range: range, time_complexities: dict | None = None):
    """
    Times `function` for each option in `input_range` and compares it against a set of time complexities.
    
    The basic are: 
    - Linear
    - Quadratic
    - Log Linear 

    If you want, you can provide your own as well.
    """

    input_sizes = list(input_range)
    times = []

    for n in input_sizes:
        start_time = time.time()
        function(n)
        times.append(time.time() - start_time)

    if time_complexities is None:
        time_complexities = {
            "Linear: O(n)": lambda n, a, b: a * n + b,
            "Quadratic: O(n^2)": lambda n, a, b: a * n**2 + b,
            "Log Linear: O(n*log(n))": lambda n, a, b: a * n * np.log(n) + b,
        }

            

    # Plotting
    plt.plot(input_sizes, times, 'o', label="Measured times")
    for label, complexity_func in time_complexities.items():
        # Perform the curve fit
        popt, _ = curve_fit(complexity_func, input_sizes, times)
        
        # Plot the fitted curve
        plt.plot(
            input_sizes, 
            complexity_func(np.array(input_sizes), *popt), 
            '-', 
            label=label
        )

    plt.xlabel("Input size (n)")
    plt.ylabel("Time (seconds)")
    plt.legend()
    plt.show()