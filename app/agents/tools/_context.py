import contextvars

_current_task_id: contextvars.ContextVar[int] = contextvars.ContextVar('current_task_id', default=None)


def set_current_task_id(task_id: int):
    _current_task_id.set(task_id)


def get_current_task_id() -> int:
    return _current_task_id.get()
