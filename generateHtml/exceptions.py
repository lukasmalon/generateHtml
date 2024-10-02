class BuilderError(Exception):
    pass

class IllegalCompositionError(BuilderError):
    pass

class DuplicateAttributeError(IllegalCompositionError, TypeError):
    pass

class WrongAttributeElementCombinationError(IllegalCompositionError):
    pass

class IllegalCharacterError(ValueError):
    pass