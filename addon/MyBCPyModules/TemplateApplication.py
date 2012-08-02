#   This file is a BCPy2000 application developer file, 
#	for use with BCPy2000
#	http://bci2000.org/downloads/BCPy2000/BCPy2000.html
# 
#	Author:	Chadwick Boulay
#   chadwick.boulay@gmail.com
#   
#   This program is free software: you can redistribute it
#   and/or modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation, either version 3 of
#   the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import numpy as np
from random import randint, uniform
from math import ceil
import VisionEgg
import SigTools
from AppTools.Displays import fullscreen
from AppTools.StateMonitors import addstatemonitor, addphasemonitor
from AppTools.Shapes import Block
import AppTools.Meters
from MyBCPyModules import MagstimExtension, DigitimerExtension, ERPExtension
import pygame, pygame.locals
import time

class BciApplication(BciGenericApplication):
	
	def Description(self):
		return "Template application"
		
	#############################################################
	def Construct(self):
		#See here for already defined params and states http://bci2000.org/wiki/index.php/Contributions:BCPy2000#CurrentBlock
		params = [
			"PythonApp:Display  int		ScreenId=           -1    -1     %   %  // on which screen should the stimulus window be opened - use -1 for last",
			"PythonApp:Display  float	WindowSize=         0.8   1.0   0.0 1.0 // size of the stimulus window, proportional to the screen",
			]
		params.extend(MagstimExtension.params)
		params.extend(DigitimerExtension.params)
		params.extend(ContingencyExtension.params)
		params.extend(ERPExtension.params)
			
		states = [
			#===================================================================
			# "Intertrial 1 0 0 0",
			# "Baseline 1 0 0 0",
			# "GoCue 1 0 0 0",
			# "Task 1 0 0 0",
			# "Response 1 0 0 0",
			# "StopCue 1 0 0 0",
			#===================================================================
		]
		states.extend(MagstimExtension.states)
		states.extend(DigitimerExtension.states)
		states.extend(ContingencyExtension.states)
		states.extend(ERPExtension.states)
		return params,states
		
	#############################################################
	def Preflight(self, sigprops):
		#Setup screen
		siz = float(self.params['WindowSize'])
		screenid = int(self.params['ScreenId'])  # ScreenId 0 is the first screen, 1 the second, -1 the last
		fullscreen(scale=siz, id=screenid, frameless_window=(siz==1)) # only use a borderless window if the window is set to fill the whole screen
		
		MagstimExtension.preflight(self, sigprops)
		DigitimerExtension.preflight(self, sigprops)
		ContingencyExtension.preflight(self, sigprops)
		ERPExtension.preflight(self, sigprops)
		
	#############################################################
	def Initialize(self, indim, outdim):
		##########
		# SCREEN #
		##########
		self.screen.color = (0,0,0) #let's have a black background
		scrw,scrh = self.screen.size #Get the screen dimensions.
		
		################################
		# State monitors for debugging #
		################################
		if int(self.params['ShowSignalTime']):
			# turn on state monitors iff the packet clock is also turned on
			addstatemonitor(self, 'Running', showtime=True)
			addstatemonitor(self, 'CurrentBlock')
			addstatemonitor(self, 'CurrentTrial')
			addphasemonitor(self, 'phase', showtime=True)

			m = addstatemonitor(self, 'fs_reg')
			m.func = lambda x: '% 6.1fHz' % x._regfs.get('SamplesPerSecond', 0)
			m.pargs = (self,)
			m = addstatemonitor(self, 'fs_avg')
			m.func = lambda x: '% 6.1fHz' % x.estimated.get('SamplesPerSecond',{}).get('global', 0)
			m.pargs = (self,)
			m = addstatemonitor(self, 'fs_run')
			m.func = lambda x: '% 6.1fHz' % x.estimated.get('SamplesPerSecond',{}).get('running', 0)
			m.pargs = (self,)
			m = addstatemonitor(self, 'fr_run')
			m.func = lambda x: '% 6.1fHz' % x.estimated.get('FramesPerSecond',{}).get('running', 0)
			m.pargs = (self,)

		MagstimExtension.initialize(self, indim, outdim)
		DigitimerExtension.initialize(self, indim, outdim)
		ContingencyExtension.initialize(self, indim, outdim)
		ERPExtension.initialize(self, indim, outdim)
		
	#############################################################
	def Halt(self):
		MagstimExtension.halt(self)
		DigitimerExtension.halt(self)
		ContingencyExtension.halt(self)
		ERPExtension.halt(self)
		
	#############################################################
	def StartRun(self):
		MagstimExtension.startrun(self)
		DigitimerExtension.startrun(self)
		ContingencyExtension.startrun(self)
		ERPExtension.startrun(self)
		
	#############################################################
	def StopRun(self):
		MagstimExtension.stoprun(self)
		DigitimerExtension.stoprun(self)
		ContingencyExtension.stoprun(self)
		ERPExtension.stoprun(self)
		
	#############################################################
	def Phases(self):
		# define phase machine using calls to self.phase and self.design
		self.phase(name='intertrial', next='baseline', duration=500)#TODO Replace this duration with some parameter
		self.phase(name='baseline', next='gocue', duration=4000)
		self.phase(name='gocue', next='task', duration=500)
		self.phase(name='task', next='response',\
				duration=None if int(self.params['ContingencyEnable']) or (int(self.params['MSEnable']) and int(self.params['MSReqStimReady'])) else 6000)
		self.phase(name='response', next='stopcue',\
				duration=None if int(self.params['ERPDatabaseEnable']) else 1)
		self.phase(name='stopcue', next='intertrial', duration=500)

		self.design(start='intertrial', new_trial='intertrial')
		
	#############################################################
	def Transition(self, phase):
		# present stimuli and update state variables to record what is going on
		#Update some states
		self.states['Intertrial'] = int(phase in ['intertrial'])
		self.states['Baseline'] = int(phase in ['baseline'])
		self.states['GoCue'] = int(phase in ['gocue'])
		self.states['Task'] = int(phase in ['task'])
		self.states['Response']  = int(phase in ['response'])
		self.states['StopCue']  = int(phase in ['stopcue'])
		
		if phase == 'intertrial':
			pass
			
		elif phase == 'baseline':
			pass
		
		elif phase == 'gocue':
			pass
			
		elif phase == 'task':
			pass
			
		elif phase == 'response':
			pass
		
		elif phase == 'stopcue':
			pass
		
		MagstimExtension.transition(self, phase)
		DigitimerExtension.transition(self, phase)
		ContingencyExtension.transition(self, phase)
		ERPExtension.transition(self, phase)
					
	#############################################################
	def Process(self, sig):
		#Process is called on every packet
		#Phase transitions occur independently of packets
		#Therefore it is not desirable to use phases for application logic in Process
		MagstimExtension.process(self, sig)
		DigitimerExtension.process(self, sig)
		ContingencyExtension.process(self, sig)
		ERPExtension.process(self, sig)
		
		#If we are in Task, and we are using ContingencyExtension or MagstimExtension
		if self.in_phase('task') and (int(self.params['ContingencyEnable']) or int(self.params['MSEnable'])):
			contingency_met = self.contingency_met if int(self.params['ContingencyEnable']) else True
			stim_ready = self.stim_ready if int(self.params['MSEnable']) else True
			if contingency_met and stim_ready: self.change_phase('response')
			
		#If we are in Response and we are using ERPExtension
		if self.in_phase('response') and int(self.params['ERPDatabaseEnable']):
			if erp_collected: self.change_phase('stopcue')
	
	#############################################################
	def Frame(self, phase):
		# update stimulus parameters if they need to be animated on a frame-by-frame basis
		pass
	
	#############################################################
	def Event(self, phase, event):
		MagstimExtension.event(self, phase, event)
		DigitimerExtension.event(self, phase, event)
		ContingencyExtension.event(self, phase, event)
		ERPExtension.event(self, phase, event)
		
#################################################################
#################################################################