class Component:
    """
    Base class for all components.
    Components should generally hold data and minimal logic.
    """
    def __init__(self, owner=None):
        self.owner = owner

    def update(self, owner, game_context, dt):
        """
        Called once per frame by the SystemsManager or Entity.
        
        :param owner: The entity that owns this component.
        :param game_context: Reference to the global Game or Context object.
        :param dt: Delta time since last frame (seconds).
        """
        pass