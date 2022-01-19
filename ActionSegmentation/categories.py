verb_categories = ["Go to", "Grasp", "Place", "Cut"]
fruit_categories  =  ["Kiwi", "Carrot", "Banana", "Tomato", "Orange"]
places_categories =  ["Board", "Table", "Bowl"]
tool_categories = ["Gripper", "Hands", "Knife"]

relations = {
                "Go to" : fruit_categories + places_categories + ["knife"],
                "Grasp" : fruit_categories  + ["knife"],
                "Place" : places_categories,
                "Cut" : fruit_categories
             }