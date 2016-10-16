# EMACS settings: -*-	tab-width: 2; indent-tabs-mode: t; python-indent-offset: 2 -*-
# vim: tabstop=2:shiftwidth=2:noexpandtab
# kate: tab-width 2; replace-tabs off; indent-width 2;
# ==============================================================================
# Authors:            Patrick Lehmann
#
# Python functions:   A streaming VHDL parser
#
# Description:
# ------------------------------------
#		TODO:
#
# License:
# ==============================================================================
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
#
from pyVHDLParser.SimulationModel.EventSystem import ProjectedWaveform, Waveform


class Simulation:
	def __init__(self):
		self._signals =         []
		self._processes =       []
	
	def AddSignal(self, signal):
		self._signals.append(signal)
	
	def AddProcess(self, process):
		self._processes.append(process)

	def Initialize(self):
		for signal in self._signals:
			signal.Initialize()
	
	def Run(self):
		pass
		
	def ExportVCD(self, filename):
		pass


class Path:
	def __init__(self, path):
		self._path =              path


class Signal:
	def __init__(self, path, subType, initializer=None):
		self._path =              path
		self._subType =           subType
		self._initializer =       initializer
		self._drivingValue =      None
		self._projectedWaveform = ProjectedWaveform(self)
		self._waveform =          Waveform(self)
	
	def Initialize(self):
		if (self._initializer is not None):
			result = self._initializer()
		else:
			result = self._subType.Attributes.Low()
		self._waveform.Initialize(result)

class Process:
	def __init__(self, path, sensitivityList=None):
		self._path =            path
		self._sensitivityList = sensitivityList
		self._constants =       []
		self._variables =       []
		self._outputs =         []
		self._instructions =    []


class Source:
	pass


class Driver(Source):
	pass


class ResolutionFunction:
	def __init__(self):
		self._function =  None


class DrivingValue:
	pass
