import os
import gi
import RPi.GPIO as GPIO
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator, GObject as gobject
gi.require_version("Gtk", "3.0")

pin = 18
temp = 50

class MainWindow(gtk.Window):
  def __init__(self):
    self.mode = 'auto'

    gtk.Window.__init__(self, title='simple cpu fan')
    self.connect('delete_event',self.close)
    self.set_border_width(15)

    self.menu = gtk.Menu()
    self.TempDisplay = gtk.MenuItem('C')
    self.TempDisplay.connect('activate',self.show)
    self.menu.append(self.TempDisplay)
    exititem = gtk.MenuItem('退出')
    exititem.connect('activate', quit)
    self.menu.append(exititem)
    self.menu.show_all()
    
    indicator = appindicator.Indicator.new('CPU-Fan', '/home/pi/Documents/cpu-fan.png', appindicator.IndicatorCategory.APPLICATION_STATUS)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(self.menu)
    self.indicator = indicator
    
    self.box = gtk.Box(spacing = 6)
    self.add(self.box)
    self.temp_label = gtk.Label('-- ℃')
    self.box.pack_start(self.temp_label, True, True, 0)
    self.status_label = gtk.Label()
    self.box.pack_start(self.status_label, True, True, 0)

    self.switch = gtk.Switch()
    self.switch.connect('notify::active', self.switch_active)
    self.switch.set_sensitive(False)
    self.box.pack_start(self.switch, True, True, 0)
    # switch.set_active(False)

    button1 = gtk.RadioButton.new_with_label_from_widget(None, '自动')
    button1.connect('toggled', self.on_button_toggled, 'auto')
    self.box.pack_start(button1, False, False, 0)
    button2 = gtk.RadioButton.new_with_label_from_widget(button1, '手动')
    button2.connect('toggled', self.on_button_toggled, 'man')
    self.box.pack_start(button2, False, False, 0)

  def loop(self):
    current = int(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000

    self.temp_label.set_label(str(current) + ' ℃')
    self.TempDisplay.set_label(str(current) + ' ℃')

    if self.mode == 'auto':
      if current >= temp:
        self.high()
      else:
        self.low()
      
    return True

  def quit(self,_):
    gtk.main_quit()

  def high(self):
    GPIO.output(pin,GPIO.HIGH)
    self.status_label.set_label('启动')
    self.indicator.set_icon('/home/pi/Documents/cpu-fan.png')

  def low(self):
    GPIO.output(pin,GPIO.LOW)
    self.status_label.set_label('停止')
    self.indicator.set_icon(os.path.abspath('/home/pi/Documents/cpu-fan-o.png'))

  def switch_active(self,switch, gparam):
    if switch.get_active():
      self.high()
    else:
      self.low()

  def on_button_toggled(self, button, name):
    if not button.get_active():
      return
    self.switch.set_sensitive(name == 'man')
    self.mode = name
    if name == 'man':
      self.switch.set_active(True)

  def startTimer(self):
    self.loop()
    gobject.timeout_add(3000,self.loop)

  def show(self, _):
    self.show_all()

  def close(self, widget, data=None):
    self.hide()
    return True

GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin,GPIO.OUT)
win = MainWindow()
win.show_all()
win.startTimer()
gtk.main()