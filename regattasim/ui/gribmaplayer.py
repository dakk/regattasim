import gi
import math

gi.require_version('Gtk', '3.0')
gi.require_version('OsmGpsMap', '1.0')

from gi.repository import Gtk, Gio, GObject, OsmGpsMap

class GribMapLayer (GObject.GObject, OsmGpsMap.MapLayer):
    def __init__ (self, grib):
        GObject.GObject.__init__ (self)
        self.grib = grib
        self.t = 0.0

    def drawWindArrow (self, cr, x, y, wdir, wspeed):
        wdir = math.radians (wdir)

        color = "0000CC"
        if wspeed>=0 and wspeed<3:color="0000CC"
        elif wspeed>=3 and wspeed<6:color="0066FF"
        elif wspeed>=6 and wspeed<9:color="00FFFF"    
        elif wspeed>=9 and wspeed<12:color="00FF66"
        elif wspeed>=12 and wspeed<15:color="00CC00"
        elif wspeed>=15 and wspeed<18:color="66FF33"
        elif wspeed>=18 and wspeed<21:color="CCFF33"
        elif wspeed>=21 and wspeed<24:color="FFFF66"
        elif wspeed>=24 and wspeed<27:color="FFCC00"
        elif wspeed>=27 and wspeed<30:color="FF9900"
        elif wspeed>=30 and wspeed<33:color="FF6600"
        elif wspeed>=33 and wspeed<36:color="FF3300"
        elif wspeed>=36 and wspeed<39:color="FF0000"
        elif wspeed>=39 and wspeed<42:color="CC6600"
        elif wspeed>=42: color="CC0000"

        a = int (color [0:2], 16) / 255.
        b = int (color [2:4], 16) / 255.
        c = int (color [4:6], 16) / 255.
        cr.set_source_rgb (a, b, c)
        
        length = 15
        cr.move_to (x, y)
        #cr.line_to (x + (wspeed / 2 * math.sin (wdir)), y + 1 * math.cos (wdir))
        cr.line_to (x + (length * math.sin (wdir)), y + (length * math.cos (wdir)))

        cr.line_to (x + (1 * math.sin (wdir - 30)), y + (1 * math.cos (wdir - 30)))
        cr.move_to (x + (length * math.sin (wdir)), y + (length * math.cos (wdir)))
        cr.line_to (x + (1 * math.sin (wdir + 30)), y + (1 * math.cos (wdir + 30)))
        
        cr.stroke ()

    def do_draw (self, gpsmap, cr):
        p1, p2 = gpsmap.get_bbox ()

        p1lat, p1lon = p1.get_degrees ()
        p2lat, p2lon = p2.get_degrees ()

        width = float (gpsmap.get_allocated_width ())
        height = float (gpsmap.get_allocated_height ())

        # Draw boat
        cr.set_line_width (1)
        cr.set_source_rgb (1,0,0)
        #print (p1lat, p1lon, p2lat, p2lon)

        bounds = ((min(p1lat,p2lat), min (p1lon, p2lon)), (max(p1lat,p2lat), max (p1lon, p2lon)))
        data = self.grib.getContinousWind (self.t, bounds)
        print (self.t)

        x = 0
        y = 0
        for r in data:
            x = 0
            for c in r:
                self.drawWindArrow (cr, x, y, c[0], c[1])
                x += width / len (r)

            y += height / len (data)
        

    def do_render (self, gpsmap):
        pass

    def do_busy (self):
        return False

    def do_button_press (self, gpsmap, gdkeventbutton):
        return False

GObject.type_register (GribMapLayer)