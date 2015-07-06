#!/usr/bin/env python
import datetime, json, copy
from Pysolar.solar import GetAltitude, GetAzimuth #TODO: potentially inefficent?
from pprint import pprint
#from Pysolar.time import get_delta_t, tt_offset, get_leap_seconds
from math import tan, cos, radians, sqrt

now = datetime.datetime.now()
"""A location has time-specific altitude, azimuth values (degrees) as per Pysolar. Using origin to actuator distances, the various effective actuator heights can be calculated."""
class Location:
	"""Returns a new Location object"""
	def __init__(self, name, lat, lon, time, o_a_dist1, o_a_dist2):
		self.name = name
		self.lat = lat
		self.lon = lon
		self.time = time
		self.o_a_dist1 = o_a_dist1
		self.o_a_dist2 = o_a_dist2

	def incrementTime(self, time, x):
		self.time += datetime.timedelta(minutes = x)

	def resetTime(self, time):
		time = now

	def coords(self):
		return (self.lat, self.lon)

	def alt(self, lat, lon, time):
		a = GetAltitude(lat, lon, time)
		#if a < 0: do something	
		return a

	def azimuth(self, lat, lon, time):
		a = GetAzimuth(lat, lon, time)
		return a

	def calcSunriseTime(self, lat, lon, time):
		a = self.alt(lat, lon, time)
		while a < 0:
			a = self.alt(lat, lon, self.time)
			self.incrementTime(self.time, 1)
		return self.time


	# a = Actuator height #first, panning actuator calculations
	# o = origin
	# H = distance from actuator to the pivot socket = distActuatorToPivot
	#         /|  |
	#        / |  |
	#       /  |  |
	#      /   |  | 
	#    H/    |  a
	#    /     |  | 
	#   /      |  |
	#  /       |  |
	# /S1______|  |
	#O<-pivot bolt
	# ---------<-distActuatorToOrigin

	"""Calculate the most effective height of the first tilting actuator based upon 45 degrees of the panels to the sun. Dist(a, o) is represented by base. Math: tan(S1) = a / distActuatorToOrigin & S1 = 90 - altitude ==> a = tan(90-altitude) * distActuatorToOrigin.  Note: the house is angled at 21 degrees so we must take the tangent of (61-altitude) in actuality...a = tan(61-alt) *distActuatorToOrigin"""
	def calcTiltingHeight(self, o_a_dist1, input_time):
		val = 69 - self.alt(self.lat, self.lon, input_time)
		left = tan(radians(val))
		right = o_a_dist1
		x = left * right
		print "Effective actuator1 height: ", '{:.5f}'.format(x), " inches"
		return x

	"""Return the value calculated via the law of consines, the # of inches the second actuator must be move in order to pan the solar panel according to the azimuth."""
	def calcPanningHeight(self, o_a_dist2, input_time):
		azimuth = self.azimuth(self.lat, self.lon, input_time)
		# if azimuth < 0:
		# 	azimuth = 360 + azimuth #TODO: figure out correct handling
		val = 2*o_a_dist2*o_a_dist2 - (2*o_a_dist2*o_a_dist2*cos((radians(azimuth))))
		x = sqrt(val)
		#print("value to sqrt: ", val)
		print "Effective actuator2 height: ", '{:.5f}'.format(x), " inches"
		return x	

	"""Print the actuator values at hourly increments starting at input time."""
	def simulateDemoDay(self, lat, lon, hours_after_UTC, input_time_zone):
			print "/br", "lat,lon: (", lat, ", ", lon, ")"
			while True:
				if self.alt(lat, lon, self.time) < 0:
					print("ValueError: altitude is below zero.")
					break
				#printing back to the input time (e.g PST)
				print(self.time + datetime.timedelta(hours = hours_after_UTC)).strftime('%H:%M:%S ' + input_time_zone)
				print_alt(self)
				self.calcTiltingHeight(self.o_a_dist1, self.time)
				self.calcPanningHeight(self.o_a_dist2, self.time)

				self.incrementTime(self.time, 60)
				print "/br"
			self.resetTime(now)

"""Print all relevant location data"""
def printLocationInfo(loc):
	print"Location obj. name: ", loc.name
	print_coords(loc)
	print_alt(loc)
	print_azimuth(loc)

def print_coords(loc):
	print "Coords of " + str(loc.name) + ":(", loc.lat, ",", loc.lon, ")"
def print_alt(loc):
	print str(loc.name) + " alt: ", loc.alt(loc.lat, loc.lon, loc.time)
def print_azimuth(loc):
	print str(loc.name) + " azimuth: ", loc.azimuth(loc.lat, loc.lon, loc.time)
def print_actuator1(loc):
	print str(loc.name) + " actuator height: ", loc.calcTiltingHeight(loc.o_a_dist1)
