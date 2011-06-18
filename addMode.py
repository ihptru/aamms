#!/usr/bin/env python3
## @file addMode.py
 # @brief Script for adding a mode.
 # @brief Call this script to add a mode.

import Mode
import Zone

print("This script helps you with adding a new mode.")
print("-"*20 + " Main settings " + "-"*20)
mname=input("Full name of the mode: ")
smname=input("Short name of the mode: ")
max_teams=None
max_team_members=None
zone_num=None
res_num=None
while max_teams==None or max_team_members==None or zone_num==None or res_num==None:
	try:
		if max_teams==None:
			max_teams=input("Maximal teams [0 for unlimited]: ")
			if max_teams.strip()=="":
				max_teams=0
			else:
				max_teams=int(max_teams)
		if max_team_members == None:
			max_team_members=input("Maximal members per team [0 for unlimited]: ")
			if max_team_members.strip()=="":
				max_team_members=0
			else:
				max_team_members=int(max_team_members)
		if zone_num==None:
			zone_num=int(input("Number of zones: ") )
		if res_num==None:
			res_num=int(input("Number of respoints: ") )
	except ValueError:
		print("Not a valid number!")
settings_file=input("Settings file [The file which to include when the mode gets activated]: ") 
Mode.Add(mname)
m=Mode.modes[mname.replace(" ","_").lower()]
m.short_name=smname
m.max_teams=max_teams
m.max_team_members=max_team_members
print("-"*20 + " Zone settings " + "-"*20)
for i in range(zone_num):
	print("Zone "+str(i+1),"-----------------------")
	name=input("Name of the zone [You can leave it empty, default is Zone"+str(i+1)+"]: ")
	if name.strip=="":
		name="Zone"+str(i+1)
	x,y=input("Position [x|y]: ").split("|")
	x,y=(int(x),int(y))
	s=int(input("Zone size: ") )
	g=int(input("Zone growth: ") )
	t=input("Zone type [on of: "+", ".join(Zone._ZONE_TYPES)+"]: ")
	direction=input("Zone direction [xdir|ydir] [leave empty if you don't know]: ")
	if direction.strip()=="":
		direction=0,0
	else:
		direction=direction.split("|")
	team=int(input("Number of the team for which the zone is spawned\n[0: the zone should be spawned once per team\n -1: if the zone should only be spawned once without a team assigned.]: "))
	color=0,0,0
	if team == 0:
		team=None
	if team == -1:
		r,g,b=input("Zone color [r;g;b]: ").split(";")
		color=int(r), int(b), int(g)
	
	settings=""
	if t=="teleport":
		print("Extra settings for teleport zones")
		print("Attention: There is no type checking here. Enter correct values!")
		settings=" ".join(settings+input("Destination for the player [x|y]: ").split("|") )
		settings=settings+" "+input("Rel, abs or cycle: ")
		settings=settings+" "+" ".join(input("Direction of the player [xdir|ydir]: ").split("|") )
		settings=settings+" 1"
	elif t=="rubber":
		print("Extra settings for rubber zones")
		settings=input("Rubber: ")
	z=Zone.Zone(name, (x,y), s, g, direction, color=color, type=t)
	z.settings=settings
	m.addZone(team, z)
print("-"*20 + " Respoints settings " + "-"*16)
for i in range(res_num):
	print("Settings for respoint",i+1)
	direction, pos, team=None, None, None
	while(None in [direction, pos, team]):
		try:
			if pos == None:
				x,y=input("Position [x|y]: ").split("|")
				pos=int(x), int(y)
				if len(pos)!=2:
					raise ValueError()
			if direction == None:
				xdir, ydir=input("Initial drive direction [xdir|ydir]: ").split("|")
				direction=int(xdir), int(ydir)
				if len(direction)!=2:
					raise ValueError()
			if team==None:
				team=input("Number of team for which the should be used [leave empty if for all teams]: ")
				if team.strip()=="":
					team=-1
				team=int(team)-1
		except ValueError:
			print("Invalid value entered!")
			continue
		m.addRespoint(pos[0],pos[1],direction[0], direction[1], team)
Mode.modes[m.getEscapedName() ]=m
Mode.saveModes()
