from __future__ import annotations
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.control
import ifcopenshell.api.resource
import ifcopenshell.api.sequence
import ifcopenshell.util.date
from datetime import datetime, timedelta, date
from typing import Union, Any, TypedDict
from typing_extensions import NotRequired


class WorkSlot(TypedDict):
    DayOfWeek: str
    WorkTimes: list[dict[str, Any]]
    ifc: Union[ifcopenshell.entity_instance, None]


class ExceptionDict(TypedDict):
    WorkTime: list[int]
    FullDay: list[int]


ExceptionsDict = dict[int, dict[int, ExceptionDict]]


class Calendar(TypedDict):
    Name: str
    Type: str
    HoursPerDay: int
    StandardWorkWeek: list[WorkSlot]
    HolidayOrExceptions: NotRequired[ExceptionsDict]
    ifc: NotRequired[ifcopenshell.entity_instance]


class Activity(TypedDict):
    Name: str
    Identification: int
    StartDate: datetime
    FinishDate: datetime
    PlannedDuration: float
    Status: str
    CalendarObjectId: str
    ifc: Union[ifcopenshell.entity_instance, None]


class WBSEntry(TypedDict):
    """Work Breakdown Strcture Entry"""

    Name: str
    Code: int
    ParentObjectId: Union[int, None]
    ifc: Union[ifcopenshell.entity_instance, None]
    rel: Union[ifcopenshell.entity_instance, None]
    activities: list[int]


class ScheduleIfcGenerator:
    file: Union[ifcopenshell.file, None]
    calendars: dict[int, Calendar]

    def __init__(self, file: Union[ifcopenshell.file, None], output, settings):
        self.file = file
        self.work_plan = settings["work_plan"]
        self.project = settings["project"]
        self.calendars = settings["calendars"]
        self.wbs = settings["wbs"]
        self.root_activites = settings["root_activities"]
        self.activities = settings["activities"]
        self.relationships = settings["relationships"]
        self.resources = settings["resources"]
        self.output = output
        self.day_map = {
            "Monday": 1,
            "Tuesday": 2,
            "Wednesday": 3,
            "Thursday": 4,
            "Friday": 5,
            "Saturday": 6,
            "Sunday": 7,
        }

    def create_ifc(self) -> None:
        if not self.file:
            self.file = self.create_boilerplate_ifc()
        if not self.work_plan:
            self.work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)
        work_schedule = self.create_work_schedule()
        self.create_calendars()
        self.create_tasks(work_schedule)
        self.create_rel_sequences()
        self.create_resources()
        if self.output:
            self.file.write(self.output)

    def create_work_schedule(self) -> ifcopenshell.entity_instance:
        return ifcopenshell.api.sequence.add_work_schedule(
            self.file, name=self.project["Name"], work_plan=self.work_plan
        )

    def create_calendars(self) -> None:
        for calendar_id, calendar in self.calendars.items():
            calendar["ifc"] = ifcopenshell.api.sequence.add_work_calendar(self.file, name=calendar["Name"])
            calendar["ifc"].Identification = str(calendar_id)
            self.process_working_week(calendar["StandardWorkWeek"], calendar["ifc"])
            self.process_exceptions(calendar.get("HolidayOrExceptions"), calendar["ifc"])

    def process_working_week(self, week: list[WorkSlot], calendar: ifcopenshell.entity_instance) -> None:
        for day in week:
            if day["ifc"] or not day.get("WorkTimes"):
                continue

            day["ifc"] = ifcopenshell.api.sequence.add_work_time(
                self.file, work_calendar=calendar, time_type="WorkingTimes"
            )
            weekday_component = [self.day_map[day["DayOfWeek"]]]
            for day2 in week:
                if day["DayOfWeek"] == day2["DayOfWeek"]:
                    continue
                if day["WorkTimes"] == day2["WorkTimes"]:
                    weekday_component.append(self.day_map[day2["DayOfWeek"]])
                    # Don't process the next day, as we can group it
                    day2["ifc"] = day["ifc"]

            work_time_name = "Weekdays: {}".format(", ".join([str(c) for c in sorted(weekday_component)]))
            ifcopenshell.api.sequence.edit_work_time(
                self.file,
                work_time=day["ifc"],
                attributes={"Name": work_time_name},
            )

            recurrence = ifcopenshell.api.sequence.assign_recurrence_pattern(
                self.file, parent=day["ifc"], recurrence_type="WEEKLY"
            )
            ifcopenshell.api.sequence.edit_recurrence_pattern(
                self.file,
                recurrence_pattern=recurrence,
                attributes={"WeekdayComponent": weekday_component},
            )
            for work_time in day["WorkTimes"]:
                ifcopenshell.api.sequence.add_time_period(
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def process_exceptions(
        self, exceptions: Union[ExceptionsDict, None], calendar: ifcopenshell.entity_instance
    ) -> None:
        if exceptions:
            for year, year_data in exceptions.items():
                for month, month_data in year_data.items():
                    if month_data["FullDay"]:
                        self.process_full_day_exceptions(year, month, month_data, calendar)
                    if month_data["WorkTime"]:
                        self.process_work_time_exceptions(year, month, month_data, calendar)

    def process_full_day_exceptions(
        self, year: int, month: int, month_data: dict[str, Any], calendar: ifcopenshell.entity_instance
    ):
        work_time = ifcopenshell.api.sequence.add_work_time(
            self.file, work_calendar=calendar, time_type="ExceptionTimes"
        )
        ifcopenshell.api.sequence.edit_work_time(
            self.file,
            work_time=work_time,
            attributes={
                "Name": f"{year}-{month}",
                "Start": date(year, 1, 1),
                "Finish": date(year, 12, 31),
            },
        )
        recurrence = ifcopenshell.api.sequence.assign_recurrence_pattern(
            self.file,
            parent=work_time,
            recurrence_type="YEARLY_BY_DAY_OF_MONTH",
        )
        ifcopenshell.api.sequence.edit_recurrence_pattern(
            self.file,
            recurrence_pattern=recurrence,
            attributes={"DayComponent": month_data["FullDay"], "MonthComponent": [month]},
        )

    def process_work_time_exceptions(
        self, year: int, month: int, month_data: dict[str, Any], calendar: ifcopenshell.entity_instance
    ) -> None:
        for day in month_data["WorkTime"]:
            if day["ifc"]:
                continue

            day["ifc"] = ifcopenshell.api.sequence.add_work_time(
                self.file, work_calendar=calendar, time_type="ExceptionTimes"
            )

            day_component = [day["Day"]]
            for day2 in month_data["WorkTime"]:
                if day["Day"] == day2["Day"]:
                    continue
                if day["WorkTimes"] == day2["WorkTimes"]:
                    day_component.append(day2["Day"])
                    # Don't process the next day, as we can group it
                    day2["ifc"] = day["ifc"]

            ifcopenshell.api.sequence.edit_work_time(
                self.file,
                work_time=day["ifc"],
                attributes={
                    "Name": "{}-{}-{}".format(year, month, ", ".join([str(d) for d in day_component])),
                    "Start": date(year, 1, 1),
                    "Finish": date(year, 12, 31),
                },
            )
            recurrence = ifcopenshell.api.sequence.assign_recurrence_pattern(
                self.file,
                parent=day["ifc"],
                recurrence_type="YEARLY_BY_DAY_OF_MONTH",
            )
            ifcopenshell.api.sequence.edit_recurrence_pattern(
                self.file,
                recurrence_pattern=recurrence,
                attributes={"DayComponent": day_component, "MonthComponent": [month]},
            )
            for work_time in day["WorkTimes"]:
                ifcopenshell.api.sequence.add_time_period(
                    self.file,
                    recurrence_pattern=recurrence,
                    start_time=work_time["Start"],
                    end_time=work_time["Finish"],
                )

    def create_tasks(self, work_schedule: ifcopenshell.entity_instance) -> None:
        for wbs in self.wbs.values():
            self.create_task_from_wbs(wbs, work_schedule)
        for activity_id in self.root_activites:
            self.create_task_from_activity(self.activities[activity_id], None, work_schedule)

    def create_task_from_wbs(self, wbs: WBSEntry, work_schedule: ifcopenshell.entity_instance) -> None:
        if not self.wbs.get(wbs["ParentObjectId"]):
            wbs["ParentObjectId"] = None
        wbs["ifc"] = ifcopenshell.api.sequence.add_task(
            self.file,
            work_schedule=None if wbs["ParentObjectId"] else work_schedule,
            parent_task=self.wbs[wbs["ParentObjectId"]]["ifc"] if wbs["ParentObjectId"] else None,
        )
        identification = wbs["Code"]
        if wbs["ParentObjectId"]:
            if self.wbs[wbs["ParentObjectId"]]["ifc"]:
                identification = str(self.wbs[wbs["ParentObjectId"]]["ifc"].Identification) + "." + str(wbs["Code"])
        ifcopenshell.api.sequence.edit_task(
            self.file,
            task=wbs["ifc"],
            attributes={"Name": wbs["Name"], "Identification": str(identification)},
        )
        for activity_id in wbs["activities"]:
            self.create_task_from_activity(self.activities[activity_id], wbs, None)

    def create_task_from_activity(
        self,
        activity: Activity,
        wbs: Union[WBSEntry, None],
        work_schedule: Union[ifcopenshell.entity_instance, None],
    ) -> None:
        activity["ifc"] = ifcopenshell.api.sequence.add_task(
            self.file,
            work_schedule=None if wbs else work_schedule,
            parent_task=wbs["ifc"] if wbs else None,
        )
        ifcopenshell.api.sequence.edit_task(
            self.file,
            task=activity["ifc"],
            attributes={
                "Name": activity["Name"],
                "Identification": str(activity["Identification"]),
                "Status": activity["Status"],
                "IsMilestone": activity["StartDate"] == activity["FinishDate"],
                "PredefinedType": "CONSTRUCTION",
            },
        )
        task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=activity["ifc"])
        calendar = self.calendars[activity["CalendarObjectId"]]
        # Seems intermittently crashy - can we investigate for larger files?
        ifcopenshell.api.control.assign_control(
            self.file,
            relating_control=calendar["ifc"],
            related_object=activity["ifc"],
        )
        ifcopenshell.api.sequence.edit_task_time(
            self.file,
            task_time=task_time,
            attributes={
                "ScheduleStart": activity["StartDate"],
                "ScheduleFinish": activity["FinishDate"],
                "DurationType": "WORKTIME" if activity["PlannedDuration"] else None,
                "ScheduleDuration": (
                    timedelta(days=float(activity["PlannedDuration"]) / float(calendar["HoursPerDay"] or 8)) or None
                    if activity["PlannedDuration"]
                    else None
                ),
            },
        )

    def create_rel_sequences(self) -> None:
        self.sequence_type_map = {
            "Start to Start": "START_START",
            "Start to Finish": "START_FINISH",
            "Finish to Start": "FINISH_START",
            "Finish to Finish": "FINISH_FINISH",
        }
        for relationship in self.relationships.values():
            rel_sequence = ifcopenshell.api.sequence.assign_sequence(
                self.file,
                relating_process=self.activities[relationship["PredecessorActivity"]]["ifc"],
                related_process=self.activities[relationship["SuccessorActivity"]]["ifc"],
            )
            ifcopenshell.api.sequence.edit_sequence(
                self.file,
                rel_sequence=rel_sequence,
                attributes={"SequenceType": relationship["Type"]},
            )
            lag = float(relationship["Lag"])
            if lag:
                calendar = self.calendars[self.activities[relationship["PredecessorActivity"]]["CalendarObjectId"]]
                ifcopenshell.api.sequence.assign_lag_time(
                    self.file,
                    rel_sequence=rel_sequence,
                    lag_value=timedelta(days=lag / float(calendar["HoursPerDay"] or 8)),
                    duration_type="WORKTIME",
                )

    def create_resources(self) -> None:
        if self.resources:
            for id, resource in self.resources.items():

                parent = self.resources.get(resource.get("ParentObjectId"))
                if parent:
                    if not parent.get("ifc"):
                        parent["ifc"] = ifcopenshell.api.resource.add_resource(
                            self.file,
                            ifc_class="IfcCrewResource",
                            name=parent["Name"],
                        )
                if parent:
                    resource["ifc"] = ifcopenshell.api.resource.add_resource(
                        self.file,
                        parent_resource=parent["ifc"] if parent else None,
                        ifc_class="IfcCrewResource",
                        name=resource["Name"],
                    )
                else:
                    resource["ifc"] = ifcopenshell.api.resource.add_resource(
                        self.file, ifc_class="IfcCrewResource", name=resource["Name"]
                    )

    def create_boilerplate_ifc(self) -> None:
        self.file = ifcopenshell.file(schema="IFC4")
        self.work_plan = self.file.create_entity("IfcWorkPlan")
