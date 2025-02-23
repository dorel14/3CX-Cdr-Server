
from pathlib import Path
from typing import Any, Callable, Optional

from nicegui.element import Element
from nicegui.events import handle_event


class FullCalendar(Element, component='fullcalendar.js'):

    def __init__(self, options: dict[str, Any],
                on_eventClick: Optional[Callable] = None,
                on_dateClick:Optional[Callable] = None) -> None:
        """FullCalendar

        An element that integrates the FullCalendar library (https://fullcalendar.io/) to create an interactive calendar display.

        :param options: dictionary of FullCalendar properties for customization, such as "initialView", "slotMinTime", "slotMaxTime", "allDaySlot", "timeZone", "height", and "events".
        :param on_click: callback that is called when a calendar event is clicked.
        """
        super().__init__()
        self.add_resource(Path(__file__).parent / 'lib')
        self._props['options'] = options

        if on_eventClick:
            self.on('eventClick', lambda e: handle_event(on_eventClick, e))
        if on_dateClick:
            self.on('dateClick', lambda e: handle_event(on_dateClick, e))

    def add_event(self, title: str, start: str, end: str, **kwargs) -> None:
        """Add an event to the calendar.

        :param title: title of the event
        :param start: start time of the event
        :param end: end time of the event
        """
        event_dict = {'title': title, 'start': start, 'end': end, **kwargs}
        self._props['options']['events'].append(event_dict)
        self.update()
        self.run_method('update_calendar')

    def remove_event(self, title: str, start: str, end: str) -> None:
        """Remove an event from the calendar.

        :param title: title of the event
        :param start: start time of the event
        :param end: end time of the event
        """
        for event in self._props['options']['events']:
            if event['title'] == title and event['start'] == start and event['end'] == end:
                self._props['options']['events'].remove(event)
                break

        self.update()
        self.run_method('update_calendar')

    @property
    def events(self) -> list[dict[str, Any]]:
        """List of events to display on the calendar."""
        return self._props['options'].get('events', [])
