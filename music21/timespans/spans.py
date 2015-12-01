# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# Name:         timespans/spans.py
# Purpose:      Tools for grouping notes and chords into a searchable tree
#               organized by start and stop offsets
#
# Authors:      Josiah Wolf Oberholtzer
#               Michael Scott Cuthbert
#
# Copyright:    Copyright © 2013-15 Michael Scott Cuthbert and the music21
#               Project
# License:      LGPL or BSD, see license.txt
#------------------------------------------------------------------------------
'''
Tools for grouping notes and chords into a searchable tree
organized by start and stop offsets.
''' 
import unittest

from music21 import exceptions21

from music21.exceptions21 import TimespanException
from music21 import environment
environLocal = environment.Environment("timespans.spans")
#------------------------------------------------------------------------------
class TimespanSpanException(exceptions21.TimespanException):
    pass

class Timespan(object):
    r'''
    A span of time, with a start offset and stop offset.

    Useful for demonstrating various properties of the timespan-collection class
    family.

    >>> timespan = timespans.spans.Timespan(-1.5, 3.25)
    >>> print(timespan)
    <Timespan -1.5 3.25>
    
    A timespan has two attributes, its offset and its endTime.  They are immutable...
    
    >>> timespan.offset
    -1.5
    >>> timespan.endTime
    3.25
    
    To create a changed timespan, call the .new() method on the timespan.
    
    >>> ts2 = timespan.new(offset=0.0)
    >>> ts2
    <Timespan 0.0 3.25>

    >>> ts3 = timespan.new(endTime=5.0)
    >>> ts3
    <Timespan -1.5 5.0>
    
    Two timespans are equal if they have the same offset and endTime
    
    >>> ts4 = timespans.spans.Timespan(-1.5, 5.0)
    >>> ts3 == ts4
    True
    >>> ts4 == ts2
    False
    '''
    __slots__ = (
        '_offset',
        '_endTime',
        )


    def __init__(self, offset=float('-inf'), endTime=float('inf')):
        if offset is not None:
            offset = float(offset)
        self._offset = offset
        if endTime is not None:
            endTime = float(endTime)
        self._endTime = endTime
        if offset is not None and endTime is not None:
            if offset > endTime:
                raise TimespanException('offset %r must be after endTime %r' % (offset, endTime))

    def __eq__(self, expr):
        if type(self) is type(expr):
            if self.offset == expr.offset:
                if self.endTime == expr.endTime:
                    return True
        return False

    def __repr__(self):
        return '<{} {} {}>'.format(
            type(self).__name__,
            self.offset,
            self.endTime,
            )


    @property
    def offset(self):
        r'''
        The start offset of the elementTimespan's element, relative to its
        containing score.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[0]
        >>> elementTimespan.offset
        1.0
        '''
        # this is a property to make it immutable.
        return self._offset

    @property
    def endTime(self):
        r'''
        The stop offset of the elementTimespan's element, relative to its
        containing score.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[0]
        >>> elementTimespan.endTime
        2.0
        '''
        # this is a property to make it immutable.
        return self._endTime

    def new(self, offset=None, endTime=None):
        '''
        return a new object with the given offset and endTime
        '''
        if offset is None:
            offset = self.offset
        if endTime is None:
            endTime = self.endTime

        return type(self)(offset=offset, endTime=endTime)
        

    def canMerge(self, other):
        '''
        returns a tuple of (True or False) if these timespans can be merged
        with the second element being a message or None.
        
        >>> ts1 = timespans.spans.Timespan(0, 5)
        >>> ts2 = timespans.spans.Timespan(5, 7)
        >>> ts1.canMerge(ts2)
        (True, '')
        >>> ts3 = timespans.spans.Timespan(6, 10)
        >>> ts1.canMerge(ts3)
        (False, 'Cannot merge <Timespan 0.0 5.0> with <Timespan 6.0 10.0>: not contiguous')

        Overlapping Timespans cannot be merged, just contiguous ones.

        >>> ts4 = timespans.spans.Timespan(3, 4)
        >>> ts1.canMerge(ts4)
        (False, 'Cannot merge <Timespan 0.0 5.0> with <Timespan 3.0 4.0>: not contiguous')
        '''
        if not isinstance(other, type(self)):
            message = 'Cannot merge {} with {}: wrong types'.format(
                self, other)
            return (False, message)
        if not ((self.endTime == other.offset) or
                (other.endTime == self.offset)):
            message = 'Cannot merge {} with {}: not contiguous'.format(
                self, other)
            return (False, message)
        return (True, "")

    def mergeWith(self, other):
        r'''
        Merges two consecutive/contiguous timespans, keeping the
        information from the former of the two.
        
        >>> ts1 = timespans.spans.Timespan(0, 5)
        >>> ts2 = timespans.spans.Timespan(5, 7)
        >>> ts3 = ts1.mergeWith(ts2)
        >>> ts3
        <Timespan 0.0 7.0>

        Note that (for now), overlapping timespans cannot be merged:
        
        >>> ts4 = timespans.spans.Timespan(6, 10)
        >>> ts3.mergeWith(ts4)
        Traceback (most recent call last):
        TimespanException: Cannot merge <Timespan 0.0 7.0> with 
            <Timespan 6.0 10.0>: not contiguous        
        '''
        can, message = self.canMerge(other)
        if can is False:
            raise TimespanException(message)
        
        if self.offset < other.offset:
            mergedTimespan = self.new(endTime=other.endTime)
        else:
            mergedTimespan = other.new(endTime=self.endTime)
        return mergedTimespan
    
    def splitAt(self, offset):
        r'''
        Split elementTimespan at `offset`.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(0)
        >>> verticality
        <Verticality 0 {A3 E4 C#5}>
        
        >>> timespan = verticality.startTimespans[0]
        >>> timespan
        <ElementTimespan (0.0 to 0.5) <music21.note.Note C#>>

        >>> for shard in timespan.splitAt(0.25):
        ...     shard
        ...
        <ElementTimespan (0.0 to 0.25) <music21.note.Note C#>>
        <ElementTimespan (0.25 to 0.5) <music21.note.Note C#>>

        >>> timespan.splitAt(1000)
        (<ElementTimespan (0.0 to 0.5) <music21.note.Note C#>>,)
        '''

        if offset < self.offset or self.endTime < offset:
            return (self,)
        left = self.new(endTime=offset)
        right = self.new(offset=offset)
        return left, right
    
    
#------------------------------------------------------------------------------


class ElementTimespan(Timespan):
    r'''
    A span of time anchored to an element in a score.  The span of time may
    be the same length as the element in the score.  It may be shorter (a
    "slice" of an element) or it may be longer (in the case of a timespan
    that is anchored to a single element but extends over rests or other
    notes following a note)

    ElementTimespans give information about an element (such as a Note).  It knows
    its absolute position with respect to the element passed into TimespanTree.  
    It contains information about what measure it's in, what part it's in, etc.

    Example, getting a passing tone from a known location from a Bach chorale.

    First we create an Offset tree:

    >>> score = corpus.parse('bwv66.6')
    >>> tree = score.asTimespans()
    >>> tree
    <TimespanTree {165} (0.0 to 36.0) <music21.stream.Score ...>>

    Then get the verticality from offset 6.5, which is beat two-and-a-half of
    measure 2 (the piece is in 4/4 with a quarter-note pickup)

    >>> verticality = tree.getVerticalityAt(6.5)
    >>> verticality
    <Verticality 6.5 {E3 D4 G#4 B4}>

    There are four elementTimespans in the verticality -- each representing
    a note.  The notes are arranged from lowest to highest.


    We can find all the elementTimespans that start exactly at 6.5. There's
    one.

    >>> verticality.startTimespans
    (<ElementTimespan (6.5 to 7.0) <music21.note.Note D>>,)

    >>> elementTimespan = verticality.startTimespans[0]
    >>> elementTimespan
    <ElementTimespan (6.5 to 7.0) <music21.note.Note D>>

    What can we do with a elementTimespan? We can get its Part object or the
    Part object name

    >>> elementTimespan.part
    <music21.stream.Part Tenor>
    >>> elementTimespan.part.partName
    'Tenor'

    Find out what measure it's in:

    >>> elementTimespan.measureNumber
    2
    >>> elementTimespan.parentOffset
    5.0

    The position in the measure is given by subtracting that from the
    .offset:

    >>> elementTimespan.offset - elementTimespan.parentOffset
    1.5

    >>> elementTimespan.beatStrength
    0.125
    >>> elementTimespan.element
    <music21.note.Note D>

    These are not dynamic, so changing the Score object does not change the
    measureNumber, beatStrength, etc.
    
    
    For quick score reductions, we can merge two consecutive 
    like-pitched element timespans, keeping
    score-relevant information from the first of the two, such as its
    Music21 Element, and any beatstrength information.

    This is useful when using timespans to perform score reduction.

    Let's demonstrate merging some contiguous E's in the alto part of a Bach
    chorale:

    >>> score = corpus.parse('bwv66.6')
    >>> tree = score.asTimespans()
    >>> timespan_one = tree[12]
    >>> print(timespan_one)
    <ElementTimespan (2.0 to 3.0) <music21.note.Note E>>

    >>> print(timespan_one.part)
    <music21.stream.Part Alto>

    >>> timespan_two = tree.findNextElementTimespanInSameStreamByClass(timespan_one)
    >>> print(timespan_two)
    <ElementTimespan (3.0 to 4.0) <music21.note.Note E>>
        
    >>> merged = timespan_one.mergeWith(timespan_two)
    >>> print(merged)
    <ElementTimespan (2.0 to 4.0) <music21.note.Note E>>

    >>> merged.part is timespan_one.part
    True

    >>> merged.beatStrength == timespan_one.beatStrength
    True

    Attempting to merge timespans which are not contiguous, or which do not
    have identical pitches will result in error:

    >>> tree[0].mergeWith(tree[50])
    Traceback (most recent call last):
    TimespanException: Cannot merge <ElementTimespan (0.0 to 0.5) <music21.note.Note C#>> 
            with <ElementTimespan (9.5 to 10.0) <music21.note.Note B>>: not contiguous

    This is probably not what you want to do: get the next element timespan in
    the same score:

    >>> timespan_twoWrong = tree.findNextElementTimespanInSameStreamByClass(
    ...     timespan_one, classList=(stream.Score,))
    >>> print(timespan_twoWrong)
    <ElementTimespan (3.0 to 4.0) <music21.note.Note C#>>
    >>> print(timespan_twoWrong.part)
    <music21.stream.Part Soprano>        
    '''

    ### CLASS VARIABLES ###

    __slots__ = (
        '_beatStrength',
        '_element',
        '_parentOffset',
        '_parentEndTime',
        '_parentage',
        )

    ### INITIALIZER ###

    def __init__(
        self,
        element=None,
        beatStrength=None,
        parentOffset=None,
        parentEndTime=None,
        parentage=None,
        offset=None,
        endTime=None,
        ):
        super(ElementTimespan, self).__init__(offset=offset, endTime=endTime)
        
        self._element = element
        if parentage is not None:
            parentage = tuple(parentage)
        self._parentage = parentage
        if beatStrength is not None:
            beatStrength = float(beatStrength)
        self._beatStrength = beatStrength
        if parentOffset is not None:
            parentOffset = float(parentOffset)
        self._parentOffset = parentOffset
        if parentEndTime is not None:
            parentEndTime = float(parentEndTime)
        self._parentEndTime = parentEndTime
        if parentOffset is not None and parentEndTime is not None:
            if parentOffset > parentEndTime:
                raise TimespanException(
                    'offset %r must be after parentEndTime %r' % (parentOffset, parentEndTime))

    ### SPECIAL METHODS ###
    def __eq__(self, other):
        if self is other:
            return True
        else:
            return False

    def __repr__(self):
        return '<{} ({} to {}) {!r}>'.format(
            type(self).__name__,
            self.offset,
            self.endTime,
            self.element,
            )

    ### PUBLIC METHODS ###
    
    def canMerge(self, other):
        '''
        submethod of base canMerge that checks to see if the pitches are the same.
        '''
        can, message = super(ElementTimespan, self).canMerge(other)
        if can is True:
            if self.pitches != other.pitches:
                message = 'Cannot merge {} with {}: different pitches'.format(
                    self, other)
                can = False                
        return (can, message)


    def new(
        self,
        beatStrength=None,
        element=None,
        parentOffset=None,
        parentEndTime=None,
        offset=None,
        endTime=None,
        ):
        '''
        Create a new object that is identical to the calling object
        but with some of the parameters overridden.
        
        TODO: Docs and Tests
        '''
        if beatStrength is None:
            beatStrength = self.beatStrength
        element = element or self.element
        if parentOffset is None:
            parentOffset = self.parentOffset
        if parentEndTime is None:
            parentEndTime = self.parentEndTime
        if offset is None:
            offset = self.offset
        if endTime is None:
            endTime = self.endTime
        
        return type(self)(
            beatStrength=beatStrength,
            element=element,
            parentOffset=parentOffset,
            parentEndTime=parentEndTime,
            parentage=self.parentage,
            offset=offset,
            endTime=endTime,
            )


    ### PUBLIC PROPERTIES ###

    @property
    def beatStrength(self):
        r'''
        The elementTimespan's element's beat-strength.

        This may be overriden during instantiation by passing in a custom
        beat-strength. That can be useful when you are generating new
        elementTimespans based on old ones, and want to maintain pitch
        information from the old elementTimespan but change the start offset to
        reflect that of another timespan.
        
        TODO: Tests
        '''
        from music21 import meter
        if self._beatStrength is not None:
            return self._beatStrength
        elif self._element is None:
            return None
        try:
            return self._element.beatStrength
        except meter.MeterException as e:
            environLocal.warn("Could not get a beatStrength from %r: %s" % (self._element, e))
            return None

    @property
    def quarterLength(self):
        '''
        TODO: Tests that show a case where this might be different from the quarterLength
        of the element.
        '''
        return self.endTime - self.offset

    @property
    def element(self):
        r'''
        The elementTimespan's element.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[0]
        >>> elementTimespan.element
        <music21.note.Note A>
        '''
        return self._element

    @property
    def measureNumber(self):
        r'''
        The measure number of the measure containing the element.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[0]
        >>> elementTimespan.measureNumber
        1
        '''
        return self.element.measureNumber
        #from music21 import stream
        #for x in self.parentage:
        #    if not isinstance(x, stream.Measure):
        #        continue
        #    return x.measureNumber
        #return None

    @property
    def parentOffset(self):
        return self._parentOffset

    @property
    def parentEndTime(self):
        return self._parentEndTime

    @property
    def parentage(self):
        r'''
        The Stream hierarchy above the elementTimespan's element.

        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[0]
        >>> for streamSite in elementTimespan.parentage:
        ...     streamSite
        <music21.stream.Measure 1 offset=1.0>
        <music21.stream.Part Soprano>
        <music21.stream.Score ...>
        '''
        return self._parentage

    def getParentageByClass(self, classList=None):
        '''
        returns that is the first parentage that has this classList.
        default stream.Part

        >>> score = corpus.parse('bwv66.6')
        >>> score.id = 'bach'
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[2]
        >>> elementTimespan
        <ElementTimespan (1.0 to 2.0) <music21.note.Note C#>>
        >>> elementTimespan.getParentageByClass(classList=(stream.Part,))
        <music21.stream.Part Tenor>
        >>> elementTimespan.getParentageByClass(classList=(stream.Measure,))
        <music21.stream.Measure 1 offset=1.0>
        >>> elementTimespan.getParentageByClass(classList=(stream.Score,))
        <music21.stream.Score bach>

        The closest parent is returned in case of a multiple list...

        >>> searchTuple = (stream.Voice, stream.Measure, stream.Part)
        >>> elementTimespan.getParentageByClass(classList=searchTuple)
        <music21.stream.Measure 1 offset=1.0>

        '''
        from music21 import stream
        if classList is None:
            classList = (stream.Part,)
        for parent in self.parentage:
            for c in classList:
                if isinstance(parent, c):
                    return parent
        return None

    @property
    def part(self):
        '''
        find the object in the parentage that is a Part object:
        
        >>> score = corpus.parse('bwv66.6')
        >>> tree = score.asTimespans()
        >>> verticality = tree.getVerticalityAt(1.0)
        >>> elementTimespan = verticality.startTimespans[2]
        >>> elementTimespan
        <ElementTimespan (1.0 to 2.0) <music21.note.Note C#>>
        >>> elementTimespan.part
        <music21.stream.Part Tenor>
        '''
        from music21 import stream
        return self.getParentageByClass(classList=(stream.Part,))


    @property
    def pitches(self):
        r'''
        Gets the pitches of the element wrapped by this elementTimespan.

        This treats notes as chords.
        
        TODO: tests, examples of usage.
        TODO: by sorting are we losing information about overlaps?
        '''
        result = []
        if hasattr(self.element, 'pitches'):
            result.extend(self.element.pitches)
        result.sort()
        return tuple(result)



#------------------------------------------------------------------------------

class Test(unittest.TestCase):

    def runTest(self):
        pass


if __name__ == "__main__":
    import music21
    music21.mainTest(Test)
