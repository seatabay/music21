from collections import OrderedDict
from music21 import prebase

from typing import List, Optional, Union, TypeVar, Tuple, Dict


accidentalNameToModifier = {
    'quarter-flat': 'q-',
    'slash-flat' : '~-',
    'double-slash-flat' : '~~-',
    'flat' : '-',
    'double-flat' : '--',

    'quarter-sharp' : 'q#',
    'sharp' : '#',
    'slash-quarter-sharp': '~q#',
    'slash-sharp' : '~#',
    'double-sharp' : '##'
}

accidentalNameToAlter = {
    'quarter-flat': -1.0,
    'slash-flat' : -4.0,
    'double-slash-flat' : -8.0,
    'flat' : -5.0,
    'double-flat' : -9.0,

    'quarter-sharp' : 1.0,
    'sharp' : 4.0,
    'slash-quarter-sharp': 5.0,
    'slash-sharp' : 8.0,
    'double-sharp' : 9.0
}


#1 CENT VALUE
TWELVE_HUNDRED_ROOT_OF_TWO = 2.0 ** (1 / 1200)


#1 COMMA VALUE
ONE_COMMA = TWELVE_HUNDRED_ROOT_OF_TWO * 22.67

STEPNAMES = {'C', 'D', 'E', 'F', 'G', 'A', 'B'}  # set


default_step = "C"


class Accidental(prebase.ProtoM21Object):

    _one_comma = ONE_COMMA 

    __slots__ = (
        '_alter',
        '_displayStatus',
        '_displayType',
        '_modifier',
        '_name',
        '_client',
        '_alterInCents',
        'displayLocation',
        'displaySize',
        'displayStyle',
    )

    def __init__(self, specifier: Union[int, str, float] = 'natural'):
        super().__init__()
        self._displayType = 'normal'  
        self._displayStatus = None  

        self.displayStyle = 'normal'
        self.displaySize = 'full' 
        self.displayLocation = 'normal'

        self._client: Optional['Pitch'] = None
        self._name = None
        self._modifier = ''
        self._alter = 0.0    

        self._alterInCents = 0.0 

        self.set(specifier)


    def set(self, name):
        '''
        Change the type of the Accidental.
        '''
        if isinstance(name, str):
            name = name.lower()
        if name in ('natural', 'n', 0):
            self._name = 'natural'
            self._alter = 0.0
        elif name in ('quarter-flat', accidentalNameToModifier['quarter-flat'], -1):
            self._name = 'quarter-flat'
            self._alter = -1.0
        elif name in ('slash-flat', accidentalNameToModifier['slash-flat'], -4):
            self._name = 'slash-flat'
            self._alter = -4.0
        elif name in ('double-slash-flat', accidentalNameToModifier['double-slash-flat'], -8):
            self._name = 'double-slash-flat'
            self._alter = -8.0
        elif name in ('flat', accidentalNameToModifier['flat'], -5):
            self._name = 'flat'
            self._alter = -5.0
        elif name in ('double-flat', accidentalNameToModifier['double-flat'], -9):
            self._name = 'double-flat'
            self._alter = -9.0

        elif name in ('quarter-sharp', accidentalNameToModifier['quarter-sharp'], 1):
            self._name = 'quarter-sharp'
            self._alter = 1.0
        elif name in ('sharp', accidentalNameToModifier['sharp'], 4):
            self._name = 'sharp'
            self._alter = 4.0
        elif name in ('slash-quarter-sharp', accidentalNameToModifier['slash-quarter-sharp'], 5):
            self._name = 'slash-quarter-sharp'
            self._alter = 5.0
        elif name in ('double-sharp', accidentalNameToModifier['double-sharp'], 9):
            self._name = 'double-sharp'
            self._alter = 9.0

        self._modifier = accidentalNameToModifier[self._name]
        if self._client is not None:
            self._client.informClient()

    @property 
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value):
        self.set(value)

    @property
    def alter(self) -> float:
        return self._alter

    @alter.setter
    def alter(self, value):
        self.set(value)

    @property
    def modifier(self) -> str:
        return self._modifier
    
    @modifier.setter
    def modifier(self, value):
        self._modifier = value

    @property
    def alterInCents(self) -> float:
        return self._alter * ONE_COMMA
    

class Pitch(prebase.ProtoM21Object):
    '''
    A fundamental object that represents a single pitch of makam tradition.
    '''

    _twelve_hundred_root_of_two = TWELVE_HUNDRED_ROOT_OF_TWO

    def __init__(self, name: Optional[Union[str,int]]=None,
                **keywords):

        self._groups = None

        self._overridden_freq440 = None

        self._accidental = None
        self._octave =  None

        self._client: Optional['music21.makam.note.Note'] = None
            
        self._step = default_step
        
        if name is not None:
            if isinstance(name, str):
                self.name = name
                     
                
        if keywords:
            if 'name' in keywords:
                self.name = keywords['name'] 
            if 'step' in keywords:
                self.step = keywords['step']
            if 'octave' in keywords:
                if keywords['octave'] in [4,5,6]:
                    self._octave = keywords['octave']
                else:
                    raise ValueError("Makam tradition does not support octave {}.".format(keywords['octave']))
            if 'accidental' in keywords:
                if isinstance(keywords['accidental'], Accidental):
                    self.accidental = keywords['accidental']
                else:
                    self.accidental = Accidental(keywords['accidental'])
            if 'ps' in keywords:
                self.ps = keywords['ps']
    
    @property
    def step(self) -> str:
        return self._step
    
    @step.setter
    def step(self, usrStr: str) -> None:
        usrStr = usrStr.strip().upper()
        if len(usrStr) == 1 and usrStr in STEPNAMES:
            self._step = usrStr
            self.spellingIsInferred = False
        else:
            raise PitchException(f'Cannot make a step out of {usrStr!r}')
            
    @property    
    def accidental(self) -> Optional[Accidental]:
        return self._accidental

    @accidental.setter
    def accidental(self, value: Union[str, int, float, Accidental]):
        if isinstance(value, str):
            self._accidental = Accidental(value)
        else: 
            self._accidental = value
    
    @property
    def alter(self) -> float:
        post = 0.0
        if self.accidental is not None:
            post += self.accidental.alter
        return post


    @property
    def octave(self) -> Optional[int]:
        return self._octave

    @octave.setter
    def octave(self, value: Optional[Union[int, float]]):
        if value is not None:
            self._octave = int(value)
        else:
            self._octave = None

    @property
    def name(self):
        if self.accidental is not None:
            return self.step + self.accidental.modifier
        else:
            return self.step
        
    @name.setter
    def name(self, usrStr: str):
        usrStr = usrStr.strip()
        octFound = []
        octNot = []

        for char in usrStr:
            if char in '456':
                octFound.append(char)
            elif char in '0123789':
                raise ValueError('Makam tradition supports octave range between 4 and 6.')
            else:
                octNot.append(char)
        usrStr = ''.join(octNot)
        octFound = ''.join(octFound)
        if len(usrStr) == 1:
            self.step = usrStr
            self.accidental = None
        elif len(usrStr) > 1:
            self.step = usrStr[0]
            self.accidental = Accidental(usrStr[1:])
        else:
            raise PitchException(f'Cannot make a name out of {usrStr!r}')

        if octFound: 
            octave = int(octFound)
            self.octave = octave
    