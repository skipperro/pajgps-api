class BaseModel:
    """Base model for PAJ GPS API objects."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self):
        """Convert the model instance to a dictionary."""
        return self.__dict__

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.__dict__})>"
