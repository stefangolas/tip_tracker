# -*- coding: utf-8 -*-
"""
Created on Thu Dec 22 11:56:10 2022

@author: stefa
"""

import tkinter as tk
from tkinter import ttk
import json
import os
import copy
import sys

from pyhamilton import (HamiltonInterface,  LayoutManager, 
 Plate96, Tip96, initialize, tip_pick_up, tip_eject, 
 aspirate, dispense,  oemerr, resource_list_with_prefix, normal_logging,
 get_plate_gripper_seq, place_plate_gripper_seq, ResourceType, tip_pick_up_96, ResourceUnavailableError)


class TipTracker:
    
    def __init__(self, json_path, deck_path, waste_seq, tool_seq,
                 gripHeight = 5, gripWidth = 90, openWidth = 100):
        
        """
        The JSON file contains a list of objects, where each object represents 
        a stack of tip racks. Each stack has a name (stack_name), a maximum number 
        of tip racks (max_tip_racks), and a list of tip racks (racks).
        Each tip rack has a name (rack_name), a number of tips (num_tips), 
        and a boolean value indicating whether it is discarded or not (discarded).
        
        """
       
        self.json_path = json_path
        
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump({}, f)
        
        with open(json_path, "r") as f:
            self.json_data = json.load(f)
        
        
        self.lmgr = LayoutManager(deck_path)
        self.hamilton_interface = None
        self.waste_seq = waste_seq
        self.tool_seq = tool_seq
        self.gripHeight = gripHeight
        self.gripWidth = gripWidth
        self.openWidth = openWidth
        
        self.assign_resources()
        self.create_gui()
        
    
    def apply_interface(self, hamilton_interface):
        self.hamilton_interface = hamilton_interface
        self.assign_resources()
    
    def create_gui(self):
        """
        Renders a Tkinter GUI with buttons for interacting with the JSON database.
        """
        
        root = tk.Tk()
        self.root = root
        
        title = self.json_path.split('.')[0]
        root.title(title)

        # Create the treeview
        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("num_tips")
        self.tree.column("#0", width=200)
        self.tree.column("num_tips", width=100)
        self.tree.heading("#0", text="Rack Name")
        self.tree.heading("num_tips", text="Number of Tips")

        # Populate the treeview with the JSON data
        for stack_id in self.json_data:
            stack = self.json_data[stack_id]
            stack_node = self.tree.insert("", "end", text=stack["stack_name"], values=(stack["max_tip_racks"]))
            for rack in stack["racks"]:
                self.tree.insert(stack_node, "end", text=rack["rack_name"], values=(rack["num_tips"]))

        # Add a scrollbar to the treeview
        yscrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        
        remove_stack_button = tk.Button(root, text="Remove Stack", command=self.remove_stack)
        add_stack_button = tk.Button(root, text="Add Stack", command=self.add_stack)
        add_rack_button = tk.Button(root, text="Add Rack", command=self.add_rack)
        reset_tips_button = tk.Button(root, text="Reset Tips", command=self.reset_tips)
        remove_stack_button.pack()
        add_stack_button.pack()
        add_rack_button.pack()
        reset_tips_button.pack()
        
        # Create a label for the entry form for changing the stack name
        name_label = tk.Label(self.root, text="Enter new stack name:")
        name_label.pack()

        # Create the entry form for changing the stack name
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack()

        # Create a button for changing the stack name
        change_name_button = tk.Button(self.root, text="Change Name", command=self.change_stack_name)
        change_name_button.pack()        
        
        tips_label = tk.Label(self.root, text="Enter new number of tips:")
        tips_label.pack()
     
        self.tips_entry = tk.Entry(self.root)
        self.tips_entry.pack()

        # Create a button for changing the number of tips
        change_tips_button = tk.Button(self.root, text="Change # of Tips", command=self.change_tips)
        change_tips_button.pack()

    def run(self):
        self.root.mainloop()
        
    
    def change_tips(self):
    # Get the new number of tips from the entry form
        new_tips = self.tips_entry.get()
        new_tips = int(new_tips)
    # Get the selected rack node
        selected_item = self.tree.selection()[0]

    # If an item is not selected or if the selected item is a stack, return
        if not selected_item or not self.tree.parent(selected_item):
            print("Not a rack")
            return

       # Get the rack data from the JSON data
        stack_key = next(stack for stack in self.json_data if any(rack["rack_name"] == self.tree.item(selected_item)["text"] for rack in self.json_data[stack]["racks"]))
        rack_num, rack = next(rack for rack in enumerate(self.json_data[stack_key]["racks"]) if rack[1]["rack_name"] == self.tree.item(selected_item)["text"])
                
        # Update the number of tips in the JSON data and the treeview
        #self.json_data[stack][rack]['num_tips'] = int(new_tips)
        self.json_data[stack_key]["racks"][rack_num]["num_tips"] = new_tips
        if new_tips > 0:
            self.json_data[stack_key]["racks"][rack_num]['discarded'] = False
        
        self.tree.item(selected_item, values=(new_tips))
        
        self.save()
    
    def change_stack_name(self):
        # Get the new stack name from the entry form
        new_name = self.name_entry.get()

        # Get the selected stack node
        selected_item = self.tree.selection()[0]
    
        # If an item is not selected or if the selected item is a rack, return
        if not selected_item or self.tree.parent(selected_item):
            print("Not a stack")
            return
    
        # Get the stack data from the JSON data
        stack_data = next(self.json_data[stack] for stack in self.json_data if self.json_data[stack]["stack_name"] == self.tree.item(selected_item)["text"])

        # Update the stack name in the JSON data and the treeview
        stack_data["stack_name"] = new_name
        self.tree.item(selected_item, text=new_name)
        for i, rack in enumerate(stack_data["racks"]):
            rack["rack_name"] = new_name + "_" + str(i + 1).zfill(4)

        # Update the rack names in the treeview
        for i, child in enumerate(self.tree.get_children(selected_item)):
            self.tree.item(child, text=stack_data["racks"][i]["rack_name"])

        self.save()


    def change_max_racks(self):
        # Get the new maximum number of racks from the entry form
        new_max = int(self.max_entry.get())

        # Get the selected stack node
        selected_item = self.tree.selection()[0]

        # If a stack node is not selected, return
        if not selected_item:
            return

        # Get the stack data from the JSON data
        stack_data = next(self.json_data[stack] for stack in self.json_data if stack["stack_name"] == self.tree.item(selected_item)["text"])

        # Update the maximum number of racks in the JSON data and the treeview
        stack_data["max_tip_racks"] = new_max
        self.tree.item(selected_item, values=(new_max))

    
    def add_stack(self):
        """
        Adds a stack of tips to the json_data dictionary and GUI window, with 4 full racks by default.
        New stacks must be renamed to match the name of a stack in the deck layout.
        """
        # Add a new stack to the list with a default name and number of tip racks
        new_stack = {
            "stack_name": "New_Stack",
            "max_tip_racks": 4,
            "racks": [{
                "rack_name": "New_Stack_000" + str(i),
                "num_tips": 96,
                "discarded": False,
                "resource": None
            } for i in range(1,5)]
        }
        
        stack_idx = len(self.json_data)
        self.json_data["New Stack " + str(stack_idx)] = new_stack
        
        # Add the new stack to the treeview
        stack_node = self.tree.insert("", "end", text=new_stack["stack_name"], values=(new_stack["max_tip_racks"]))
       
        for rack_idx in range(4):
            self.tree.insert(stack_node, "end", text="New_Stack_000" + str(rack_idx+1), values=(96))
        
        self.save()
    
    def remove_stack(self):
        
        selected_stack = self.tree.selection()[0]
        stack_key = (self.tree.item(selected_stack, "text"))
        # Remove the selected stack
        self.json_data.pop(stack_key)

        # Add the new stack to the treeview
        self.tree.delete(selected_stack)
        self.save()
        
        
    def add_rack(self):
        """
        Adds a rack to a stack of tips.
        """
        # Get the selected stack node
        selected_item = self.tree.selection()[0]
    
        # If an item is not selected or if the selected item is a rack, return
        if not selected_item or self.tree.parent(selected_item):
            return
    
        # Get the stack data from the JSON data
        stack_data = next(self.json_data[stack] for stack in self.json_data if self.json_data[stack]["stack_name"] == self.tree.item(selected_item)["text"])
        
        if len(stack_data["racks"]) >= stack_data["max_tip_racks"]:
            return
        
        # Generate a new rack name for the stack
        rack_name = stack_data["stack_name"] + "_" + str(len(stack_data["racks"]) + 1).zfill(4)
    
        # Add a new rack to the stack with the generated name and default number of tips
        new_rack = {
            "rack_name": rack_name,
            "num_tips": 96,
            "discarded": False
        }
        stack_data["racks"].append(new_rack)
    
        # Add the new rack to the treeview
        self.tree.insert(selected_item, "end", text=new_rack["rack_name"], values=(new_rack["num_tips"]))
        self.save()
        
    def reset_tips(self):
        """
        Set the number of tips in the selected rack to 96. 
        Triggered by the user pressing the Reset Tips button.
        """
        # Get the selected rack node
        selected_item = self.tree.selection()[0]

        # If a rack node is not selected, return
        if not self.tree.parent(selected_item):
            return
        
        stack_key = next(stack for stack in self.json_data if any(rack["rack_name"] == self.tree.item(selected_item)["text"] for rack in self.json_data[stack]["racks"]))
        rack_num, rack = next(rack for rack in enumerate(self.json_data[stack_key]["racks"]) if rack[1]["rack_name"] == self.tree.item(selected_item)["text"])
                
        # Update the number of tips in the JSON data and the treeview
        self.json_data[stack_key]["racks"][rack_num]["num_tips"] = 96
        self.json_data[stack_key]["racks"][rack_num]['discarded'] = False            

        
        self.tree.item(selected_item, values=(96))
        self.save()

    
    
    def save(self):
        """
        Writes the json_data dictionary to a JSON file
        """
        json_data = copy.deepcopy(self.json_data)
        for stack_id in json_data: # Loop that removes unserializable data from JSON structure
            stack = json_data[stack_id]
            for rack in stack['racks']:
                rack.pop('resource') # Remove unserializable resource item
        with open(self.json_path, "w") as f:
            json.dump(json_data, f)

    def assign_resources(self):
        """
        Adds a resource key to the json_data dictionary at run-time for non-serializable DeckResource objects.
        """
        for stack_id in list(self.json_data):
            stack = self.json_data[stack_id]
            for rack in stack['racks']:
                if 'resource' in rack:
                    continue
                try:
                    rack['resource'] = self.lmgr.assign_unused_resource(ResourceType(Tip96, rack['rack_name']))
                except ResourceUnavailableError:
                    print("Invalid stack name detected, removing from JSON")
                    self.json_data.pop(stack_id)
                    break
            
    def get_tips(self, num_tips):
        """
        Retrieve a list of tips from the top rack in a stack.
        If the top rack does not have enough tips, the next rack is discarded and the
        function is called again.
        """
        for stack_idx, stack_id in enumerate(self.json_data):
            stack = self.json_data[stack_id]
            racks = stack['racks']
            try:
                top_rack_idx = max([i for i, rack in enumerate(racks) if not rack['discarded']])
            except ValueError:
                raise Exception("No tips remaining in any stack")
            rack = stack['racks'][top_rack_idx]
            if not rack['discarded'] and rack['num_tips'] >= num_tips:
                current_tip = 96 - rack['num_tips']
                resource = rack['resource']
                tips_list = [(resource, tip) for tip in range(current_tip, current_tip + num_tips)]
                self.json_data[stack_id]['racks'][top_rack_idx]['num_tips'] -= num_tips
                tip_pick_up(self.hamilton_interface, tips_list)
                self.save()
                return
        
        self.discard_empty_racks()
        self.get_tips(num_tips)
        
    
    def discard_empty_racks(self):
        """
        Loop through stacks and discard any empty racks from the top of the stack
        using the CO-RE gripper. 
        """
        for stack_idx, stack_id in enumerate(self.json_data):
            stack = self.json_data[stack_id]
            racks = stack['racks']
            top_rack_idx = max([i for i, rack in enumerate(racks) if not rack['discarded']])
            rack = stack['racks'][top_rack_idx]
            if not rack['discarded'] and rack['num_tips'] == 0:
                resource = rack['resource']
                get_plate_gripper_seq(self.hamilton_interface, resource.layout_name(), 
                                      gripHeight = self.gripHeight, gripWidth = self.gripWidth, openWidth=self.openWidth, lid = False,
                                      tool_sequence = self.tool_seq)
                place_plate_gripper_seq(self.hamilton_interface, self.waste_seq, self.tool_seq)
                self.json_data[stack_id]['racks'][top_rack_idx]['discarded'] = True
        
        
        
    def get_96_tips(self):
        """
        Use the 96-head to pick up a whole rack of tips from the top of a stack.
        """
        for stack_idx, stack_id in enumerate(self.json_data):
            stack = self.json_data[stack_id]
            racks = stack['racks']
            try:
                top_rack_idx = max([i for i, rack in enumerate(racks) if not rack['discarded']])
            except ValueError:
                raise Exception("No tips remaining in any stack")
            rack = stack['racks'][top_rack_idx]
            if not rack['discarded'] and rack['num_tips'] == 96:
                resource = rack['resource']
                self.json_data[stack_id]['racks'][top_rack_idx]['num_tips'] = 0
                tip_pick_up_96(self.hamilton_interface, resource)
                self.save()
                return
        self.discard_empty_racks()
        self.get_96_tips()

    
    def discard_next_rack(self):
        """
        Discard the next rack in the list of racks.
        This function moves the gripper to the next rack, picks it up, and moves it to the
        waste container. The rack is then marked as discarded in the JSON data.

        """
        lowest_tips_num = 96
        for stack_idx, stack in enumerate(self.json_data):
            racks = self.json_data[stack]['racks']
            top_rack_idx = max([i for i, rack in enumerate(racks) if not rack['discarded']])
            if racks[top_rack_idx]['num_tips'] < lowest_tips_num and top_rack_idx>0:
                discard_idxs = (stack, top_rack_idx)
                lowest_tips_num = racks[top_rack_idx]['num_tips']
        
        if not discard_idxs:
            raise Exception("No racks remaining to discard")
        stack, rack_idx = discard_idxs
        resource = self.json_data[stack]['racks'][rack_idx]['resource']
        get_plate_gripper_seq(self.hamilton_interface, resource.layout_name(), 
                              gripHeight = 5, gripWidth = 90, openWidth=100, lid = False,
                              tool_sequence = self.tool_seq)
        place_plate_gripper_seq(self.hamilton_interface, self.waste_seq, self.tool_seq)
        self.json_data[stack]['racks'][rack_idx]['discarded'] = True
        self.json_data[stack]['racks'][rack_idx]['num_tips'] = 0
        self.save()
            
        
    def run_editor(self):
        self.run()

        

if __name__ == "__main__":
    tip_tracker = TipTracker(json_path = 'newfile.json', 
                                 deck_path = 'deck.lay', 
                                 waste_seq = 'tips_waste',
                                 tool_seq = 'COREGripTool',
                                 gripHeight = 5,
                                 gripWidth = 90,
                                 openWidth = 100)
    
    
    input("")
    with HamiltonInterface(simulate=True) as ham_int:
        initialize(ham_int)
        tip_tracker.apply_interface(ham_int)
        tip_tracker.run_editor()
        initialize(ham_int)
        for i in range(80):
            tip_tracker.get_tips(4)
            tip_eject(ham_int)

