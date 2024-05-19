from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.core.image import Image
from kivy.core.text import Label
from kivy.config import Config
from kivy.base import EventLoop

import random, json, os

class WrApp(App):
  def build(self):
    return Cv()

class Cv(Widget):
  def __init__(self):
    global values

    super(Cv, self).__init__()
  
    with open("data.json") as fl:
      self.d = json.load(fl)

    if "inventory.json" in os.listdir():
      with open("inventory.json") as fl:
        self.i = json.load(fl)
    else:
      self.i = {x:0 for x in self.d["values"].keys()}

    with open("gossip.json") as fl:
      self.library = json.load(fl)

    self.location = "The Office"
    self.history = ["The Office"]
    self.get_supply()

    Clock.schedule_once(self.resize, 0.1)
    Clock.schedule_interval(self.momentum, 0.02)
    self.hysteresis = 0
    self.p = 0
    self.clicking = None

    with self.canvas:
      self.rect=Rectangle(texture=Image(f"imgs/{self.location}.png").texture,
                          size=(self.width,self.height), pos=(0,0))
      Color(.8,1,.5,1)
      self.buttons=[Line(points=(0,0),width=2) for x in range(30)]

      Color(.8,1,.5,.2)
      self.fill=Rectangle(size=(0,0), pos=(0,0))
      
      Color(1,1,1)
      self.textr = [Label(font_size=self.height/50, bold=True, outline_width=2) 
                    for x in range(len(self.buttons))]
      self.labels=[Rectangle(size=(0,0), pos=(0,0)) for x in range(len(self.buttons))]

      self.icons = [Rectangle(size=(0,0), pos=(0,0), outline_width=3) for x in range(20)]

      self.gossip = Rectangle(size=(0,0), pos=(0,0))

      Color(.8,1,.5,1)
      self.score_label = Label(font_size=self.height/40, bold=True, outline_width=3)
      self.score = Rectangle(size=(0,0), pos=(0,0))

    self.label_text = ["" for x in range(len(self.buttons))]
    self.bind(size=self.resize)
    EventLoop.window.bind(on_keyboard=self.hook_keyboard)

  def momentum(self, *args):
    if self.clicking:
      if self.hysteresis < 25:
        self.hysteresis += 1
      else:
        self.hysteresis = 22
        self.p+=.2
        for _ in range(int(self.p)+1):
          self.buy_or_sell(*self.clicking)
        self.set_buttons()

  def buy_or_sell(self, x, buying):
    if "supply" not in dir(self) or x not in self.supply:
      return
    if (buying and self.i["Paperclips"] >= self.supply[x][1]
        and self.supply[x][0] > 0):
      self.supply[x][0] -= 1
      self.i["Paperclips"] -= self.supply[x][1]
      self.i[x] += 1
    elif not buying and self.i[x] > 0:
      self.supply[x][0] += 1
      self.i["Paperclips"] += self.supply[x][1]
      self.i[x] -= 1

  def get_supply(self):
    if self.location in self.d["supply"]:
      self.supply = {x:[int(y[0]*random.random()*2), 
                        int((y[1]+(y[2]-y[1])*random.random())*self.d["values"][x])] 
                     for x,y in self.d["supply"][self.location].items()}

  def net_worth(self):
    x = sum([self.i[x]*self.d["values"][x] for x in self.d["values"].keys()])
    if "max_net_worth" not in self.d or x > self.d["max_net_worth"]:
      self.d["max_net_worth"] = x
    return x

  def add_icon(self, box, icon):
    new_icon = [x for x in range(len(self.icons))
      if self.icons[x].size[0] == 0][0]+1
    self.icons[new_icon].size = [box[2] * self.height] * 2
    self.icons[new_icon].pos = (box[0] * self.width, box[1] * self.height)
    if box[0]==0:
      self.icons[new_icon].pos = ((self.width-self.icons[new_icon].size[0])/2,
        self.icons[new_icon].pos[1])
    self.icons[new_icon].texture = Image(f"imgs/{icon}.png", mipmap=True).texture

    self.icons[new_icon-1].size = [x+4 for x in self.icons[new_icon].size]
    self.icons[new_icon-1].pos = [x-2 for x in self.icons[new_icon].pos]

  def add_button(self, points, text):
    new_button = [x for x in range(len(self.buttons))
      if len(self.buttons[x].points)<3][0]
    self.buttons[new_button].points=self.box(points)
    self.label_text[new_button] = text
    self.textr[new_button].font_size = self.height/50
    self.textr[new_button].text=text
    self.textr[new_button].refresh()
    self.labels[new_button].texture = self.textr[new_button].texture
    self.labels[new_button].size = self.textr[new_button].texture.size
    x,y,w,h=self.unbox(new_button)
    self.labels[new_button].pos = ( 
       x + (w - self.textr[new_button].texture.size[0]) / 2,
       y + (h - self.textr[new_button].texture.size[1]) / 2)

  def hook_keyboard(self, window, key, *largs):
    if key == 27:
      if len(self.history) > 1:
        self.history = self.history[:-1]
      self.location = self.history[-1]
      self.get_supply()
      self.set_buttons()
      return True

  def resize(self, a, b=0):
    self.rect.size=self.size
    self.textr = [Label(font_size=self.height/50, bold=True, outline_width=2,
                        halign='center', valign='middle') 
                  for x in range(len(self.buttons))]
    self.score_label = Label(font_size=self.height/40, bold=True, outline_width=3)
    self.set_buttons()

  def on_touch_down(self, t):
    self.hysteresis = 0
    self.p = 0
    self.on_touch_move(t)

  def on_touch_move(self, t):
    self.clicking = None
    self.fill.pos=(0,0)
    self.fill.size=(0,0)
    for x in range(len(self.buttons)):
      if self.clicked(t, x):
        self.fill.pos = self.unbox(x)[0:2]
        self.fill.size = self.unbox(x)[2:4]
        self.clicking = [self.label_text[x].split("\n")[0].split(" ")[-1],
                         self.label_text[x].split(" ")[0]=="Buy"]

  def set_buttons(self):
    self.rect.texture = Image(f"imgs/{self.location}.png").texture
    self.fill.size=(0,0)
    self.fill.pos=(0,0)

    self.score_label.text=f"Net worth: ${self.net_worth()/100:,.2f}"
    self.score_label.refresh()
    self.score.texture = self.score_label.texture
    self.score.size=self.score_label.texture.size
    self.score.pos=(0,self.height-self.score_label.texture.height)

    self.net_worth()

    for x in range(len(self.buttons)):
      self.buttons[x].points=(0,0)
      self.labels[x].size = (0,0)
      self.labels[x].pos = (0,0)

    for x in range(len(self.icons)):
      self.icons[x].size = (0,0)
      self.icons[x].pos = (0,0)

    if self.location == "The Office":
      self.add_button((.16,.56,.5,.13), "HR")
      if self.d["max_net_worth"] > 10:
        self.add_button((.3,.15,.6,.15), "Marketing")
      if self.d["max_net_worth"] > 100:
        self.add_button((.2,.31,.5,.15), "Engineering")
      if self.d["max_net_worth"] > 1000:
        self.add_button((.19,.47,.48,.08), "IT")
      if self.d["max_net_worth"] > 100000:
        self.add_button((.18,.7,.4,.12), "C-Suite")
      if self.d["max_net_worth"] > 1000000:
        self.add_button((.69,.01,.3,.09), "Suburbs")

    else:
      self.add_button((.05,.025,.15,.05), "Back")
      self.add_icon((0,.65,.1), "Paperclips")
      self.add_button((.05,.65,.3,.1), f"Scrounge\nfor Paperclips\n#: {self.i['Paperclips']}")
      self.add_button((.65,.65,.3,.1), "Gossip")

      if self.d["max_net_worth"] > 1:
        self.add_icon((0,.54,.1), "Pens")
        self.add_button((.05,.54,.3,.1), 
                        f"Buy Pens\n#: {self.supply['Pens'][0]}\n{self.supply['Pens'][1]}c")
        self.add_button((.65,.54,.3,.1), 
                        f"Sell Pens\n#: {self.i['Pens']}\n{self.supply['Pens'][1]}c")
      if self.d["max_net_worth"] > 100:
        self.add_icon((0,.43,.1), "Markers")
        self.add_button((.05,.43,.3,.1), 
                        f"Buy Markers\n#: {self.supply['Markers'][0]}\n{self.supply['Markers'][1]}c")
        self.add_button((.65,.43,.3,.1), 
                        f"Sell Markers\n#: {self.i['Markers']}\n{self.supply['Markers'][1]}c")
      if self.d["max_net_worth"] > 1000:
        self.add_icon((0,.32,.1), "Paper")
        self.add_button((.05,.32,.3,.1), 
                        f"Buy Paper\n#: {self.supply['Paper'][0]}\n{self.supply['Paper'][1]}c")
        self.add_button((.65,.32,.3,.1), 
                        f"Sell Paper\n#: {self.i['Paper']}\n{self.supply['Paper'][1]}c")
      if self.d["max_net_worth"] > 10000:
        self.add_icon((0,.21,.1), "Heater")
        self.add_button((.05,.21,.3,.1), 
                        f"Buy Heater\n#: {self.supply['Heater'][0]}\n{self.supply['Heater'][1]}c")
        self.add_button((.65,.21,.3,.1), 
                        f"Sell Heater\n#: {self.i['Heater']}\n{self.supply['Heater'][1]}c")
      if self.d["max_net_worth"] > 100000:
        self.add_icon((0,.1,.1), "Chair")
        self.add_button((.05,.1,.3,.1), 
                        f"Buy Chair\n#: {self.supply['Chair'][0]}\n{self.supply['Chair'][1]}c")
        self.add_button((.65,.1,.3,.1), 
                        f"Sell Chair\n#: {self.i['Chair']}\n{self.supply['Chair'][1]}c")

    with open("inventory.json","w") as fl:
      json.dump(self.i, fl, indent=2, sort_keys=True)

  def add_gossip(self, text):

    gl = Label(text=text, font_size=self.height/50, bold=True, halign='center',
      outline_width=2, size=(self.width*.9, self.height*.2), valign='middle') 
    gl.refresh()
    self.gossip.texture = gl.texture
    self.gossip.size = (gl.texture.width,gl.texture.height)
    self.gossip.pos = ((self.width - gl.texture.width)*.5,self.height*.76
      + (self.height*.2-gl.texture.height)/2)

  def on_touch_up(self, t):

    if self.location != "The Office":
      if self.clicked(t, "Scrounge"):
        if random.random()>0.5:
          self.add_gossip("Found a paperclip!")
          self.i["Paperclips"] += 1
        else:
          self.add_gossip("Couldn't find anything")

      if self.clicked(t, "Gossip"):
        self.add_gossip(random.choice(self.library[self.location]))

      if self.clicked(t, "Back"):
        self.location = "The Office"
        self.add_gossip("")

      for x in self.d["values"].keys():
        if self.clicked(t, "Buy " + x):
          self.buy_or_sell(x, True)
        elif self.clicked(t, "Sell " + x):
          self.buy_or_sell(x, False)

    for x in self.d["locations"]:
      if self.clicked(t, x):
        self.location = x

    if self.location != self.history[-1]:
      self.get_supply()
      self.history.append(self.location)

    self.clicking = None

    self.set_buttons()

  def clicked(self, t, xywh):
    if isinstance(xywh, str):
      xywh = ([x for x in range(len(self.label_text))
        if self.label_text[x].split("\n")[0]==xywh] + [-1])[0]
    if isinstance(xywh, int):
      if xywh == -1 or len(self.buttons[xywh].points) < 3:
        return False
      x,y,w,h=self.unbox(xywh)
    else:
      x,y,w,h=xywh
      x,y,w,h=x*self.width,y*self.height,w*self.width,h*self.height
    return t.x>x and t.x<x+w and t.y>y and t.y<y+h

  def box(self, xywh):
    x,y,w,h=xywh
    x,y,w,h=x*self.width,y*self.height,w*self.width,h*self.height
    return (x,y,x+w,y,x+w,y+h,x,y+h,x,y)

  def unbox(self, b):
    x = self.buttons[b].points[0]
    y = self.buttons[b].points[1]
    w = self.buttons[b].points[2]-x
    h = self.buttons[b].points[5]-y
    return x,y,w,h

if __name__=="__main__":
  Config.set('graphics', 'width', '432')
  Config.set('graphics', 'height', '960')
  WrApp().run()
