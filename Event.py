#!/usr/bin/python3
## @file Event.py
 # @package Event
 # @brief Functions and classes for events
 # @details This file contains functions and classes that are used for events. 
 #          %Events are actions that can be triggered. 

import logging
import logging.handlers

## @cond
logging.getLogger("EventModule").addHandler(logging.NullHandler())
log=logging.getLogger("EventModule")
## @endcond

## @class Event.Action
 # @brief Represents an action
 # @details An Action object represents an action. It's callable and the function can have
 #          constant parameters. 
class Action: 
	## @property __function
	 # @brief The function to call.
	 # @details The function which to call when the action is executed.
	 # @private
	
	## @property __args
	 # @brief The arguments of the function.
	 # @details List of arguments to pass to the function when it is called.
	 # @private

	## @property name
	 # @brief The name of the action.
	 # @details The name of the action. It's used for logging messages.
	 
	## @cond
	__slots__ = ("name", "__function","__args")
	## @endcond

	## @brief Init function
	 # @details Inits a new Action and its properties.
	 # @param name The name of the action
	 # @param function The function to call when the action is executed.
	 # @param args List of arguments to pass to the function
	def __init__(self, name, function, *args):
		self.name=name
		self.__function=function
		self.__args=args

	## @brief Executes the action
	 # @details This function calls __function with the arguments __args
	def __call__(self,*args):
		args=args+self.__args
		self.__function(*args)

	## @brief Sets the action function
	 # @details This function sets the function to execute when the action is executed
	 # @param function The function to call when the action is executed.
	 # @exception TypeError Raised when function isn't callable 
	def setFunction(self,function):
		if not hasattr(function,"__call__"):
			raise(TypeError("Function must be callable") )
		self.__function=function
	
	## @brief Sets the args of the function.
	 # @details Sets the args of the function which to call when the action is executed.
	 # @param args The arguments for the call of the function when the action is executed.
	def setArgs(self,*args):
		self.__args=args

## @class Event.Event
 # @brief An simple event class
 # @details This class is used for an simple event. It can be named and triggered. 
class Event:  
	## @property __actions
	 # @private 
	 # @brief List of actions
	 # @details List of actions that are excecuted when the event is triggered.
	 #          An action is an object of the class Action.

	## @property __enabled
	 # @private
	 # @brief If the event enabled?
	 # @details If False no actions are executed when the event is triggered.

	## @property name
	 # @public
	 # @brief Name of the event.
	 # @details The name of the event.
	
	## @cond 
	__slots__=("__actions","__enabled","name")
	## @endcond
	
	## @brief Init function.
	 # @details Inits a new Event and adds the properties.
	 # @param name The event name
	 # @param action Actions
	def __init__(self, name, action=list() ):
		#Add properties
		self.__actions=list()
		for a in action:
			self.addAction(a)
		self.__enabled=True
		self.name=name

	## @brief Is the event enabled?
	 # @details Returns True if the event is enabled, otherwise False.
	 #          If the event is disables, no actions are executed.
	 # @public
	def isEnabled(self):
		return self.__enabled

	## @brief Enables the event.
	 # @details This function enables the event. If the event is enabled, 
	 #          actions are executed when it's triggered.
	 # @public
	def enable(self):
		log.debug("Event „" + self.name + "“ enabled.")
		self.__enabled=True
	
	## @brief Disables the event.
	 # @details This function disbales the event. If the event is disabled,
	 #          no actions are executed when it's triggered.
	def disable(self):
		log.debug("Event „" + self.name +"“ disabled.")
		self.__enabled=False
	
	## @brief Adds an action to the event.
	 # @details Adds the given action to the event. %Actions are executed 
	 #          when the event is triggered.
	 # @param action The action to add. The action could be an Action object or 
	 #               any other callable object.
	 # @exception TypeError Raised with e when no callable object is given.
	 # @exception RuntimeError Raised when the action already exists.
	def addAction(self, action): 
		if not hasattr(action,"__call__"):
			raise TypeError("Action must be callable")
		if action in self.__actions:
			raise RuntimeError("Action „" + action.name+"“ already exists.")
		else:
			self.__actions.append(action)

	## @brief Removes an action from the event.
	 # @details Removes the given action from the event. %Actions are executed
	 #          when the event is triggered.
	 # @param action The action to remove. The action could be an Action object 
	 #               or any other callable object.
	 # @exception TypeError Raised when no callable object is given.
	 # @exception RuntimeError Raised when the action doesn't exist.
	def removeAction(self, action):
		if not hasattr(action,"__call__"):
			raise TypeError("Action must be callable.")
		if action not in self.__actions:
			raise RuntimeError("Action “" + action.name +"“ doesn't exist.")
		self.__actions.remove(action)
	
	## @brief Triggers the event.
	 # @details This function executes all actions registered with the event 
	 #          if it is enabled.
	 # @param args The args to pass to the trigger
	def trigger(self,*args):
		if self.__enabled==False:
			return None
		for action in self.__actions:
			action(*args)
		log.debug("Event „" + self.name + "“ triggered.")
	
	## @brief Removes all actions from the event
	 # @details This function removes all action from the event
	def cleanActions(self):
		self.__actions=list()
	
## @class Event.EventGroup
 # @brief Class for a group of events.
 # @details Class for a group of events for better management of events.
class EventGroup:
	## @property __events
	 # @brief \link Event Events\endlink assigned with this group.
	 # @details Dictionary of all \link Event Events\endlink assigned to 
	 #          this group, where the key is the name of the event.
	 # @private
	
	## @property __enabled
	 # @brief Are events of this group enabled?
	 # @details If not True, no actions are executed when an event is triggered.
	 # @private

	## @property name
	 # @brief name of the group
	 # @details The name of the group.

	## @cond
	__slots__=("name","__enabled","__events")
	## @endcond

	## @brief Init function
	 # @details Inits a new EventGroup and adds the properties.
	 # @param name The name of the group.
	 # @param enabled Is the group enabled? If not True, no actions are executed when an
	 #                event is triggered.
	 # @param events The events assigned with the group.
	def __init__(self, name,enabled=True,events=dict() ):
		self.__events=dict()
		for e in events:
			self.addEvent(e)
		self.name=name
		self.__enabled=enabled

	## @brief Adds an event to the group.
	 # @details This function adds the given event to the group and enables it. 
	 # @param events One or more events to add
	 # @exception TypeError Raised if event isn't an instance of Event.
	 # @exception RuntimeError Raised when the event already exists.
	def addEvent(self,*events):
		for event in events:
			if not isinstance(event, Event):
				raise(TypeError("Parameter 1 must be an instance of Event.") )
			if event.name in self.__events:
				raise RuntimeError("Event „" + event.name + "“ already exists.")
			event.enable()
			self.__events[event.name]=event

	## @brief Removes an event from the group.
	 # @details This function removes the given event from the group.
	 # @param eventname The name of the event.
	 # @exception RuntimeError Raised if the event doesn't exist.
	def removeEvent(self, eventname):
		if eventname not in self.__events:
			raise RuntimeError("Event „" + eventname + "“ doesn't exist.")
		del self.__events[eventname]
	
	## @brief Triggers an event in the group
	 # @details This function triggers the given event.
	 # @param name The name of the event to triggers
	 # @param args The arguments to pass to the actions
	 # @exception RuntimeError Raised when the event doesn't exist.
	def triggerEvent(self, name,*args):
		if name not in self.__events:
			raise RuntimeError("Event „" + name +"“ doesn't exist")
		if not self.__enabled:
			return
		self.__events[name].trigger(*args)
	
	## @brief Disables the group
	 # @details Disables the event group. If the event group is disables, no events 
	 #          are triggered.
	def disable(self):
		log.debug("Event group „" + self.name + "“ disabled.")  
		self.__enabled=False
	
	## @brief Enables the group
	 # @details Enables the group. %Events are only triggered when the group is enabled.
	def enable(self):
		log.debug("Event group „" + self.name + "“ enabled.")
		self.__enabled=True

	## @brief Returns an event
	 # @details Returns a reference to an event. 
	 # @param name The name of the event to return
	 # @exception RuntimeError Raised if the event doesn't exist.
	 # @return A reference to the event.
	def getEvent(self, name):
		if name not in self.__events:
			raise RuntimeError("Event „" + name +"“ doesn't exist.")
		return self.__events[name]
	
## @brief Enables Logging
 # @details This function enables logging for all Event classes. For more information see
 #          the logging module.
 # @param h The handler used for logging
 # @param f The formatter used for logging
 # @param level The logging level 
def enableLogging(level=logging.DEBUG, h=None,f=None):
	logging.getLogger("EventModule").setLevel(level)
	if not h:
		h=logging.StreamHandler()
		h.setLevel(level)
	if not f: 
		f=logging.Formatter("[%(name)s] (%(asctime)s) %(levelname)s: %(message)s")
	h.setFormatter(f)
	logging.getLogger("EventModule").addHandler(h)

## @brief Saves the result of the tests
tests=list()
## @brief runs tests

def __runTest(param=None,i=None):
	if param:
		if i==None:
			tests.append(param)
		else:
			tests[i]=param
		return
	print("Running tests ... ")
	enableLogging()
	g=EventGroup("My event group")
	f=__runTest
	a=Action("Test action",f, True)
	e=Event("My event")
	e.addAction(a)
	g.addEvent(e)
	g.triggerEvent(e.name)
	tests.append(True)
	b=Action("Test action 2",f, False,len(tests)-1)
	g.getEvent(e.name).disable()
	g.getEvent(e.name).removeAction(a)
	g.getEvent(e.name).addAction(b)
	g.triggerEvent(e.name)
	#print results
	print("TEST RESULTS --------------------------------")
	i=1
	for test in tests:
		state="failed"
		if test==True:
			state="succeed"
		print("Test " + str(i) + " " + state)
		i=i+1
	

if __name__=='__main__':
	__runTest()
