# -*- coding: utf-8 -*-
"""
zx10challenges.challenges.numeric
=================================
Challenges related to number processing and the like.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from textwrap import dedent
from .base import Challenge, image_size, exec_time
from ..models import TestCase

def hex_list(numbers):
    return u", ".join(u"{:#06x}".format(n) for n in numbers)

class Fibonacci(Challenge):
    id = "fibonacci"
    title = "Fibonacci"
    objective = "Generate the Fibonacci numbers up to 0x10000."

    spec = dedent("""\
    The Fibonacci sequence starts with 0 and 1. Every number after that is
    the sum of the two numbers immediately before it -- so the sequence
    continues with 1 (0 + 1), 2 (1 + 1), 3 (1 + 2), 5 (2 + 3), and so on.

    Write a program that, when run, generates all the Fibonacci numbers
    less than 0x10000 (65,536) in a list starting at memory location 0x1000.
    """)

    metrics = (image_size, exec_time)

    def evaluate(self, submission):
        fibos = [0, 1]
        while fibos[-1] < 0x10000:
            fibos.append(fibos[-2] + fibos[-1])
        fibos.pop()

        program, image = self.parse_and_assemble(submission)
        submission.metrics[image_size.id] = len(image)
        last_inst = program.instructions[-1]
        end_pc = last_inst.offset + last_inst.size

        test_case = TestCase(title=u"Fibonacci numbers")
        test_case.expected_output = hex_list(fibos)

        emu = self.create_emulator(image)
        completed = self.run_until(emu, end_pc)

        if completed:
            submission.metrics[exec_time.id] = emu.cycles
            actual_fibos = [emu.memory[0x1000]]
            offset = 0x1001
            while emu.memory[offset] != 0 and offset < 0x10000:
                actual_fibos.append(emu.memory[offset])
                offset += 1

            test_case.actual_output = hex_list(actual_fibos)
            test_case.passed = fibos == actual_fibos
        else:
            test_case.passed = False
            test_case.violations.append(u"Took longer than 10,000 cycles")

        submission.test_cases.append(test_case)

        self.summarize(submission)
