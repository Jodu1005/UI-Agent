"""窗口操作相关异常。"""


class WindowError(Exception):
    """窗口操作基础异常。"""

    pass


class WindowNotFoundError(WindowError):
    """窗口未找到异常。"""

    def __init__(self, title: str, available_windows: list[str] | None = None) -> None:
        """初始化窗口未找到异常。

        Args:
            title: 查找的窗口标题
            available_windows: 当前可用窗口列表（可选）
        """
        self.title = title
        self.available_windows = available_windows or []
        message = f"未找到窗口: {title}"
        if self.available_windows:
            message += f"\n可用窗口: {', '.join(self.available_windows[:5])}"
        super().__init__(message)


class WindowActivationError(WindowError):
    """窗口激活失败异常。"""

    pass
