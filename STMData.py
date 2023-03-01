# -*- coding: utf-8 -*-

import numpy as np


class STMData:
    UNITS = {'Z': 'm', 'I': 'A', 'V': 'V'}
    UNITS_PREFIXES = {'': 1, 'm': 10 ** 3, 'μ': 10 ** 6, 'n': 10 ** 9, 'Å': 10 ** 10, 'p': 10 ** 12}
    filename = None
    parameters = {}
    comment = {}
    filetype = None
    unit = None
    xunit = None

    def __init__(self):
        pass

    def __repr__(self):
        if self.filetype == 'Z':
            return 'Topography image'
        else:
            return 'No data'

    def auto_set_unit_xyz(self, array, unit='m'):
        min = np.amin(array)
        max = np.amax(array)
        range = max - min
        if range < 10 ** -9:
            unit = 'p' + unit
            return array * self.UNITS_PREFIXES['p'], unit
        if 10 ** -9 <= range < 10 ** -8:
            unit = 'Å'
            return array * self.UNITS_PREFIXES['Å'], unit
        if 10 ** -8 <= range < 10 ** -6:
            unit = 'n' + unit
            return array * self.UNITS_PREFIXES['n'], unit
        if 10 ** -6 <= range < 10 ** -3:
            unit = 'μ' + unit
            return array * self.UNITS_PREFIXES['μ'], unit
        if 10 ** -3 <= range < 10 ** -1:
            unit = 'm' + unit
            return array * self.UNITS_PREFIXES['m'], unit
        return array, unit

    def auto_set_unit(self, array, unit):
        min = np.amin(array)
        max = np.amax(array)
        range = max - min
        if unit == 'm':
            array, unit = self.auto_set_unit_xyz(array, unit)
            return array, unit
        if range < 10 ** -9:
            unit = 'p' + unit
            return array * self.UNITS_PREFIXES['p'], unit
        if 10 ** -9 <= range < 10 ** -6:
            unit = 'n' + unit
            return array * self.UNITS_PREFIXES['n'], unit
        if 10 ** -6 <= range < 10 ** -3:
            unit = 'μ' + unit
            return array * self.UNITS_PREFIXES['μ'], unit
        if 10 ** -3 <= range < 10 ** -1:
            unit = 'm' + unit
            return array * self.UNITS_PREFIXES['m'], unit
        return array, unit

    def update_unit(self, array, unit):
        if unit[-1] == 'm' or unit[0] == 'Å':
            if unit == 'm':
                unit = ''
            array = array*(1/self.UNITS_PREFIXES[unit[0]])
            unit = 'm'
            array, unit = self.auto_set_unit(array, unit)
            return array, unit
        else:
            if len(unit) == 2:
                array = array / self.UNITS_PREFIXES[unit[0]]
                unit = unit[-1]
            array, unit = self.auto_set_unit(array, unit)
            return array, unit

    def unit_to_si(self, array, unit):
        if unit[-1] == 'm' or unit[0] == 'Å':
            if unit == 'm':
                unit = ''
            array = array*(1/self.UNITS_PREFIXES[unit[0]])
            unit = 'm'
            return array, unit
        else:
            if len(unit) == 2:
                array = array / self.UNITS_PREFIXES[unit[0]]
                unit = unit[-1]
            return array, unit
        return array, unit

    def set_unit(self, array, old_unit, new_unit):
        array, _ = self.unit_to_si(array, old_unit)
        if new_unit in self.UNITS:
            return array
        array = array*self.UNITS_PREFIXES[new_unit[0]]
        return array