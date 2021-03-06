"""
States represent the memory of a dynamical system. In MoDyPy, states are always
real-valued, and may be multi-dimensional.

For each state, a derivative function may be defined which describes the
evolution of the value of the state over time. The value of that derivative
function may depend on the value of any system state or signal, which are made
accessible by the :class:`DataProvider <modypy.model.evaluation.DataProvider>`
object passed to it.

States may also be updated by :mod:`event listeners <modypy.model.events>`.

States are represented as instances of the :class:`State` class. In addition,
:class:`SignalState` instances are states that are also signals.
"""
import numpy as np
from modypy.model.ports import AbstractSignal


class State(AbstractSignal):
    """A state describes a portion of the state of a block.

    Args:
        owner: The owner of the state
        derivative_function: The derivative function of the state
            (Default: 0)
        shape: The shape of the state (Default: 1)
        initial_condition: The initial value of the state (Default: 0)
    """

    def __init__(
        self, owner, derivative_function=None, shape=(), initial_condition=None
    ):
        super().__init__(shape)
        self.owner = owner
        self.derivative_function = derivative_function
        if initial_condition is None:
            self.initial_condition = np.zeros(self.shape)
        else:
            self.initial_condition = np.asarray(initial_condition)

        self.state_index = self.owner.system.allocate_state_lines(self.size)
        self.owner.system.states.append(self)

    @property
    def state_slice(self):
        """A slice object that represents the indices of this state in the
        states vector."""

        return slice(self.state_index, self.state_index + self.size)

    def __call__(self, system_state):
        return system_state.get_state_value(self)

    def set_value(self, system_state, value):
        """
        Update the value of this state in the given system state.

        Args:
            system_state: The system state to update
            value: The value to set this state to
        """
        system_state.set_state_value(self, value)
