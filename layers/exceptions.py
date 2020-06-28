class InsufficientBoundsError(Exception):
    """Raised when Bounds object does not have enough bounding descriptors."""
    pass

class InvalidBoundsError(Exception):
    """Raised when bounds object is passed bound descriptors that are invalid."""
    pass

class NotReadyToRenderError(Exception):
    """Raised when Layer does not have sufficient information, (usually the
    content property) to render."""
    pass

class NotEvaluatedError(Exception):
    """Raised when trying to trying to bound a Layer and not all of it's
    attributes have evaluated yet."""
    pass

class NotBoundedError(Exception):
    """Raised when trying to access bounds of a layer, but it has not been
    bounded yet."""
    pass

class NotReadyToEvaluateError(Exception):
    """Raised when trying to evaluate an attribute and it does not have
    sufficient information to return an evaluated_value"""
    pass

class LayerDoesNotExistError(Exception):
    """Raised when a layer is referenced when it does not exist yet."""
    pass
