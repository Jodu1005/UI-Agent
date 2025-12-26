"""窗口管理器模块。"""

import logging
import os
from typing import Any, Callable, Optional

from src.window.exceptions import WindowActivationError, WindowNotFoundError

logger = logging.getLogger(__name__)


class WindowManager:
    """跨平台窗口管理器。"""

    def __init__(self) -> None:
        """初始化窗口管理器。"""
        self._pygetwindow: Any | None = None
        try:
            import pygetwindow as gw  # type: ignore[import-untyped]

            self._pygetwindow = gw
        except ImportError:
            logger.warning("pygetwindow 未安装，窗口管理功能将不可用")

    def find_by_process_name(self, process_name: str) -> Any | None:
        """根据进程名查找窗口。

        Args:
            process_name: 进程名称（如 "pycharm64.exe", "WeChatApp.exe"）

        Returns:
            窗口对象，未找到返回 None
        """
        if self._pygetwindow is None:
            logger.error("pygetwindow 未安装，无法查找窗口")
            return None

        try:
            # Windows 特定实现
            import win32gui
            import win32process

            # 存储找到的窗口
            found_windows = []

            def enum_windows_callback(hwnd: Any, _: Any) -> bool:
                """枚举窗口的回调函数。"""
                try:
                    # 获取窗口进程 ID
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)

                    # 获取进程名称
                    import psutil
                    process = psutil.Process(pid)
                    exe_name = process.name()

                    # 检查进程名是否匹配
                    if exe_name.lower() == process_name.lower() or exe_name.lower().startswith(
                        process_name.lower().replace(".exe", "")
                    ):
                        # 获取窗口标题
                        title = win32gui.GetWindowText(hwnd)

                        # 过滤掉没有标题或不可见的窗口
                        if title and win32gui.IsWindowVisible(hwnd):
                            found_windows.append((hwnd, title, exe_name, pid))
                except Exception:
                    pass
                return True

            # 枚举所有窗口
            win32gui.EnumWindows(enum_windows_callback, None)

            if found_windows:
                # 优先选择可见的主窗口（通常是第一个找到的）
                # 排序策略：优先选择标题较长的（通常主窗口标题更长）
                found_windows.sort(key=lambda x: len(x[1]), reverse=True)

                hwnd, title, exe, pid = found_windows[0]
                logger.info(f"找到进程窗口: {exe} - {title} (PID: {pid})")

                # 使用 pygetwindow 获取窗口对象
                try:
                    windows = self._pygetwindow.getWindowsWithTitle(title)
                    if windows:
                        return windows[0]
                except Exception:
                    pass

                # 如果 pygetwindow 找不到，返回一个包装对象
                class WindowWrapper:
                    def __init__(self, hwnd: Any, title: str, pid: int) -> None:
                        self.hwnd = hwnd
                        self.title = title
                        self.pid = pid  # 存储进程 ID 用于权限检测
                        self._win32gui = win32gui

                    @property
                    def isMinimized(self) -> bool:
                        return bool(self._win32gui.IsIconic(self.hwnd))

                    def restore(self) -> None:
                        self._win32gui.ShowWindow(self.hwnd, 9)  # SW_RESTORE

                    def activate(self) -> None:
                        self._win32gui.SetForegroundWindow(self.hwnd)

                return WindowWrapper(hwnd, title, pid)

            return None

        except ImportError:
            logger.warning("需要安装 psutil 和 pywin32 来使用进程查找功能")
            return None
        except Exception as e:
            logger.error(f"按进程名查找窗口时出错: {e}")
            return None

    def find_window(self, title: str, exact_match: bool = False) -> Any | None:
        """根据标题查找窗口。

        Args:
            title: 窗口标题（支持部分匹配）
            exact_match: 是否精确匹配

        Returns:
            窗口对象，未找到返回 None
        """
        if self._pygetwindow is None:
            logger.error("pygetwindow 未安装，无法查找窗口")
            return None

        try:
            if exact_match:
                windows = self._pygetwindow.getWindowsWithTitle(title)
                if windows:
                    return windows[0]
                return None

            # 尝试部分匹配
            all_windows = self._pygetwindow.getAllWindows()
            for window in all_windows:
                if title.lower() in window.title.lower():
                    return window
            return None
        except Exception as e:
            logger.error(f"查找窗口时出错: {e}")
            return None

    def activate_by_process(self, process_name: str) -> bool:
        """通过进程名激活窗口。

        Args:
            process_name: 进程名称（如 "pycharm64.exe", "WeChatApp.exe"）

        Returns:
            是否成功激活

        Raises:
            WindowNotFoundError: 窗口未找到
            WindowActivationError: 激活失败
        """
        window = self.find_by_process_name(process_name)
        if window is None:
            available = self.list_processes()[:10]
            raise WindowNotFoundError(f"进程: {process_name}", available)

        try:
            # 如果窗口最小化，先恢复
            if window.isMinimized:
                logger.info(f"窗口已最小化，正在恢复")
                window.restore()

            # 激活窗口
            window.activate()
            logger.info(f"已激活进程窗口: {process_name}")
            return True
        except Exception as e:
            error_msg = str(e)
            # 检查是否是权限问题（Windows Error Code 5）
            if "Error code from Windows: 5" in error_msg or "拒绝访问" in error_msg:
                logger.error(f"权限不足: 目标进程可能以管理员权限运行")
                raise WindowActivationError(
                    f"权限不足，无法激活窗口。目标应用可能以管理员权限运行。\n"
                    f"解决方案：\n"
                    f"1. 以管理员身份运行此脚本\n"
                    f"2. 或关闭目标应用后以普通用户身份重新打开"
                ) from e
            logger.error(f"激活窗口失败: {e}")
            raise WindowActivationError(f"激活窗口失败: {e}") from e

    def activate_window(self, title: str) -> bool:
        """激活指定标题的窗口。

        Args:
            title: 窗口标题

        Returns:
            是否成功激活

        Raises:
            WindowNotFoundError: 窗口未找到
            WindowActivationError: 激活失败
        """
        if self._pygetwindow is None:
            raise WindowActivationError("pygetwindow 未安装")

        window = self.find_window(title)
        if window is None:
            # 获取可用窗口列表用于错误提示
            available = self.list_windows()[:10]
            raise WindowNotFoundError(title, available)

        try:
            # 如果窗口最小化，先恢复
            if window.isMinimized:
                logger.info(f"窗口 {title} 已最小化，正在恢复")
                window.restore()

            # 尝试多种激活方法
            # 方法 1: 标准激活
            try:
                window.activate()
            except Exception as e:
                logger.warning(f"标准激活失败: {e}")

            # 方法 2: 强制前置（Windows 特有）
            try:
                # 尝试使用 win32gui 强制激活
                import win32gui
                import win32con

                # 获取窗口句柄
                hwnd = win32gui.FindWindow(None, window.title)
                if hwnd:
                    # 强制将窗口置于前台
                    # 这对某些以管理员权限运行的应用有效
                    try:
                        # 先尝试正常的激活
                        win32gui.SetForegroundWindow(hwnd)
                    except Exception:
                        # 如果失败，尝试其他方法
                        # 将窗口线程附加到前台线程
                        import win32api
                        import win32process

                        foreground_thread = win32process.GetWindowThreadProcessId(
                            win32gui.GetForegroundWindow()
                        )[0]
                        current_thread = win32api.GetCurrentThreadId()
                        target_thread = win32process.GetWindowThreadProcessId(hwnd)[0]

                        # 附加线程输入
                        if current_thread != target_thread:
                            win32process.AttachThreadInput(current_thread, target_thread, True)

                        # 设置前台窗口
                        if win32gui.IsIconic(hwnd):
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                        else:
                            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

                        win32gui.SetForegroundWindow(hwnd)
                        win32gui.SetFocus(hwnd)

                        # 分离线程
                        if current_thread != target_thread:
                            win32process.AttachThreadInput(current_thread, target_thread, False)

                    logger.info(f"使用 Win32 API 强制激活窗口: {title}")
                    return True
            except ImportError:
                # win32gui 未安装，使用标准方法
                logger.debug("win32gui 未安装，使用标准激活方法")
            except Exception as e:
                logger.warning(f"Win32 API 激活失败: {e}")

            logger.info(f"窗口已激活: {title}")
            return True
        except Exception as e:
            logger.error(f"激活窗口失败: {e}")
            raise WindowActivationError(f"激活窗口失败: {e}") from e

    def is_window_minimized(self, title: str) -> bool:
        """检查窗口是否最小化。

        Args:
            title: 窗口标题

        Returns:
            是否最小化
        """
        window = self.find_window(title)
        if window is None:
            return False
        return bool(window.isMinimized)

    def restore_window(self, title: str) -> bool:
        """恢复最小化的窗口。

        Args:
            title: 窗口标题

        Returns:
            是否成功恢复
        """
        window = self.find_window(title)
        if window is None:
            return False

        try:
            window.restore()
            return True
        except Exception as e:
            logger.error(f"恢复窗口失败: {e}")
            return False

    def list_windows(self, title_filter: str = "") -> list[str]:
        """列出所有窗口标题。

        Args:
            title_filter: 标题过滤关键词

        Returns:
            窗口标题列表
        """
        if self._pygetwindow is None:
            return []

        try:
            all_windows = self._pygetwindow.getAllWindows()
            titles = [w.title for w in all_windows if w.title]

            if title_filter:
                filter_lower = title_filter.lower()
                titles = [t for t in titles if filter_lower in t.lower()]

            return titles
        except Exception as e:
            logger.error(f"获取窗口列表失败: {e}")
            return []

    def list_processes(self) -> list[str]:
        """列出所有运行的进程名称。

        Returns:
            进程名称列表
        """
        try:
            import psutil

            processes = set()
            for proc in psutil.process_iter(["name"]):
                try:
                    name = proc.info["name"]
                    if name:
                        processes.add(name)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return sorted(list(processes))
        except ImportError:
            logger.warning("psutil 未安装，无法列出进程")
            return []
        except Exception as e:
            logger.error(f"获取进程列表失败: {e}")
            return []
