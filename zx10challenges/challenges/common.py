# -*- coding: utf-8 -*-
"""
zx10challenges.challenges.common
================================
This contains some assembly-related helpers for DCPUs.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from dcpucore.assembler import AssemblyParser, Program
from dcpucore.emulator import Emulator
from dcpucore.errors import AssemblyError
from ..models import Challenge, Metric, StopEvaluating

image_size = Metric("image_size", "Image size", "{} words")
exec_time = Metric("exec_time", "Execution time", "{} cycles")


class DCPUChallenge(Challenge):
    """
    This is a challenge class extended with some helpers for assembling
    and testing DCPU assembly code.
    """
    def summarize(self, submission):
        if all(case.passed for case in submission.test_cases):
            submission.caption = u"Your program passes all the test cases!"
            submission.passed = True
        else:
            submission.caption = u"Your program did not pass the test cases."

    def parse_and_assemble(self, submission):
        parser = AssemblyParser()
        try:
            source = submission.assembly.encode("utf8")
            instructions = parser.parse(source)
            program = Program(instructions)
            image = program.assemble()

            return program, image
        except AssemblyError as exc:
            submission.caption = u"Your program could not be assembled."
            submission.violations.append(str(exc).decode("utf8"))
            raise StopEvaluating

    def create_emulator(self, image=None):
        emu = Emulator()
        if image is not None:
            emu.read(image)
        return emu

    def run_until(self, emu, stop_at_pc=0xFFFF, cycle_limit=10000):
        while emu.pc != stop_at_pc and emu.cycles < cycle_limit:
            emu.step()
        return emu.cycles < cycle_limit
