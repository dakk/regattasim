# -*- coding: utf-8 -*-
# Copyright (C) 2017-2021 Davide Gessa
'''
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

For detail about GNU see <http://www.gnu.org/licenses/>.
'''

import time
import gi
import math
from threading import Thread

gi.require_version('Gtk', '3.0')
gi.require_version('OsmGpsMap', '1.0')

from gi.repository import Gtk, Gio, GObject, OsmGpsMap

from .. import config
from .aboutdialog import AboutDialog
from .routingwizarddialog import RoutingWizardDialog
from .gribselectdialog import GribSelectDialog
from .gribmaplayer import GribMapLayer
from .isochronesmaplayer import IsochronesMapLayer

UI_INFO = """
<ui>
	<menubar name='MenuBar'>
		<menu action='FileMenu'>
			<menuitem action='FileNew' />
			<menuitem action='FileOpen' />
			<menuitem action='FileSave' />
			<menuitem action='FileSaveAs' />
			<separator />
			<menuitem action='FileTakeScreenshoot' />
			<separator />
			<menuitem action='FileQuit' />
		</menu>
		<menu action='ViewMenu'>
		</menu>
		<menu action='GribMenu'>
			<menuitem action='GribSet' />
		</menu>
		<menu action='RoutingMenu'>
			<menuitem action='RoutingWizard' />
			<separator />
			<menuitem action='RoutingSavePath' />
		</menu>
		<menu action='HelpMenu'>
			<menuitem action='HelpAbout' />
		</menu>
	</menubar>
	<toolbar name='ToolBar'>
		<toolitem action='FileNew' />
		<toolitem action='FileOpen' />
		<toolitem action='FileSave' />
		<separator />
		<toolitem action='RoutingWizard' />
		<toolitem action='RoutingSavePath' />
	</toolbar>
</ui>
"""



class MainWindow(Gtk.Window):
	def __init__(self, core):
		Gtk.Window.__init__ (self, title="Regatta Simulator - New file")

		settings = Gtk.Settings.get_default ()
		#settings.set_property ("gtk-application-prefer-dark-theme", False)

		self.core = core
		self.openedFile = None

		self.set_default_size (800, 600)
		self.maximize ()

		box = Gtk.Box (orientation=Gtk.Orientation.VERTICAL)

		# Menu
		action_group = Gtk.ActionGroup ("actions")

		action_filemenu = Gtk.Action ("FileMenu", "File", None, None)
		action_group.add_action(action_filemenu)

		act = Gtk.Action ("FileNew", None, None, Gtk.STOCK_NEW)
		act.connect ("activate", self.onNew)
		action_group.add_action (act)

		act = Gtk.Action ("FileOpen", None, None, Gtk.STOCK_OPEN)
		act.connect ("activate", self.onOpen)
		action_group.add_action (act)
				
		act = Gtk.Action ("FileSave", None, None, Gtk.STOCK_SAVE)
		act.connect ("activate", self.onSave)
		action_group.add_action (act)

		act = Gtk.Action ("FileSaveAs", None, None, Gtk.STOCK_SAVE_AS)
		act.connect ("activate", self.onSaveAs)
		action_group.add_action (act)

		act = Gtk.Action ("FileTakeScreenshoot", 'Take Screenshoot', None, Gtk.STOCK_ZOOM_FIT)
		act.connect ("activate", self.onQuit)
		action_group.add_action (act)

		act = Gtk.Action ("FileQuit", None, None, Gtk.STOCK_QUIT)
		act.connect ("activate", self.onQuit)
		action_group.add_action (act)

		action_filemenu = Gtk.Action ("ViewMenu", "View", None, None)
		action_group.add_action(action_filemenu)

		action_filemenu = Gtk.Action ("GribMenu", "Grib", None, None)
		action_group.add_action(action_filemenu)

		act = Gtk.Action ("GribSet", 'Set grib', None, Gtk.STOCK_COLOR_PICKER)
		act.connect ("activate", self.onGribSelect)
		action_group.add_action (act)


		action_filemenu = Gtk.Action ("RoutingMenu", "Routing", None, None)
		action_group.add_action(action_filemenu)


		act = Gtk.Action ("RoutingWizard", 'Routing...', None, Gtk.STOCK_MEDIA_PLAY)
		act.connect ("activate", self.onRoutingWizard)
		action_group.add_action (act)

		act = Gtk.Action ("RoutingSavePath", 'Save path', None, Gtk.STOCK_SAVE)
		act.connect ("activate", self.onQuit)
		action_group.add_action (act)

		action_filemenu = Gtk.Action ("HelpMenu", "Help", None, None)
		action_group.add_action(action_filemenu)

		act = Gtk.Action ("HelpAbout", 'About', None, Gtk.STOCK_ABOUT)
		act.connect ("activate", self.onAbout)
		action_group.add_action (act)

		uimanager = Gtk.UIManager ()
		uimanager.add_ui_from_string (UI_INFO)
		accelgroup = uimanager.get_accel_group ()
		self.add_accel_group (accelgroup)

		uimanager.insert_action_group (action_group)
		self.menubar = uimanager.get_widget ("/MenuBar")
		box.pack_start (self.menubar, False, False, 0)

		self.toolbar = uimanager.get_widget("/ToolBar")
		box.pack_start(self.toolbar, False, False, 0)


		### Center
		boxcenter = Gtk.Box (orientation=Gtk.Orientation.HORIZONTAL)
		box.pack_start (boxcenter, True, True, 0)



		## Map area
		self.osm = OsmGpsMap.Map () #repo_uri="http://acetate.geoiq.com/tiles/acetate-hillshading/#Z/#X/#Y.png", image_format='png')
		self.osm.connect ('button_press_event', self.onMapClick)

		#self.openseaMapLayer = #repo_uri="http://t1.openseamap.org/seamark/#Z/#X/#Y.png", image_format='png')
		#self.osm.layer_add (self.openseaMapLayer)

		self.osm.set_center_and_zoom (39., 9., 6)

		self.isochronesMapLayer = IsochronesMapLayer ()
		self.osm.layer_add (self.isochronesMapLayer)

		self.gribMapLayer = GribMapLayer (self.core.grib)
		self.osm.layer_add (self.gribMapLayer)

		self.osm.layer_add (OsmGpsMap.MapOsd (show_dpad=True, show_zoom=True, show_crosshair=False))
		boxcenter.pack_start (self.osm, True, True, 0)

		self.notebook = Gtk.Notebook ()
		boxcenter.pack_start (self.notebook, False, False, 0)

		## Track
		boxtrack = Gtk.Box (orientation=Gtk.Orientation.VERTICAL)
		self.notebook.append_page(boxtrack, Gtk.Label ('Track'))

		self.trackStore = Gtk.ListStore (int, float, float)
		self.trackTree = Gtk.TreeView (self.trackStore)

		renderer = Gtk.CellRendererText ()
		self.trackTree.append_column (Gtk.TreeViewColumn(" ", renderer, text=0))
		self.trackTree.append_column (Gtk.TreeViewColumn("Latitude", renderer, text=1))
		self.trackTree.append_column (Gtk.TreeViewColumn("Longitude", renderer, text=2))

		scbar = Gtk.ScrolledWindow ()
		scbar.set_hexpand (False)
		scbar.set_vexpand (True)
		scbar.add (self.trackTree)
		boxtrack.pack_start (scbar, True, True, 0)

		# Track controls
		boxtrackcontrols = Gtk.Box (orientation=Gtk.Orientation.HORIZONTAL)
		boxtrack.pack_start (boxtrackcontrols, False, False, 0)

		button = Gtk.Button.new_from_stock (Gtk.STOCK_GO_UP)
		button.connect ("clicked", self.onWaypointUp)
		boxtrackcontrols.pack_start (button, True, True, 0)

		button = Gtk.Button.new_from_stock (Gtk.STOCK_GO_DOWN)
		button.connect ("clicked", self.onWaypointDown)
		boxtrackcontrols.pack_start (button, True, True, 0)

		button = Gtk.Button.new_from_stock (Gtk.STOCK_REMOVE)
		button.connect ("clicked", self.onWaypointRemove)
		boxtrackcontrols.pack_start (button, True, True, 0)

		boxtrack.pack_start (Gtk.Separator (), False, False, 10)
		
		boxtrack.pack_start (Gtk.Label ('Latitude:'), False, False, 0)
		self.waypointLat = Gtk.Entry ()
		boxtrack.pack_start (self.waypointLat, False, False, 3)
		
		boxtrack.pack_start (Gtk.Label ('Longitude:'), False, False, 0)
		self.waypointLon = Gtk.Entry ()
		boxtrack.pack_start (self.waypointLon, False, False, 3)

		button = Gtk.Button.new_with_label ('Insert')
		button.connect ("clicked", self.addWaypoint)
		boxtrack.pack_start (button, False, False, 0)

		## Simulation Controls
		boxcontrols = Gtk.Box (orientation=Gtk.Orientation.VERTICAL)
		self.notebook.append_page(boxcontrols, Gtk.Label ('Routing'))

		self.timeScale = Gtk.HScale ()
		self.timeScale.set_adjustment (Gtk.Adjustment(0.0, 0.0, 120.0, 0.1, 1.0, 1.0))
		self.timeScale.connect ("change-value", self.timeScaleChange)
		boxcontrols.pack_start (self.timeScale, False, False, 10)


		self.routingProgress = Gtk.ProgressBar ()
		boxcontrols.pack_start (self.routingProgress, False, False, 10)

		
		"""
		self.simulationStore = Gtk.ListStore (int, str, float, float)
		self.simulationTree = Gtk.TreeView (self.simulationStore)

		renderer = Gtk.CellRendererText ()
		self.simulationTree.append_column (Gtk.TreeViewColumn("Time", renderer, text=0))
		self.simulationTree.append_column (Gtk.TreeViewColumn("TWD", renderer, text=1))
		self.simulationTree.append_column (Gtk.TreeViewColumn("TWS", renderer, text=2))
		self.simulationTree.append_column (Gtk.TreeViewColumn("TWA", renderer, text=3))
		self.simulationTree.append_column (Gtk.TreeViewColumn("HDG", renderer, text=4))
		self.simulationTree.append_column (Gtk.TreeViewColumn("Speed", renderer, text=5))

		scbar = Gtk.ScrolledWindow ()
		scbar.set_hexpand (False)
		scbar.set_vexpand (True)
		scbar.add (self.simulationTree)
		boxcontrols.pack_start (scbar, True, True, 0)
		"""
		
		# Status bar
		self.statusbar = Gtk.Statusbar ()
		self.statusbar.push (self.statusbar.get_context_id ('Info'), 'Regatta Simulator started')
		box.pack_start (self.statusbar, False, False, 0)

		self.add (box)
		self.show_all ()

		#self.onOpen (self)


	########### Routing

	def onRoutingWizard (self, widget):
		if len (self.core.getTrack ()) < 2:
			edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Error")
			edialog.format_secondary_text ("You need at least 2 track points to create a routing path")
			edialog.run ()
			edialog.destroy ()
			return

		dialog = RoutingWizardDialog (self)
		response = dialog.run ()

		if response == Gtk.ResponseType.OK:
			self.currentRouting = self.core.createRouting (dialog.getSelectedAlgorithm (), dialog.getSelectedBoat (), dialog.getInitialTime ())
			self.notebook.set_current_page (1)
			GObject.timeout_add (10, self.onRoutingStep)

		dialog.destroy ()
		
	def onRoutingStep (self):
		res = self.currentRouting.step ()
		self.isochronesMapLayer.setIsochrones (res['isochrones'])
		self.gribMapLayer.time = res['time']
		self.osm.queue_draw ()
		self.timeScale.set_value (res['time'])

		track = OsmGpsMap.MapTrack ()
		track.set_property ("line-width", 5)
		for wp in res['path']:
			p = OsmGpsMap.MapPoint ()
			p.set_degrees (wp[0], wp[1])
			track.add_point (p)
		
		self.osm.track_add (track)		

		if not self.currentRouting.isEnd ():
			GObject.timeout_add (1000, self.onRoutingStep)


	def timeScaleChange (self, range, scroll, value):
		self.gribMapLayer.time = value
		self.osm.queue_draw ()



	########### Help

	def onAbout (self, widget):
		dialog = AboutDialog (self)
		response = dialog.run ()
		dialog.destroy ()



	########### Track
	
	def onNew (self, widget):
		self.openedFile = None
		self.core.getTrack ().clear ()
		self.updateTrack ()
		self.set_title ('Regatta Simulator - New file')

	def onSave (self, widget):
		if self.openedFile == None:
			return self.onSaveAs (widget)

		if self.core.save (self.openedFile):
			self.statusbar.push (self.statusbar.get_context_id ('Info'), 'Saved %d waypoints to %s' % (len (self.core.getTrack ()), self.openedFile))					
		else:
			edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Error")
			edialog.format_secondary_text ("Cannot save file: %s" % self.openedFile)
			edialog.run ()
			edialog.destroy ()


	def onSaveAs (self, widget):
		dialog = Gtk.FileChooserDialog ("Please select a destination", self,
					Gtk.FileChooserAction.SAVE,
					(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

		filter_gpx = Gtk.FileFilter()
		filter_gpx.set_name("GPX track")
		filter_gpx.add_mime_type("application/gpx+xml")
		filter_gpx.add_pattern ('*.gpx')
		dialog.add_filter(filter_gpx)

		response = dialog.run ()

		if response == Gtk.ResponseType.OK:
			filepath = dialog.get_filename ()
			
			if not filepath.endswith('.gpx'):
				filepath += '.gpx'

			if self.core.save (filepath):
				self.openedFile = filepath
				self.set_title ('Regatta Simulator - %s' % filepath)
				self.statusbar.push (self.statusbar.get_context_id ('Info'), 'Saved %d waypoints to %s' % (len (self.core.getTrack ()), self.openedFile))
			else:
				edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Error")
				edialog.format_secondary_text ("Cannot save file: %s" % filepath)
				edialog.run ()
				edialog.destroy ()
			
		dialog.destroy ()


	def onOpen (self, widget):
		dialog = Gtk.FileChooserDialog ("Please choose a file", self,
					Gtk.FileChooserAction.OPEN,
					(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
			
		filter_gpx = Gtk.FileFilter ()
		filter_gpx.set_name ("GPX track")
		filter_gpx.add_mime_type ("application/gpx+xml")
		filter_gpx.add_pattern ('*.gpx')
		dialog.add_filter (filter_gpx)

		response = dialog.run()
		
		if response == Gtk.ResponseType.OK:
			filepath = dialog.get_filename ()
			dialog.destroy ()

			if self.core.load (filepath):
				self.set_title ('Regatta Simulator - %s' % filepath)
				self.openedFile = filepath
				self.updateTrack ()
				edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Done")
				edialog.format_secondary_text ("File opened, loaded %d waypoints" % len (self.core.getTrack ()))
				edialog.run ()
				edialog.destroy ()	
				self.statusbar.push (self.statusbar.get_context_id ('Info'), 'Loaded %s with %d waypoints' % (filepath, len (self.core.getTrack ())))					
				
			else:
				edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CANCEL, "Error")
				edialog.format_secondary_text ("Cannot open file: %s" % filepath)
				edialog.run ()
				edialog.destroy ()
		else:
			dialog.destroy()


	def updateTrack (self):
		self.trackStore.clear ()
		self.osm.track_remove_all ()
		track = OsmGpsMap.MapTrack ()

		#TODO: make it editable? should swap values between track and core model
		#track.set_property ("editable", True)
		track.set_property ("line-width", 2)

		i = 0
		for wp in self.core.getTrack ():
			i += 1
			self.trackStore.append([i, wp[0], wp[1]])

			p = OsmGpsMap.MapPoint ()
			p.set_degrees (wp[0], wp[1])
			track.add_point (p)
		self.osm.track_add (track)
		

	def onMapClick (self, osm, event):
		lat, lon = self.osm.get_event_location (event).get_degrees ()
		self.waypointLat.set_text (str (lat))
		self.waypointLon.set_text (str (lon))


	def addWaypoint (self, widget):
		lat = self.waypointLat.get_text ()
		lon = self.waypointLon.get_text ()

		if len (lat) > 1 and len (lon) > 1:
			self.core.getTrack ().add (float (lat), float (lon))
			self.updateTrack ()

			self.waypointLat.set_text ('')
			self.waypointLon.set_text ('')


	def onWaypointDown (self, widget):
		selection = self.trackTree.get_selection ()
		model, treeiter = selection.get_selected ()
		
		if treeiter != None:
			self.core.getTrack ().moveDown (int (model[treeiter][0]) - 1)
			self.updateTrack ()

		
	def onWaypointUp (self, widget):
		selection = self.trackTree.get_selection ()
		model, treeiter = selection.get_selected ()
		
		if treeiter != None:
			self.core.getTrack ().moveUp (int (model[treeiter][0]) - 1)
			self.updateTrack ()

		
	def onWaypointRemove (self, widget):
		selection = self.trackTree.get_selection ()
		model, treeiter = selection.get_selected ()
		
		if treeiter != None:
			self.core.getTrack ().remove (int (model[treeiter][0]) - 1)
			self.updateTrack ()


	########### Misc

	def onQuit (self, widget):
		Gtk.main_quit ()


	def dummyClick (self, w):
		pass



	########### GRIB

	def onGribDownloadPercentage (self, percentage):
		self.statusbar.push (self.statusbar.get_context_id ('Info'), 'Downloading grib: %d%% completed' % percentage)

	def onGribDownloadCompleted (self, status):
		if status:
			edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.INFO, Gtk.ButtonsType.OK, "Done")
			edialog.format_secondary_text ("Grib downloaded successfully")
			edialog.run ()
			edialog.destroy ()	
		else:
			edialog = Gtk.MessageDialog (self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error")
			edialog.format_secondary_text ("Error during grib download")
			edialog.run ()
			edialog.destroy ()	


	def onGribSelect (self, widget):
		dialog = GribSelectDialog (self)
		response = dialog.run()

		if response == Gtk.ResponseType.OK:
			selectedGrib = dialog.get_selected_grib ()
			t = Thread(target=self.core.grib.download, args=(selectedGrib, self.onGribDownloadPercentage, self.onGribDownloadCompleted,))
			t.start ()
		elif response == Gtk.ResponseType.CANCEL:
			pass

		dialog.destroy()