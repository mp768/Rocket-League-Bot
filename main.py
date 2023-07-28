# This file is for strategy

from util.objects import *
from util.routines import *
from util.tools import find_hits


class Bot(GoslingAgent):
    debug_text = ''
    
    def debug_print(self):
        white = self.renderer.white()
        self.renderer.draw_string_2d(10, 150, 3, 3, self.debug_text, white)
    
    # This function runs every in-game tick (every time the game updates anything)
    def run(self):
        self.debug_print()
        
        if self.get_intent() is not None:
            self.debug_intent()
            return
        
        # set_intent tells the bot what it's trying to do
        if self.kickoff_flag:
            self.set_intent(kickoff())
            return
    
        if self.is_in_front_of_ball():
            self.set_intent(goto(self.friend_goal.location))
            self.debug_text = "Retreating"
            return
        
        if self.me.boost == 100:
            self.set_intent(short_shot(self.foe_goal.location))
            self.debug_text = "Shooting the ball"
            return
        
        closest_boost = self.get_closest_boost()
        
        if closest_boost is not None:
            self.set_intent(goto(closest_boost.location))
            self.debug_text = "Getting boost"
            return
    
    def is_in_front_of_ball(self):
        me_to_goal = (self.me.location - self.foe_goal.location).magnitude()
        ball_to_goal = (self.ball.location - self.foe_goal.location).magnitude()
        
        return me_to_goal < ball_to_goal + 1000
        
    
    def get_closest_boost(self):
        avalible_boosts = [boost for boost in self.boosts if boost.large and boost.active]
        
        closest_boost = None
        closest_distance = 100000
        
        for boost in avalible_boosts:
            distance = (self.me.location - boost.location).magnitude()
            
            if closest_boost is None or distance < closest_distance:
                closest_boost = boost
                closest_distance = distance
        
        return closest_boost
        
        
            
        
        