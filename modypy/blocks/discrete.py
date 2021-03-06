"""Blocks for discrete-time simulation"""
from modypy.model import Block, Port, EventPort, State


class ZeroOrderHold(Block):
    """A zero-order-hold block which samples an input signal when the connected
    event occurs.

    The block provides an event port ``event_input`` that should be connected
    to the event source that shall trigger the sampling.
    """

    def __init__(self, owner, shape=1, initial_condition=None):
        """
        Constructor for ``ZeroOrderHold``

        Args:
            owner: The owner of the block (system or block)
            shape: The shape of the input and output signal
            initial_condition: The initial state of the sampling output
                (before the first tick of the block)
        """
        Block.__init__(self, owner)

        self.event_input = EventPort(self)
        self.event_input.register_listener(self.update_state)
        self.input = Port(shape=shape)
        self.output = State(
            self,
            shape=shape,
            initial_condition=initial_condition,
            derivative_function=None,
        )

    def update_state(self, data):
        """Update the state on a clock event

        Args:
          data: The time, states and signals of the system
        """
        self.output.set_value(data, self.input(data))


def zero_order_hold(system, input_port, event_port, initial_condition=None):
    """Create a ``ZeroOrderHold`` instance that samples the given input port.
    This is a convenience function that returns the single output port of the
    zero-order-hold block.

    Args:
      system: The system the ``ZeroOrderHold`` block shall be added to.
      input_port: The input port to sample.
      event_port: The event port to use as a sampling signal
      initial_condition: The initial condition of the ``ZeroOrderHold`` block.
        (Default value = None)

    Returns:
        The output signal of the zero-order hold
    """

    hold = ZeroOrderHold(
        system, shape=input_port.shape, initial_condition=initial_condition
    )
    hold.input.connect(input_port)
    hold.event_input.connect(event_port)
    return hold.output
