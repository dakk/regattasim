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

import math
import logging

from . import utils
from .boat import Boat
from .track import Track
from .routers import linearbestisorouter, RoutingResult

logger = logging.getLogger ('gweatherrouting')

def listRoutingAlgorithms():
	return [
		{
			'name': 'LinearBestIsoRouter',
			'class': linearbestisorouter.LinearBestIsoRouter
		}
	]

class Routing:
	def __init__ (self, algorithm, boat, track, grib, startDatetime, startPosition):
		self.end = False
		self.algorithm = algorithm
		self.boat = boat
		self.track = track
		self.steps = 0
		self.path = []
		self.time = startDatetime
		self.grib = grib
		self.log = []           # Log of each simulation step
		if startPosition:
			self.wp = 0
			self.position = startPosition
		else:
			self.wp = 1
			self.position = self.track[0]
		logger.debug ('initialized (time: %s)' % (self.time))


	def toTrack(self):
		pass

	def step (self):
		self.steps += 1
		#self.t += 0.1

		if self.wp >= len (self.track):
			self.end = True
			return self.log[-1]

		# Next waypoint
		nextwp = self.track[self.wp]

		if len (self.log) > 0:
			res = self.algorithm.route (self.log[-1], self.time, self.position, nextwp)
		else:
			res = self.algorithm.route (None, self.time, self.position, nextwp)


		#self.time += 0.2
		progress = len (self.log) * 5
		logger.debug ('step (time: %s, %f%% completed): %f %f' % (self.time, progress, self.position[0], self.position[1]))

		if len (res.path) != 0:
			self.position = res.position
			self.path = self.path + res.path
			self.wp += 1
			res.isochrones = []

		np = []
		ptime = None 
		for x in self.path:
			if len(x) > 3: nt = x[4]
			else: nt = x[2]

			if ptime:
				if ptime < nt:
					np.append(x)
					ptime = nt
			else:
				np.append(x)
				ptime = nt

		self.path = np
		self.time = res.time
		nlog = RoutingResult(progress=progress, time=res.time, path=self.path, isochrones=res.isochrones)

		self.log.append (nlog)
		return nlog
		