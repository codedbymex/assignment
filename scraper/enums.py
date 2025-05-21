from enum import Enum


class ClickStatus(Enum):
    SUCCESS = "clicked_and_loaded"
    BUTTON_HIDDEN = "button_hidden"
    NO_NEW_ITEMS = "no_new_items"
    FAILURE = "failure"