from actions.sheets import create_spreadsheet, spreadsheet_batch_update, get_sheet_names
from utils.sheet_updates import add_sheet

class Registry:
    def __init__(self):
        self._rooms = 0
        self._scoresheets = []
        self._statsheets = []
        self._combined = None

    def add_room(self, score_id: str | None):
        self. _rooms += 1
        if score_id == None:
            self._scoresheets.append(create_spreadsheet(f'SCORESHEET_{self._rooms}'))
        else:
            self._scoresheets.append(score_id)
        self._statsheets.append(create_spreadsheet(f'STATS_{self._rooms}'))
        spreadsheet_batch_update(self._statsheets[-1], [add_sheet("Overall")])
        get_sheet_names(self._statsheets[-1])

    def rooms(self):
        return self._rooms

    def scoresheet_id(self, room: int):
        return self._scoresheets[room-1]
    
    def statsheet_id(self, room: int):
        return self._statsheets[room-1]

    def combined(self):
        if not self._combined:
            self._combined = create_spreadsheet('COMBINED')
            spreadsheet_batch_update(self._combined, [add_sheet("Overall")])
            get_sheet_names(self._combined)
        return self._combined