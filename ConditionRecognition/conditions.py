verb_categories = ["Go to", "Grasp", "Place", "Cut"]
fruit_categories = ["Kiwi", "Carrot", "Banana", "Tomato", "Orange"]
places_categories = ["Board", "Table", "Bowl"]
tool_categories = ["Gripper", "Hands", "Knife"]

relations = {
    "Go to": {
        "Pre": [
            "{picker} not over {object}"
        ],
        "Post": [
            "{picker} over {object}"
        ]
    },
    "Grasp": {
        "Pre": [
            "{picker} over {object}",
            "{picker} free/opened",  # free hand, opened gripper
        ],
        "Post": [
            "{object} in {picker}",
        ]
    },
    "Place": {
        "Pre": {
            "Table": [
                "{object} in {picker}"
            ],
            "Board": [
                "{object} in {picker}",
                "Board is free"
            ],

        },

        "Post": [
            "{picker} is free",
            "{object} on {place}"
        ]
    },
    "Cut": {
        "Pre": [
            "Knife in {picker}",
            "{object} on Board",
            "{object} is whole"
        ],
        "Post": [
            "{object} is sliced"
        ]
    }}

"""

.....................
GO TO [Object] 
(hand or gripper)
_____________
    PRE
        Hand / Gripper Not OVER the [Object] 
    POST
        Hand / Gripper OVER the [Object] 
        
.....................
GRASP [OBJECT] 
    - OBJECT can be FRUIT or Knife
_____________
    PRE
        Hand / Gripper Free / Opened
        OBJECT on Table / Board
    POST
        OBJECT Not on Table / board
        OBJECT in Hand / Gripper

.....................
PLACE [OBJECT] into [PLACE]
_____________
    PRE
        OBJECT in Hand / Gripper
        if PLACE == Table : (Not define that the place is free)
        if PLACE == Board: Board is free
        
    POST
        OBJECT / Hand is Free
        OBJECT on PLACE
        
        
.....................
CUT [OBJECT]
_____________
    PRE
        knife in Hand/Gripper
        OBJECT on Board
        OBJECT is whole
    POST
        OBJECT is Sliced

"""
