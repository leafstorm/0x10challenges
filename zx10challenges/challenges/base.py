# -*- coding: utf-8 -*-
"""
zx10challenges.challenges.base
==============================
This is the base class that individual challenges inherit from.

:copyright: (C) 2013 Matthew Frazier
:license:   MIT/X11 -- see the LICENSE file for details
"""
from abc import ABCMeta, abstractmethod
from dcpucore.assembler import AssemblyParser, Program
from dcpucore.emulator import Emulator
from dcpucore.errors import AssemblyError

class StopEvaluating(BaseException):
    pass


class Metric(object):
    """
    This represents a metric that can apply to a program.
    """
    def __init__(self, id, name, pattern):
        self.id = id
        self.name = name
        self.pattern = pattern

    def format(self, n):
        return self.pattern.format(n)


image_size = Metric("image_size", "Image size", "{} words")
exec_time = Metric("exec_time", "Execution time", "{} cycles")


class Challenge(object):
    """
    This is the base class that each challenge inherits from.
    """
    __metaclass__ = ABCMeta

    #: The ID of this challenge. This should be unique, and is used to
    #: look up the challenge from the URL etc.
    id = None

    #: The title of this challenge.
    title = None

    #: A brief, one-imperative-sentence description of this challenge.
    objective = None

    #: A more detailed description which specifies exactly what the challenge
    #: is graded on.
    spec = None

    #: The metrics that the user's program will be evaluated on.
    metrics = ()

    @abstractmethod
    def evaluate(self, submission):
        """
        This accepts a user's submission, evaluates it, and fills out the
        report fields.

        :param submission: A `Submission` object with the assembly code and
                           notes filled in.
        """
        pass

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
