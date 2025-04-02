from pydantic import BaseModel
from typing import List

# API input classes

class Buzz(BaseModel):
    player: str
    points: int

class Question(BaseModel):
    number: int
    buzzes: List[Buzz] = []

class Scoresheet(BaseModel):
    reader: str | None = None
    roster: List[str]
    results: List[Question]
        
    def to_values_array(self):
        array = [["Question", "Answerer", "Points"]]
        for question in self.results:
            for buzz in question.buzzes:
                if buzz.player == question.buzzes[0].player:
                    array.append([question.number, buzz.player, buzz.points])
                else:
                    array.append(["", buzz.player, buzz.points])
        array.append([])
        if self.reader != None:
            array.append(["Reader", self.reader])
        for player in self.roster:
            if player == self.roster[0]:
                array.append(["Roster", player])
            else:
                array.append(['', player])
        return array
    
def scoresheet_from_values(vals: List[List[str]]):
    roster = []
    results = []
    reader = None
    r = 0
    question = None
    while len(vals[r]) > 0:
        try:
            question = Question(number=int(vals[r][0]))
            results.append(question)
        except:
            pass
        question.buzzes.append(Buzz(player=vals[r][1], points=int(vals[r][2])))
        r += 1
    r += 1
    if vals[r][0] == "Reader":
        reader = vals[r][1]
        r += 1
    while r < len(vals):
        roster.append(vals[r][1])
        r += 1

    return Scoresheet(reader=reader, roster=roster, results=results)

# Analysis classes

class Statline(BaseModel):
    name: str
    played: int = 0
    powers: int = 0
    gets: int = 0
    negs: int = 0
    written: int = 0
    read: int = 0

    def points(self) -> int:
        return 15*self.powers + 10*self.gets + -5*self.negs + min(10*self.written, 200) + min(5*self.read, 100)
    
    def ppg(self) -> float:
        if self.played == 0:
            return 0
        else:
            return (15*self.powers + 10*self.gets + -5*self.negs) / self.played
        
    def add_buzz(self, value: int):
        if value == 10:
            self.gets += 1
        elif value == 15:
            self.powers += 1
        elif value == -5:
            self.negs += 1

    def add_stats(self, stats):
        self.played += stats.played
        self.powers += stats.powers
        self.gets += stats.gets
        self.negs += stats.negs
        self.read += stats.read
        self.written += stats.written

    def to_data_row(self):
        return [self.name, self.played, self.powers, self.gets, self.negs, self.written, self.read, self.ppg(), self.points()]