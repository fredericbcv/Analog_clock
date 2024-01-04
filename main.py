#!/usr/bin/python3

# TODO 
# Add button reverse Analog <-> Num
# Add score
# Use inside polygone to detect click on needle

from math import sqrt, pi, cos, sin, acos, atan2, degrees, radians

from kivy.app import App

from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty
from kivy.vector import Vector
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line, Ellipse
from kivy.utils import get_color_from_hex
from kivy.graphics import PushMatrix, PopMatrix, Rotate

def point_inside_polygon(x, y, poly):
    '''Taken from http://www.ariel.com.au/a/python-point-int-poly.html
    '''
    n = len(poly)
    inside = False
    p1x = poly[0]
    p1y = poly[1]
    for i in range(0, n + 2, 2):
        p2x = poly[i % n]
        p2y = poly[(i + 1) % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def inside_polygon(x, y, points):
    """
    Return True if a coordinate (x, y) is inside a polygon defined by
    the list of verticies [(x1, y1), (x2, y2), ... , (xN, yN)].

    Reference: http://www.ariel.com.au/a/python-point-int-poly.html
    """
    n = len(points)
    inside = False
    p1x, p1y = points[0]
    for i in range(1, n + 1):
        p2x, p2y = points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

class Circle(Widget):
    def __init__(self, **kwargs):
        super(Circle, self).__init__(**kwargs)

        with self.canvas:
            Color(1,0,0,0.5, mode="rgba")
            self.circle = Ellipse(pos=(0,0),size=(150,150))


class clock_hand(Widget):
    def __init__(self, **kwargs):
        super(clock_hand, self).__init__(**kwargs)

        self.origin   = [0,0]
        self.endpoint = [1,1]
        self.length   = 10
        self.width    = 4
        self.selected = False

        with self.canvas.before:
            PushMatrix()
            self.rotation = Rotate(angle=0, origin=self.origin)

        with self.canvas:
            Color(0,0,0,1, mode="rgba")
            self.line = Line(points=self.origin+self.endpoint, width=self.width)

        with self.canvas.after:
            PopMatrix()


    def point_inside_line(self, pos):
        x, y = pos

        # Check x aera
        if self.origin[0] < self.endpoint[0]:
            x_range = self.origin[0]-self.width/2 <= x <= self.endpoint[0]+self.width
        else:
            x_range = self.origin[0]+self.width/2 >= x >= self.endpoint[0]-self.width

        # Check y aera
        if self.origin[1] < self.endpoint[1]:
            y_range = self.origin[1]-self.width/2 <= y <= self.endpoint[1]+self.width
        else:
            y_range = self.origin[1]+self.width/2 >= y >= self.endpoint[1]-self.width

        print(pos)
        print(self.origin)
        print(self.endpoint)
        print(x_range and y_range)
        print('----')

        return x_range and y_range

    def on_touch_down(self, touch):
        if self.point_inside_line(touch.pos):
            self.selected = True
        else:
            self.selected = False

    def on_touch_move(self, touch):
        if self.selected:
            # Set new angle
            self.rotation.angle = -degrees(atan2(touch.pos[0]-self.origin[0],touch.pos[1]-self.origin[1]))

    def on_touch_up(self,touch):
        if not self.selected:
            return

        self.endpoint_apply_angle()

        print(self.rotation.angle)
        print(self.endpoint)
        print('----')


    def endpoint_apply_angle(self):
        # Get endpoint
        x = 0
        y = self.length

        # Convert angle to radians
        if self.rotation.angle < 0:
            angle = self.rotation.angle+360
        else:
            angle = self.rotation.angle
        angle = radians(angle)

        # Calc new endpoint with Matrix
        # |cos(A) -sin(A)| * |x| = |x'|
        # |sin(A)  cos(A)|   |y|   |y'|
        # x' = cos(A)*x - sin(A)*y
        # y' = sin(A)*x + cos(A)*y

        x_ = cos(angle)*x - sin(angle)*y
        y_ = sin(angle)*x + cos(angle)*y
        x_ += self.origin[0]
        y_ += self.origin[1]

        # Update value
        self.endpoint = [x_,y_]

    def draw(self):
        self.line.points = self.origin+self.endpoint
        self.endpoint_apply_angle()
        self.rotation.origin = self.origin
        self.line.width = self.width

class root_layout(FloatLayout):
    def __init__(self,**kwargs):
        super(root_layout, self).__init__(**kwargs)

        # Create clock
        self.clock  = Circle()
        self.hour   = clock_hand()
        self.hour.size_hint = None,None
        self.minute = clock_hand()
        self.minute.size_hint = None,None

        # Create textinput
        self.textin = TextInput(write_tab=False,multiline=False)
        self.textin.size_hint = None,None
        self.textin.bind(on_text_validate=self.on_enter)

        # Add widget to layout
        self.add_widget(self.textin)
        self.add_widget(self.clock)
        self.add_widget(self.hour)
        self.add_widget(self.minute)

    def on_enter(self,instance):
        print('User pressed enter in ',instance.text)

    def do_layout(self,*args):
        self.apply_ratio()
        super(root_layout, self).do_layout()

    def apply_ratio(self):
        size_frac   = self.height/10
        diameter    = size_frac*5

        if diameter + 2*size_frac > self.width:
            size_frac = self.width/10

            if size_frac*8 < diameter:
                diameter = size_frac*8

        txt_h = size_frac*2
        span  = (self.height-diameter-txt_h)/3

        # Resize clock
        self.clock.circle.size = (diameter,diameter)
        self.clock.circle.pos  = (self.width/2-self.clock.circle.size[0]/2,self.height-span-diameter)

        # Resize hour hand clock
        self.hour.length   = diameter/2-15
        self.hour.origin   = [self.width/2,self.height-span-diameter/2]
        self.hour.endpoint = [self.width/2,self.height-span-diameter/2+self.hour.length]
        self.hour.draw()

        # Resize minute hand clock
        self.minute.width    = 6
        self.minute.length   = diameter/4
        self.minute.origin   = [self.width/2,self.height-span-diameter/2]
        self.minute.endpoint = [self.width/2,self.height-span-diameter/2+self.minute.length]
        self.minute.draw()

        # Resize textinput
        self.textin.size = (diameter,txt_h)
        self.textin.pos  = (self.width/2-self.textin.size[0]/2,span)
        self.textin.font_size = size_frac

class AnalogClockApp(App):
    def build(self):
        Window.clearcolor = (1, 1, 1, 1)
        self.root = root_layout()
        return self.root

if __name__ == '__main__':
    AnalogClockApp().run()
