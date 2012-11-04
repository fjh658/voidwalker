# (void)walker user interface
# Copyright (C) 2012 David Holm <dholmster@gmail.com>

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


class Widget(object):
    def draw(self, terminal, width):
        raise NotImplementedError()


class Section(Widget):
    _name = None
    _components = None

    def __init__(self, name):
        self._name = name
        self._components = []

    def _draw_header(self, terminal, width):
        title = ''
        if self._name:
            title = ('[%s]' % self._name)
        assert terminal.string_width(title) <= width

        header = ['%(face-header)s']
        dashes = width - len(title)
        header += ['-' for i in range(dashes)]
        header += [title, '\n']
        terminal.write(''.join(header))

    def add_component(self, component):
        self._components.append(component)

    def draw(self, terminal, width):
        width -= (width / 20)
        self._draw_header(terminal, width)

        for component in self._components:
            component.draw(terminal, width)


class Table(Widget):
    class Cell(Widget):
        def __init__(self, contents=''):
            super(Table.Cell, self).__init__()
            self._contents = ''
            if contents:
                self._contents = (' %s ' % contents)

        def width(self, terminal):
            return terminal.string_width(self._contents)

        def draw(self, terminal, width):
            assert self.width(terminal) <= width
            padding = ' ' * (width - self.width(terminal))
            terminal.write(('%(contents)s%(padding)s' %
                            {'contents': self._contents,
                             'padding': padding}))

    class Row(Widget):
        def __init__(self):
            super(Table.Row, self).__init__()
            self._cells = []

        def cells(self):
            return self._cells

        def add_cell(self, cell):
            self._cells.append(cell)

        def width(self, terminal):
            width = 0
            for cell in self._cells:
                width += cell.width(terminal)
            return width

        def draw(self, terminal, cell_widths):
            assert len(cell_widths) == len(self._cells)
            assert self.width(terminal) <= sum(cell_widths)

            for i in range(len(self._cells)):
                self._cells[i].draw(terminal, cell_widths[i])

    def _max_cell_width(self, terminal):
        max_width = 0
        for cell in self._cells:
            max_width = max(max_width, cell.width(terminal))
        return max_width

    def __init__(self):
        self._rows = []
        self._cells = []

    def add_cell(self, cell):
        assert isinstance(cell, Table.Cell)
        self._cells.append(cell)

    def add_row(self, row):
        assert isinstance(row, Table.Row)
        self._rows.append(row)

    def _draw_cells(self, terminal, width):
        cell_width = self._max_cell_width(terminal)
        cells_per_row = width / cell_width
        assert cells_per_row

        cell_row_width = (cell_width * cells_per_row)
        row_padding_begin = (width - cell_row_width) / 2
        row_padding_end = (width - cell_row_width - row_padding_begin)

        terminal.write('%s' % (' ' * row_padding_begin))
        cell_offset = 0
        for cell in self._cells:
            if cells_per_row <= cell_offset:
                cell_offset = 0
                terminal.write(('%s\n%s' % (' ' * row_padding_end,
                                            ' ' * row_padding_begin)))

            cell.draw(terminal, cell_width)
            cell_offset += 1

        last_row_padding = (width - (cell_width * cell_offset) -
                            row_padding_begin)
        terminal.write('%s\n' % (' ' * last_row_padding))

    def _draw_rows(self, terminal, width):
        cell_widths = []
        for row in self._rows:
            cells = len(row.cells())
            cell_widths.extend([0] * (cells - len(cell_widths)))

            for i in range(len(row.cells())):
                cell_widths[i] = max(cell_widths[i],
                                     row.cells()[i].width(terminal))

        row_width = sum(cell_widths)
        for row in self._rows:
            row.draw(terminal, cell_widths)
            padding = ' ' * (width - row_width)
            terminal.write('%s\n' % padding)

    def draw(self, terminal, width):
        if self._rows:
            self._draw_rows(terminal, width)
        if self._cells:
            self._draw_cells(terminal, width)