# -*- coding: utf-8 -*-
"""
zx10challenges.challenges.lists
===============================
Challenges related to processing lists of data.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from random import sample, randint
from textwrap import dedent
from .common import (DCPUChallenge, image_size, exec_time,
                     A, B, C, X, Y, Z, I, J)
from .numeric import hex_list
from ..models import TestCase

class BinarySearch(DCPUChallenge):
    id = "binary-search"
    version = (1, 1)
    title = "Binary search"
    objective = "Find elements of a sorted list."

    spec = dedent("""\
    When a list is in arbitrary order, it's possible that you have to search
    every item in the list in order to find out whether the list contains
    a specific item.

    However, when it's sorted, you can make the search far more efficient,
    by starting in the middle -- if the item you're searching for is higher
    than the one in the middle, you can throw away the entire bottom half
    of the list and just search the top half. Similarly, if the target item is
    smaller than the one in the middle, you can just search the bottom half.

    If you repeat this process with the half of the list you picked, you can
    find the item you're looking for (or find that it doesn't exist) much
    faster than if you had to check every item individually.
    This is called a binary search.

    Write a subroutine named `list_bsearch` that implements a binary search.
    When it's called, the B register will point to a list of unsigned
    integers, the C register will indicate the number of items in the list,
    and the A register will contain the item to search for.

    The subroutine should use binary search to find out whether A is in the
    list. If A is in the list, the subroutine should set I to the address
    where it can be found. If A is not in the list, the subroutine should
    set I to 0. All other registers (except EX) should have the same values
    when the subroutine returns as they had when it started.

    #### Notes

    * This is intended for lists with no duplicates.
      If there are multiple copies of A in the list, you can return the
      address of any of them.
    * It's possible that 0x0000 could be an item in the list. Don't worry
      about this happening.
    * Don't modify the input list.
    """)

    metrics = (image_size,)
    case_metrics = (exec_time,)

    def evaluate(self, submission):
        program, image = self.parse_and_assemble(submission)
        submission.metrics[image_size.id] = len(image)
        if len(image) > 0x1FFF:
            submission.caption = u"Your program is too large to test."
            submission.comments.append(u"Image size limit of 8191 words "
                                        "exceeded.")
            submission.passed = False
            return

        if 'list_bsearch' not in program.symbols:
            submission.caption = u"Your program does not meet the spec."
            submission.violations.append(u"There is no subroutine named "
                                          "list_bsearch.")
            submission.passed = False
            return

        l1 = self.create_list(7)
        self.case(submission, image, u"First item of odd list", l1, l1[0])
        self.case(submission, image, u"Last item of odd list", l1, l1[-1])
        self.case(submission, image, u"Middle item of odd list", l1, l1[3])

        self.case(submission, image, u"Small item in odd list", l1, l1[1])
        self.case(submission, image, u"Large item in odd list", l1, l1[-2])

        self.case(submission, image, u"Min item not in odd list", l1, 0)
        self.case(submission, image, u"Max item not in odd list", l1, 0xFFFF)

        self.case(submission, image, u"Small item not in odd list",
                                     l1, l1[0] + 1)
        self.case(submission, image, u"Large item not in odd list",
                                     l1, l1[-1] - 1)

        l2 = self.create_list(8)
        self.case(submission, image, u"First item of even list", l2, l2[0])
        self.case(submission, image, u"Last item of even list", l2, l2[-1])

        self.case(submission, image, u"Left middle item of even list",
                                     l2, l2[3])
        self.case(submission, image, u"Right middle item of even list",
                                     l2, l2[4])

        self.case(submission, image, u"Small item in even list", l2, l1[1])
        self.case(submission, image, u"Large item in even list", l2, l1[-2])

        self.case(submission, image, u"Min item not in odd list", l1, 0)
        self.case(submission, image, u"Max item not in odd list", l1, 0xFFFF)

        self.case(submission, image, u"Small item not in odd list",
                                     l1, l1[0] + 1)
        self.case(submission, image, u"Large item not in odd list",
                                     l1, l1[-1] - 1)

        self.summarize(submission)

    def create_list(self, n):
        l = sample(xrange(1, 0xFFFF, 2), n)
        l.sort()
        return l

    def case(self, submission, image, title, data, target):
        base = randint(0x2000, 0xF000 - len(data))
        if target in data:
            target_address = base + data.index(target)
        else:
            target_address = 0

        test_case = TestCase(title=title)
        test_case.input["A"] = "{:#06x}".format(target)
        test_case.input["B"] = "{:#06x}".format(base)
        test_case.input["C"] = "{:#06x}".format(len(data))
        test_case.input["List at {:#06x}".format(base)] = hex_list(data)

        test_case.expected_output["I"] = "{:#06x}".format(target_address)

        emu = self.create_emulator(image)
        emu.read(data, base)
        emu.registers[A] = target
        emu.registers[B] = base
        emu.registers[C] = len(data)
        emu.push(0xFFFF)

        self.scramble_registers(emu, X, Y, Z, I, J)
        regs = self.save_registers(emu, A, B, C, X, Y, Z, J)

        if self.run_until(emu, 0xFFFF):
            test_case.metrics[exec_time.id] = emu.cycles

            i = emu.registers[I]
            test_case.passed = i == target_address
            test_case.actual_output["I"] = "{:#06x}".format(i)

            for idx, value in enumerate(data):
                if emu.memory[base + idx] != value:
                    test_case.passed = False
                    test_case.violations.append(u"Input list was modified.")
                    break
            self.check_registers(test_case, emu, regs)
        else:
            test_case.passed = False
            test_case.violations.append(u"Took longer than 10,000 cycles")

        submission.test_cases.append(test_case)
