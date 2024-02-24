from m8b.event import Event


class SampleApp:

    def __init__(self):
        """Run any setup code here for when the app first starts."""

    def handle_event(self, event: Event):
        """Handle any events that the app cares about here.
        For example, if the app cares about shake events:

          if isinstance(event, ShakeEvent):
              do_something()
        """

    def run(self):
        """Run the app's logic here.
        This function will be called every tick of the Run loop.
        """

    def draw(self, display):
        """Draw the app's state to the display here, if changed.
        This function will be called every tick of the Draw loop.
        """

    def stop(self):
        """Run any cleanup code here for when the app is about to exit."""
