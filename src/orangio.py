
import os
import tcod
import time
import textwrap

from const import *
import managers   
import maths
##import word



    #colors
WHITE=tcod.Color(255,255,255)
BLACK=tcod.Color(0,0,0)

    #global key and mouse handlers for all objects in OrangIO
key = tcod.Key()
mouse = tcod.Mouse()


'''###
#key_bindings.txt
    #This is the backup key bindings file

    #To add a new command into the game, add it into the key_bindings.txt
    #defaults below. Add Shift+ or Ctrl+ or Alt+ or any combo thereof.
    #Delete the key_bindings.txt file from the game's directory to
    #have the game recreate it using the defaults.
    #   - Do not use spaces.
    #   - To use special keys, including spacebar:
            refer to the TEXT_TO_KEY dict.
    #   - Take note of the placement you put the command into the text file.
    #Put that command into the dict COMMANDS in the SAME ORDER that you put
    #it into key_bindings.
    #   - Put the command into player.commands or player.const_commands.
    #       (If using this as a third party module, simply run
    #       handle_mousekeys and check that the result == the desired command)
    
#if you add new commands you must add new key bindings for those commands.
#key bindings begin on a new line,
    #and consist of any combination of the following:
        #Ctrl+
        #Shift+
        #Alt+
    #followed by a key constant as defined in TEXT_TO_KEY
        #or a letter/number/symbol on the keyboard.
    #ALERT: To get the ? key:
        #do the key combination Shift+/ instead of ?
        #IN GENERAL, only use the lowercase keys and indicate Shift+
        #in order to indicate that the uppercase character should be used.
        #Example: to make a command respond to the command ">",
            #the command must be written as Shift+.
            #(shift+ period key)
    #Note: NumPad is not currently supported. NumPad must be OFF during play.
    #Note: commands are not case-sensitive.
###'''


COMMANDS = {        # translate commands into actions

    tcod.event.KeySym.SLASH     : {'help': True},
    tcod.event.KeySym.KP_2      : {'context-dir': (0, -1,  0,) },
    tcod.event.KeySym.k         : {'context-dir': (0, -1,  0,) },
    tcod.event.KeySym.KP_4      : {'context-dir': (-1, 0,  0,) },
    tcod.event.KeySym.h         : {'context-dir': (-1, 0,  0,) },
    tcod.event.KeySym.KP_2      : {'context-dir': (0,  1,  0,) },
    tcod.event.KeySym.j         : {'context-dir': (0,  1,  0,) },
    tcod.event.KeySym.KP_6      : {'context-dir': (1,  0,  0,) },
    tcod.event.KeySym.l         : {'context-dir': (1,  0,  0,) },
    tcod.event.KeySym.KP_7      : {'context-dir': (-1, -1, 0,) },
    tcod.event.KeySym.y         : {'context-dir': (-1, -1, 0,) },
    tcod.event.KeySym.KP_1      : {'context-dir': (-1, 1,  0,) },
    tcod.event.KeySym.b         : {'context-dir': (-1, 1,  0,) },
    tcod.event.KeySym.KP_3      : {'context-dir': (1,  1,  0,) },
    tcod.event.KeySym.n         : {'context-dir': (1,  1,  0,) },
    tcod.event.KeySym.KP_9      : {'context-dir': (1, -1,  0,) },
    tcod.event.KeySym.u         : {'context-dir': (1, -1,  0,) },
    tcod.event.KeySym.KP_5      : {'context-dir': (0,  0,  0,) },
    tcod.event.KeySym.PERIOD    : {'context-dir': (0,  0,  0,) },
    tcod.event.KeySym.e         : {'context-dir': (0,  0,  1,) },
    tcod.event.KeySym.N1        : {'use1': True},
    tcod.event.KeySym.z         : {'use1': True},
    tcod.event.KeySym.N2        : {'use2': True},
    tcod.event.KeySym.x         : {'use2': True},
    tcod.event.KeySym.N3        : {'use3': True},
    tcod.event.KeySym.c         : {'use3': True},
    tcod.event.KeySym.SPACE     : {'context': True},
    tcod.event.KeySym.a         : {'character-page': True},
    tcod.event.KeySym.SEMICOLON : {'look': True},
    tcod.event.KeySym.f         : {'find player': True},
    tcod.event.KeySym.m         : {'message history': True},
    tcod.event.Quit             : {'quit game': True},

    tcod.event.KeySym.UP        : {'menu-nav': (0, -1,  0,) },
    tcod.event.KeySym.LEFT      : {'menu-nav': (-1, 0,  0,) },
    tcod.event.KeySym.DOWN      : {'menu-nav': (0,  1,  0,) },
    tcod.event.KeySym.RIGHT     : {'menu-nav': (1,  0,  0,) },
    tcod.event.KeySym.RETURN    : {'select': True},
    tcod.event.KeySym.ESCAPE    : {'exit': True},
    tcod.event.KeySym.PAGEUP    : {'page up': True},
    tcod.event.KeySym.PAGEDOWN  : {'page down': True},
    tcod.event.KeySym.HOME      : {'home': True},
    tcod.event.KeySym.END       : {'end': True},
    tcod.event.KeySym.DELETE    : {'delete': True},
    tcod.event.KeySym.INSERT    : {'insert': True},
    tcod.event.KeySym.BACKSPACE : {'backspace': True},
    
    tcod.event.KeySym.BACKQUOTE : {'console': True},
    tcod.event.KeySym.N0        : {'last cmd': True},
}












#-----------#
#  classes  #
#-----------#


#
# cursor
#
    
class Cursor:
    
    def __init__(self,x=0,y=0,rate=0.3):
        self.set_pos(x,y)
        self.time_stamp = 0
        self.blink_time = rate
        
    def set_pos(self,x,y):  self._x = x; self._y = y;
    def draw(self,con=0):   console_invert_color(con,self.x,self.y)
        
    def blink(self):
        if time.time() - self.time_stamp > self.blink_time:
            self.blink_reset_timer_off()
            return True
        else: return False
        
    def blink_reset_timer_off(self):
        self.time_stamp = time.time()
    def blink_reset_timer_on(self):
        self.time_stamp = 0
        
    @property
    def x(self): return self._x
    @property
    def y(self): return self._y


#
# Text Input Manager
#
#

# Display user-entered text field with blinking cursor
# and handle all processes thereof.

# key bindings should NEVER affect input for this function.
# that got nasty real fast in Caves of Qud...

#---------------Args----------------#
# int x,y           location on screen
# int w,h           width and height of textbox
# string default    text that appears when textbox is created
# string mode       'text' or 'wait' :
#   - text mode: normal input mode, returns text when Enter key pressed
#   - wait mode: returns first accepted key press input
# bool insert       begin in "insert" mode?
#

VK_TO_CHAR = {      # translate key consants into a char
    tcod.KEY_KP0     : '0',
    tcod.KEY_KP1     : '1',
    tcod.KEY_KP2     : '2',
    tcod.KEY_KP3     : '3',
    tcod.KEY_KP4     : '4',
    tcod.KEY_KP5     : '5',
    tcod.KEY_KP6     : '6',
    tcod.KEY_KP7     : '7',
    tcod.KEY_KP8     : '8',
    tcod.KEY_KP9     : '9',
    tcod.KEY_KPDEC   : '.',
    
    tcod.KEY_UP          : chr(K_UP),
    tcod.KEY_DOWN        : chr(K_DOWN),
    tcod.KEY_RIGHT       : chr(K_RIGHT),
    tcod.KEY_LEFT        : chr(K_LEFT),
    tcod.KEY_BACKSPACE   : chr(K_BACKSPACE),
    tcod.KEY_DELETE      : chr(K_DELETE),
    tcod.KEY_INSERT      : chr(K_INSERT),
    tcod.KEY_PAGEUP      : chr(K_PAGEUP),
    tcod.KEY_PAGEDOWN    : chr(K_PAGEDOWN),
    tcod.KEY_HOME        : chr(K_HOME),
    tcod.KEY_END         : chr(K_END),
    tcod.KEY_ENTER       : chr(K_ENTER),
    tcod.KEY_KPENTER     : chr(K_ENTER),
    tcod.KEY_ESCAPE      : chr(K_ESCAPE),
}
class TextInputManager(managers.Manager): #Manager_Input | ManagerInput
    
    def __init__(self, x,y, w,h, default,mode,insert):
        
        # init
        self.console    = tcod.console_new(w, h)
        self.init_time  = time.time()
        
        self.x=x
        self.w=w
        self.y=y
        self.h=h
        self.mode=mode
        self.text="" if mode=="wait" else default
        self.default=default
        
        self.keyInput=''
        
        self.redraw_cursor  = True
        self.render_text    = True
        self.flush          = False
        
        self.key=key
        self.mouse=mouse
        
        self.cursor=Cursor()
        self.cursor.set_pos(x,y)
        self.insert_mode=insert #replace the character under the cursor or shift it aside?
        
        #ignore buffer
        get_raw_input()


    def set_result(self,val):
        if val == '': val=self.default
        if val == '': val='0'
        elif val == '\x1c': val='0'
        super(TextInputManager,self).set_result(val)
    
    def run(self):
        super(TextInputManager, self).run()
        
##        # manually close game #
##        if libtcod.console_is_window_closed():
##            #sys.exit() # no, there should be a custom exit func
        
        tcod.sys_sleep_milli(5)  #reduce CPU usage
        
        self.update()
        
        tcod.sys_check_for_event(    # check don't wait.
            tcod.EVENT_KEY
            | tcod.EVENT_MOUSE_PRESS     # we only want to know mouse press
            | tcod.EVENT_MOUSE_RELEASE,  # or release, NOT mouse move event.
            self.key, self.mouse)
        
        self.get_char()
        self.mouse_events()
        self.keyboard_events()
    
    def close(self):
        ##do not inherit
        tcod.console_delete(self.console)
    
    def update(self):
        
        self.flush=False
        
        if self.cursor.blink():
            self.redraw_cursor=True
            
        if self.render_text:
            self.update_render_text()
            self.redraw_cursor=True
            
        if self.redraw_cursor:
            self.cursor.draw()
            self.flush=True
            
        if self.flush:
            tcod.console_flush()

        #now we've updated, turn all update variables to False
        self.redraw_cursor  =False
        self.render_text    =False
        self.flush          =False

    def keyboard_events(self):
        
        if self.keyInput:

            if self.mode == "wait": # CHANGED. Was just self.set_result(self.keyInput). Test that all Input() uses are still working properly using "wait" mode.
                if (ord(self.keyInput) == K_ESCAPE):
                    self.set_result(self.default)
                else:
                    self.set_result(self.keyInput)

            self.redraw_cursor=True
            self.cursor_blinkOn()

            if self.mode == "text":
                self.input_vk()
                self.input_text()

    def mouse_events(self):
        
        if self.mouse.lbutton_pressed:
            self.cursor_blinkOn()
            self.putCursor(self.mouse.cx - self.x)
            self.blit_console()
            self.flush=True


    def input_vk(self):
        
        if not tcod.console_is_key_pressed(self.key.vk):
            return

        cpos=self.cursor_pos
        ans=ord(self.keyInput)

        # returning a result
        if (ans == K_ENTER):    self.set_result(self.text)
        if (ans == K_ESCAPE):   self.set_result(self.default)

        # deleting
        if (ans == K_BACKSPACE) :
            self.render_text=True
            self.putCursor(cpos - 1)
            self.delete()
        elif (ans == K_DELETE) :
            self.render_text=True
            self.delete()
        # moving
        elif (ans == K_LEFT)    : self.move(cpos - 1)
        elif (ans == K_RIGHT)   : self.move(cpos + 1)
        
        # insert mode
        elif (ans == K_INSERT)  : self.insert_mode = not self.insert_mode


    def input_text(self):

        if not self.key.vk == tcod.KEY_TEXT:
            return
        
        ans=self.keyInput
        if self.cursor_pos < len(self.text): # insert or replace
            self.render_text=True
            first_half = self.text[:self.cursor_pos]
            second_half = self.text[self.insert_mode + self.cursor_pos:]
            self.text='{}{}{}'.format(first_half, ans, second_half)
        else:   # append
            self.text += ans
            self.put_next_char(ans)
            self.blit_console()
            self.flush=True

        # truncate
        if (len(self.text) > self.w):
            self.text = self.text[:self.w]
        
        # move cursor
        self.putCursor(self.cursor_pos + 1)
        #


    def move(self, new):
        tcod.console_set_char_foreground(
            0, self.x + self.cursor_pos, self.y, WHITE)
        tcod.console_set_char_background(
            0, self.x + self.cursor_pos, self.y, BLACK)
        self.flush=True
        self.putCursor(new)

    def update_render_text(self):
        tcod.console_clear(self.console)
        tcod.console_print_ex(
            self.console,0,0,
            tcod.BKGND_NONE,tcod.LEFT,
            self.text )
        self.blit_console()
    
    def get_char(self):
        reply=''
        if tcod.console_is_key_pressed(self.key.vk):
            reply = VK_TO_CHAR.get(self.key.vk, None)
        
        elif self.key.vk == tcod.KEY_TEXT:
            tx = self.key.text #.decode()
            if (ord(tx) >= 128 or tx == '%'):
                return ''    # Prevent problem-causing input
            else: reply=tx
        self.keyInput=reply

    def delete(self):
        self.text=self.text[:self.cursor_pos] + self.text[1+self.cursor_pos:]
        
    def put_next_char(self,new):
        tcod.console_put_char_ex(
            self.console, self.cursor_pos,0, new,
            WHITE,BLACK
        )
    def blit_console(self):
        tcod.console_blit(
            self.console,   0,0,self.w,self.h,
            0,      self.x,self.y
        )    
    '''def ignore_buffer(self):
        return (time.time() - self.init_time < .05)'''
    def putCursor(self,new):
        pos=maths.restrict( new, 0, min(self.w - 1, len(self.text)) )
        self.cursor.set_pos(self.x + pos, self.y)
    def cursor_blinkOn(self):   self.cursor.blink_reset_timer_on()
    
    @property
    def cursor_pos(self):   return self.cursor.x


#--------------------------------------------------#




#-----------#
# functions #
#-----------#


# tcod #

def color_invert(rgb):
    return tcod.Color(255-rgb[0],255-rgb[1],255-rgb[2])
def console_invert_color(con,x,y):
    col1 = tcod.console_get_char_foreground(con,x,y)
    col2 = tcod.console_get_char_background(con,x,y)
    tcod.console_set_char_foreground(con, x,y, color_invert(col1))
    tcod.console_set_char_background(con, x,y, color_invert(col2))

#
#
# get raw input
#
# checks for input
# returns key and mouse objects in a tuple
#
def get_raw_input():
    tcod.sys_sleep_milli(1)  # prevent from checking a billion times/second to reduce CPU usage

    # we use the check_for_event instead of the wait_for_event function
    # because wait_for_event causes lots of problems
    tcod.sys_check_for_event(
        tcod.EVENT_KEY
        | tcod.EVENT_MOUSE_PRESS     # we only want to know mouse press
        | tcod.EVENT_MOUSE_RELEASE,  # or release, NOT mouse move event.
        key, mouse)
    return (key,mouse,)


#Input
#wrapper function to get a simple input from the user
def Input(x,y, w=1,h=1, default='',mode='text',insert=False):
    manager=TextInputManager(x,y, w,h, default,mode,insert)
    result=None
    while not result:
        manager.run()
        result=manager.result
    manager.close()
    return result


def wait_for_command(context):
    for event in tcod.event.wait():
##        context.convert_event(event)
        if isinstance(event, tcod.event.Quit):
            print(event)
            raise SystemExit()
        if isinstance(event, tcod.event.KeyDown):
            if event.sym in COMMANDS.keys():
                command = COMMANDS[event.sym]
##                print("command: ", command)
                return command
    return {"None" : True}
            


# help page
def render_help() -> str: # may not display all commands
    return ''' ~~~~~ Help / Command List ~~~~~

Command =================== Default Key Combo

 ~~~~~ Global commands ~~~~~
show this help page ======= Shift+/
show submarine status ===== a

 ~~~~~ Movement controls ~~~~~
# Default movement controls use vim keys or keypad numbers

up ======================== k -or- keypad 8 -or- UP
left ====================== h -or- keypad 4 -or- LEFT
down ====================== j -or- keypad 2 -or- DOWN
right ===================== l -or- keypad 6 -or- RIGHT
up-left =================== y -or- keypad 7
down-left ================= b -or- keypad 1
down-right ================ n -or- keypad 3
up-right ================== u -or- keypad 9
towards self ============== . -or- keypad 5
enter passage ============= Shift+.

 ~~~~~ Basic controls ~~~~~
context action ============ Space
use module 1 ============== 1 -or- Z
use module 2 ============== 2 -or- X
use module 3 ============== 3 -or- C
use module 4 ============== 4 -or- V

'''


