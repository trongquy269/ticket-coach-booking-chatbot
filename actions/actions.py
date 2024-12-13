# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import requests
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class ActionGetGarageInfo(Action):
    def name(self) -> str:
        return "action_get_garage_info"

    def format_garage_names(self, garages):
        if not garages:
            return "Không có nhà xe nào."

        # Lấy tên các nhà xe
        names = [garage['name'] for garage in garages]

        # Nếu chỉ có một nhà xe
        if len(names) == 1:
            return names[0]
        # Nếu có hai nhà xe
        elif len(names) == 2:
            return f"{names[0]} và {names[1]}"
        # Nếu có ba nhà xe trở lên
        else:
            return ", ".join(names[:-1]) + " và " + names[-1]

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        try:
            response = requests.get("http://localhost:3000/manager-garage")
            garages = response.json()  # Assuming this returns a list

            # Example: Iterate over the list and create a message
            if isinstance(garages, list):
                garage_names = self.format_garage_names(garages)
                dispatcher.utter_message(text=f"Có {len(garages)} nhà xe: {garage_names}")
            else:
                dispatcher.utter_message(text="Không có nhà xe nào.")

        except Exception as e:
            dispatcher.utter_message(text="Xin lỗi, có thể tôi đã bị lỗi trong quá trình thu thập thông tin.")
            print(f"Error: {e}")

        return []


class ActionGetRoute(Action):
    def name(self) -> str:
        return "action_get_route"

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: dict) -> list:
        start_place = tracker.get_slot("start_place")
        end_place = tracker.get_slot("end_place")
        print(f"Start Place: {start_place}, End Place: {end_place}")

        if not start_place or not end_place:
            dispatcher.utter_message(text="Vui lòng cung cấp cả điểm đi và điểm đến.")
            return []

        try:
            response = requests.get("http://localhost:3000/routes")
            routes = response.json()

            # Filter routes that match start and end cities
            matching_routes = [
                route for route in routes
                if route["start_place"] == start_place and route["end_place"] == end_place
            ]
            print(matching_routes)

            if matching_routes:
                route_info = f"Có {len(matching_routes)} chuyến từ {start_place} đến {end_place}."
            else:
                route_info = f"Không tìm thấy chuyến nào từ {start_place} đến {end_place}."

            dispatcher.utter_message(text=route_info)

            return []
        except Exception as e:
            dispatcher.utter_message(text="Xin lỗi, tôi gặp sự cố khi tìm kiếm thông tin chuyến đi.")
            print(f"Error: {e}")
            return []
