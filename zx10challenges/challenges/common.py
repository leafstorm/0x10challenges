# -*- coding: utf-8 -*-
"""
zx10challenges.challenges.common
================================
This contains some assembly-related helpers for DCPUs.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from dcpucore.assembler import AssemblyParser, Program
from dcpucore.emulator import Emulator, A, B, C, X, Y, Z, I, J
from dcpucore.errors import AssemblyError
from random import randint
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

    def check_size(self, submission, image, size_limit):
        if len(image) > size_limit:
            submission.caption = u"Your program could not be tested."
            submission.violations.append(
                u"The image size limit of {} words was exceeded.".format(
                    len(image)
                )
            )
            raise StopEvaluating

    def check_subroutines(self, submission, program, *subroutines):
        missing = [s for s in subroutines if s not in program.symbols]
        if missing:
            submission.caption = u"Your program could not be tested."
            for subroutine in missing:
                submission.violations.append(
                    u"The {} subroutine is missing.".format(subroutine)
                )
            raise StopEvaluating
        return [program.symbols[s] for s in subroutines]

    def create_emulator(self, image=None):
        emu = Emulator()
        if image is not None:
            emu.read(image)
        return emu

    def scramble_registers(self, emu, *registers):
        for reg in registers:
            emu.registers[reg] = randint(0, 0xFFFF)

    def save_registers(self, emu, *registers):
        rvalues = []
        for reg in registers:
            rvalues.append((reg, emu.registers[reg]))
        return rvalues

    def check_registers(self, case, emu, rvalues):
        bad_registers = ["ABCXYZIJ"[r] for (r, v) in rvalues if
                         emu.registers[r] != v]
        if bad_registers:
            case.passed = False
            for reg in bad_registers:
                case.violations.append(
                    u"The {} register was not restored.".format(reg)
                )

    def run_until(self, emu, stop_at_pc=0xFFFF, cycle_limit=10000):
        while emu.pc != stop_at_pc and emu.cycles < cycle_limit:
            emu.step()
        return emu.cycles < cycle_limit
