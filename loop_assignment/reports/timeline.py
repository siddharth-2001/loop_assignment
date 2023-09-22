from datetime import datetime


class Timeline:

    def __init__(self, start, end) -> None:

        self.start_time = start
        self.end_time = end
        self.event_list = []

    
    def add_event(self, new_event):

        self.event_list.append(new_event)


    def sort_timeline(self):

        self.event_list = sorted(self.event_list, key= lambda x: x.time)



class Event:
    def __init__(self, status, time) -> None:
        self.status = status
        self.time = time