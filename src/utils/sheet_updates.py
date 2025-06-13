"""
Defines several methods that return JSON for batch updates to a spreadsheet.
"""
from typing import List
from utils.types import Statline, Scoresheet

def add_sheet(title: str):
    """
    Returns batchUpdate json for adding a sheet with the given title to a spreadsheet.
    """
    request = {
        "addSheet": {
            "properties": {
                "title": title
            }
        }
    }
    return request

def write_scoresheet_json(writer: str, results: Scoresheet):
    """
    Returns batchUpdate json for adding values across a certain range to a scoresheet
    """
    range = f'{writer}!A:C'
    values = results.to_values_array()
    data = {
        "range": range,
        "values": values
    }
    return data

def write_stats_json(writers: list, stats_data: List[List[Statline]]):
    """
    Parses statline data for a list of stat sheets and returns a list of value entry objects
    """
    writers.insert(0, "Overall")
    data = []
    for i in range(len(writers)):
        statsheet = [['Player', 'Questions', '15', '10', '-5', 'W', 'R', 'PPG', 'Points']]
        for statline in stats_data[i]:
            statsheet.append(statline.to_data_row())
        data.append({
            "range": f'{writers[i]}!A:I',
            "values": statsheet
        })
    return data


def get_scoresheet_values(name: str):
    """
    Returns a range for retrieving scoresheet data for one packet.
    """
    return f'{name}!A2:C'
