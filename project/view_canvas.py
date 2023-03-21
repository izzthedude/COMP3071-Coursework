from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from project.enums import Sizes
from project.map_gen import MapTile, Direction, MapGenerator


class _StyleableQWidget(QWidget):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, painter, self)


class CanvasView(_StyleableQWidget):
    def __init__(self, mapgen: MapGenerator, parent: QObject = None):
        super().__init__(parent)

        self.setFixedSize(Sizes.CANVAS_SIZE, Sizes.CANVAS_SIZE)
        self._tiles: list[MapTile] = mapgen.get_tiles()

    def paintEvent(self, event):
        p = QPainter(self)
        p.pen().setWidth(5)
        for tile in self._tiles:
            for border in tile.borders:
                if border is not None:
                    start, end = border
                    x_start, y_start = start
                    x_end, y_end = end
                    p.drawLine(
                        x_start,
                        y_start,
                        x_end,
                        y_end
                    )


class TileWidget(_StyleableQWidget):
    def __init__(self, tile: MapTile, canvas: CanvasView, size: float, parent: QObject = None):
        super().__init__(canvas)
        self.setFixedSize(size, size)
        self.move(tile.x * size, tile.y * size)

        self._top_border = HBorderWidget(self)
        self._bottom_border = HBorderWidget(self)
        self._left_border = VBorderWidget(self)
        self._right_border = VBorderWidget(self)
        self._init_borders()

        self._hide_border(tile.from_direction)
        self._hide_border(tile.to_direction)

    def _init_borders(self):
        self._top_border.move(0, 0)
        self._bottom_border.move(0, self.height() - self._bottom_border.height())
        self._left_border.move(0, 0)
        self._right_border.move(self.width() - self._right_border.width(), 0)

    def _hide_border(self, direction: Direction):
        match direction:
            case Direction.UP:
                self._top_border.hide()
            case Direction.LEFT:
                self._left_border.hide()
            case Direction.RIGHT:
                self._right_border.hide()
            case Direction.DOWN:
                self._bottom_border.hide()


class _BorderWidget(_StyleableQWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setStyleSheet("background-color: black;")


class VBorderWidget(_BorderWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setFixedWidth(5)
        self.setFixedHeight(parent.height())


class HBorderWidget(_BorderWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)

        self.setFixedWidth(parent.width())
        self.setFixedHeight(5)
