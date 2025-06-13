"""
Analysis functions for reading scoresheets and combining stats
"""

from typing import List, Dict
from utils.types import Scoresheet, Statline, scoresheet_from_values

def parse_scoresheet(writer: str, scores: Scoresheet, writer_stats: Dict[str, Statline]):
    """
    Parses a scoresheet object into a dictionary of player statlines for the packet.
    """
    for name in scores.roster:
        writer_stats[name] = Statline(name=name)
        writer_stats[name].played += len(scores.results)
    for question in scores.results:
        for buzz in question.buzzes:
            writer_stats[buzz.player].add_buzz(buzz.points)

    if scores.reader != None:
        writer_stats[scores.reader] = Statline(name=scores.reader)
        writer_stats[scores.reader].read += len(scores.results)

    if writer not in writer_stats:
        writer_stats[writer] = Statline(name=writer)
        writer_stats[writer].written = len(scores.results)

def merge_stats(stats_list: List[Dict[str, Statline]]):

    overall_stats = dict()
    for statsheet in stats_list:
        for player in statsheet:
            if player not in overall_stats:
                overall_stats[player] = Statline(name=player)
            overall_stats[player].add_stats(statsheet[player])
    
    return overall_stats

def scoresheet_anal(writers: list, scoresheets_list: list, rooms=1):
    """
    Takes a list of writers and list of scoresheets in nested array form from sheets API return and 
    parses them into a list of player stats dictionaries for each packet. Returns a list of sorted lists
    of player statlines.
    - Each scoresheet array is read into a Scoresheet object before individual parsing
    - If rooms is greater than 1, this will combine the stats for the same packet read in multiple rooms. 
    """
    def points_key(s: Statline):
        return s.points()

    writer_stats_list = []
    for i in range(len(writers)):
        writer_stats = dict()
        for j in range(rooms):
            scoresheet = scoresheet_from_values(scoresheets_list[j][i])
            parse_scoresheet(writers[i], scoresheet, writer_stats)
        writer_stats_list.append(writer_stats)

    overall = merge_stats(writer_stats_list)

    full_stats = [sorted([overall[player] for player in overall], reverse=True, key=points_key)]
    for statsheet in writer_stats_list:
        full_stats.append(sorted([statsheet[player] for player in statsheet], reverse=True, key=points_key))

    return full_stats
