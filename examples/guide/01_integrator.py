"""
Simple integrator element with sine wave input.
"""
import numpy as np
import matplotlib.pyplot as plt

from modypy.model import System, State, Signal
from modypy.simulation import Simulator

# Create a new system
system = System()


# Define the function for generating the sine signal
def sine_input(data):
    return np.sin(data.time)


# Define the input signal
input_signal = Signal(system,
                      shape=1,
                      value=sine_input)


# Define the derivative for the integrator
def integrator_dt(data):
    return data.signals[input_signal]


# Define the integrator state
integrator_state = State(system,
                         shape=1,
                         derivative_function=integrator_dt,
                         initial_condition=-1)

# Set up a simulation
simulator = Simulator(system,
                      start_time=0.0)

# Run the simulation for 10s
msg = simulator.run_until(time_boundary=10.0)

if msg is not None:
    print("Simulation failed with message '%s'" % msg)
else:
    # Plot the result
    input_line, integrator_line = \
        plt.plot(simulator.result.time,
                 simulator.result.signals[:, input_signal.signal_slice],
                 'r',
                 simulator.result.time,
                 simulator.result.state[:, integrator_state.state_slice],
                 'g')
    plt.legend((input_line, integrator_line), ('Input', 'Integrator State'))
    plt.title("Integrator")
    plt.xlabel("Time")
    plt.savefig("01_integrator_simulation.png")
    plt.show()