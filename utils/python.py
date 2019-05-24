# coding:utf-8
import sys

if sys.platform != 'win32':
    def patch():
        pass
else:
    def patch_win_selector():
        """Patch selectors.SelectSelector to fix WinError 10038 in Windows
        Ref: https://bugs.python.org/issue33350
        """
        import select
        from selectors import SelectSelector

        def _select(self, r, w, _, timeout=None):
            try:
                r, w, x = select.select(r, w, w, timeout)
            except OSError as e:
                if hasattr(e, 'winerror') and e.winerror == 10038:
                    # descriptors may already be closed
                    return [], [], []
                raise
            else:
                return r, w + x, []

        SelectSelector._select = _select
