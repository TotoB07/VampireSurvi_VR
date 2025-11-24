from Monster import Monster
import random

class GameManagement():
    def __init__(self, game):
        #partie
        self.game = game
        self.difficulte = 0
        self.score = 0
        self.vague = 0
        self.enemyVague = 10
        self.initialEnemyVague = 10
        self.maxMonsters = 5
        self.timeNextMonster = self.game.gametime

    def NewVague(self):
        self.vague += 1
        self.timeNextMonster = 10
        self.enemyVague = int(1.5 * (self.initialEnemyVague + self.difficulte) + self.vague * 10)
        self.initialEnemyVague = self.enemyVague
        self.maxMonsters = int(self.enemyVague //2 + (self.difficulte * 5))
        print(self.enemyVague, self.maxMonsters)
    
    def spawn_monster(self):
        return Monster(self.game, [random.randint(0,self.game.terrain.terrain_width),random.randint(0,self.game.terrain.terrain_length),100], 100, 2, 10, 2, 50)
    
    def update(self, dt):
        self.timeNextMonster -= dt
        if self.enemyVague == 0 and len(self.game.monsters) == 0:
            print("newvague")
            self.NewVague()
        if self.timeNextMonster <= 0 and self.enemyVague > 0 and len(self.game.monsters) < self.maxMonsters:
            self.game.monsters.append(self.spawn_monster())
            self.enemyVague -= 1
            if self.enemyVague != 0:
                self.timeNextMonster = 3*random.random()



        
