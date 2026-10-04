"""Public failure types for generation and checkpoint recovery."""

class GenerationError(RuntimeError):
    """A generation batch exhausted its finite attempts."""

    def __init__(self, message, *, stage_index=None, batch_index=None, row_ids=None):
        super().__init__(message)
        self.stage_index = stage_index
        self.batch_index = batch_index
        self.row_ids = list(row_ids or [])


class CheckpointError(GenerationError):
    """A checkpoint belongs to another run or contains invalid state."""
