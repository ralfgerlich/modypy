# pylint: disable=missing-module-docstring
import numpy as np
from modypy.blocks.discont import saturation
from modypy.model import Clock, System, signal_function
from modypy.simulation import SimulationResult, Simulator
from numpy import testing as npt


def test_saturation():
    system = System()
    Clock(system, period=0.01)

    @signal_function
    def _sine_source(system_state):
        return np.sin(2 * np.pi * system_state.time)

    saturated_out = saturation(_sine_source, lower_limit=-0.5, upper_limit=0.6)

    simulator = Simulator(system, start_time=0.0)
    result = SimulationResult(system, simulator.run_until(time_boundary=1.0))

    sine_data = _sine_source(result)
    saturated_data = saturated_out(result)
    saturated_exp = np.minimum(np.maximum(sine_data, -0.5), 0.6)
    npt.assert_almost_equal(saturated_data, saturated_exp)
