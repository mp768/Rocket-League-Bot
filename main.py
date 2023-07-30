# This file is for strategy

from util.objects import *
from util.routines import *
from util.tools import find_hits

import time

class Bot(GoslingAgent):
    debug_text = ''
    timer = 0
    current_time = 0
    last_time = 0
    went_to_goal = False
    
    def debug_print(self):
        white = self.renderer.white()
        self.renderer.draw_string_2d(10, 150, 3, 3, self.debug_text, white)
    
    def run(self):
        self.last_time = self.current_time
        self.current_time = time.time()
        
        delta_time = self.current_time - self.last_time
        
        self.timer += 10 * delta_time
        
        if self.intent is not None:
            if type(self.intent) == goto_boost and self.timer > 75:
                self.set_intent(goto(self.ball.location))
                self.timer = 0
            
            return
        
        if self.kickoff_flag:
            self.set_intent(kickoff())
            return

        if self.is_in_front_of_ball():
            # self.set_intent(short_shot(self.foe_goal.location))
            self.set_intent(jump_shot(self.ball.location, self.time, (self.ball.location - self.foe_goal.location).normalize(), self.me.orientation.forward.normalize()))
            return
        
        if (self.foe_goal.location - self.ball.location).magnitude() < 1000:
            self.set_intent(goto(self.ball.location))
            return
        
        if (self.friend_goal.location - self.me.location).magnitude() < 500 and self.went_to_goal:
            self.set_intent(goto(self.ball.location))
            return
        
        if (self.friend_goal.location - self.ball.location).magnitude() < 1000 and not self.went_to_goal:
            self.set_intent(goto(self.friend_goal.location))
            self.went_to_goal = True
            return
        
        foe = self.get_closest_foe()
        
        if self.me.boost > 50 and foe is not None:
            self.set_intent(ram_with_boost(foe))
            print("Found a foe to ram ", foe)
            print(self.foes)
            self.went_to_goal = False
            return
        
        if foe is not None and (foe.location - self.foe_goal.location).magnitude() > 100:
            # self.set_intent(jump_shot(self.ball.location, 1, (self.foe_goal.location - self.ball.location).normalize(), self.me.orientation.forward.normalize()))
            self.set_intent(short_shot(self.foe_goal.location))
            return
        
        if not (self.me.boost > 95):
            closest_boost = self.get_closest_boost(True)
            closest_boost_any = self.get_closest_boost(False)
            
            if closest_boost is not None and (closest_boost.location - self.me.location).magnitude() < 1000:
                self.set_intent(goto_boost(closest_boost))
                return
            elif closest_boost_any is not None:
                self.set_intent(goto_boost(closest_boost_any))
                return

        if self.me.boost > 65:
            # self.set_intent(jump_shot(self.ball.location, 1, (self.foe_goal.location - self.ball.location).normalize(), self.me.orientation.forward.normalize()))
            self.set_intent(short_shot(self.foe_goal.location))
            return
        
        self.set_intent(jump_shot(self.ball.location, self.time, (self.ball.location - self.foe_goal.location).normalize(), self.me.orientation.forward.normalize()))
        
        
    
    # This function runs every in-game tick (every time the game updates anything)
    # def run(self):
    #     self.debug_print()
        
    #     self.last_time = self.current_time
    #     self.current_time = time.time()
        
    #     delta_time = self.current_time - self.last_time
        
    #     self.timer += 10 * delta_time
        
    #     if self.get_intent() is not None:
    #         if type(self.intent) == goto_boost and self.timer > 100:
    #             self.set_intent(goto(self.ball.location))
    #             self.timer = 0
            
    #         self.debug_intent()
    #         return
        
    #     # set_intent tells the bot what it's trying to do
    #     if self.kickoff_flag:
    #         self.set_intent(kickoff())
    #         return
    
    #     if self.is_in_front_of_ball():
    #         self.set_intent(short_shot(self.foe_goal.location))
    #         self.debug_text = "Retreating"
    #         return
        
    #     if self.me.boost > 95:
    #         foe = self.get_closest_foe()
    #         if foe is not None:
    #             self.set_intent(ram_with_boost(foe))
    #         return
        
    #     if self.me.boost > 75:
    #         self.set_intent(short_shot(self.foe_goal.location))
    #         self.debug_text = "Shooting the ball"
    #         return
        
    #     if (self.friend_goal.location - self.ball.location).magnitude() < 800:
    #         self.set_intent(goto(self.friend_goal.location))
    #         return
        
    #     if (self.me.location - self.ball.location).magnitude() < 1000:
    #         self.set_intent(short_shot(self.foe_goal.location))
    #         # self.set_intent(short_shot(self.foe_goal.location))
    #         return
        
    #     if self.me.boost > 5:
    #         self.set_intent(goto(self.ball.location))
    #         closest_boost = self.get_closest_boost(True)
            
    #         if closest_boost is not None:
    #             self.set_intent(goto_boost(closest_boost))
            
    #         self.debug_text = "Getting boost"
    #         return
        
    #     closest_boost = self.get_closest_boost(True)
        
    #     if closest_boost is not None:
    #         self.set_intent(goto_boost(closest_boost))
    #         self.debug_text = "Getting boost"
    #         return
        
    #     self.set_intent(recovery())
    
    def is_in_front_of_ball(self):
        me_to_goal = (self.me.location - self.foe_goal.location).magnitude()
        ball_to_goal = (self.ball.location - self.foe_goal.location).magnitude()
        
        return me_to_goal < ball_to_goal + 100
    
    def get_closest_foe(self):
        closest_foe = None
        closest_distance = 100000
        
        for foe in self.foes:
            distance = (self.me.location - foe.location).magnitude()
            
            if closest_foe is None or distance < closest_distance:
                closest_foe = foe
                closest_distance = distance
        
        return closest_foe
    
    def get_closest_boost(self, large = False):
        avalible_boosts = [boost for boost in self.boosts if boost.active and (True if not large else boost.large)]
        
        closest_boost = None
        closest_distance = 100000
        
        for boost in avalible_boosts:
            distance = (self.me.location - boost.location).magnitude()
            
            if closest_boost is None or distance < closest_distance:
                closest_boost = boost
                closest_distance = distance
        
        return closest_boost
        
        
            
        
        