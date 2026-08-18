class TodoNotFoundError(Exception):
    """待办事项不存在"""

    pass


class TodoTitleEmptyError(Exception):
    """待办标题为空"""

    pass