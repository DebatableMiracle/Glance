from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

class DraggableMixin(QWidget):
    """Mixin to make a frameless PyQt window draggable."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.old_pos = None

    def mousePressEvent(self, event):
        """Store the position when mouse is pressed."""
        if event.button() == Qt.LeftButton:
            self.old_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Move the window based on mouse drag."""
        if self.old_pos:
            delta = event.pos() - self.old_pos
            self.move(self.pos() + delta)

    def mouseReleaseEvent(self, event):
        """Reset the stored position when mouse is released."""
        if event.button() == Qt.LeftButton:
            self.old_pos = None
