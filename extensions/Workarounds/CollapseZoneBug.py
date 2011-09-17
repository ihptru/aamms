import LadderLogHandlers
import Team

def BasezoneConqueredHandler(team, zonex, zoney, NO_ENEMIES=None):
    if NO_ENEMIES!=None:
        noe=True
    else:
        noe=False
    if noe:
        return
    try:
        Team.teams[team].kill()
    except:
        pass
    
LadderLogHandlers.register_handler("BASEZONE_CONQUERED", BasezoneConqueredHandler)