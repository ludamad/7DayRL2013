import libtcodpy as libtcod
from geometry import *
from utils import *
import console
import colors

screen = console.Console()

def _cat_string_parts(header):
    s=""
    for i in range(0, len(header), 2):
        s += header[i+1]
    return s

def menu(header, options, width, index_color=colors.WHITE):
    from globals import SCREEN_SIZE

    if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')
 
    #calculate total height for the header (after auto-wrap) and one line per option
    header_height = screen.get_height_rect( Rect(0, 0, width, SCREEN_SIZE.h), _cat_string_parts(header))
    if _cat_string_parts(header) == 0:
        header_height = 0
    height = len(options) + header_height
 
    #create an off-screen console that represents the menu's window
    window = console.Console( Size(width, height) )
 
    #print the header, with auto-wrap
    window.set_default_foreground(libtcod.white)
    
    window.print_rect_ex(Rect(0, 0, width, height), libtcod.BKGND_NONE, libtcod.LEFT, "")
    print_colored(window, Pos(0,0), *header)
 
    #print all the options
    y = header_height
    index = 1
    for option_text in options:
        print_colored(window, Pos(0,y), index_color, str(index) + " ", *option_text)

        y += 1
        index += 1
 
    #blit the contents of "window" to the root console
    x = SCREEN_SIZE.w/2 - width/2
    y = SCREEN_SIZE.h/2 - height/2
    window.blit(Rect(0, 0, width, height), screen, Pos(x, y), 1.0, 0.7)
 
    #present the root console to the player and wait for a key-press
    screen.flush()
    while True:
        key = console.wait_for_keypress(True)
        if not key.pressed:
            continue
     
        #convert the ASCII code to an index; if it corresponds to an option, return it
        if key.c == ord('0'):
            index = 10
        else:
            index = key.c - ord('1')
        if index >= 0 and index < len(options): 
            return index
        return None
#        elif key.c != ord('i'):
#            return None

def msgbox(text, width=50):
    menu(text, [], width) 

class Message:
    def __init__(self, message):
        self.message = message
        self.occurences = 1
class Messages:
    def __init__(self, amount_to_draw):
        self.messages = []
        self.amount_to_draw = amount_to_draw
    def add(self, msg):
        amount = len(self.messages) 
        if amount > 0 and self.messages[amount-1].message == msg:
            self.messages[amount-1].occurences += 1
        else:
            self.messages.append(Message(msg))
            if amount+1 > self.amount_to_draw:
                del self.messages[0 : amount+1 - self.amount_to_draw]
    def draw(self, con, xy):
        for msg in self.messages:
            contents = msg.message
            if msg.occurences > 1:
                contents = list(contents) + [colors.PALE_GREEN,  ' x' + str(msg.occurences)]
            print_colored(con, xy, *contents)
            xy += Pos(0, 1)