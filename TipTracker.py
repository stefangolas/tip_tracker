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

from pyhamilton import (HamiltonInterface,  LayoutManager, 
 Plate96, Tip96, initialize, tip_pick_up, tip_eject, 
 aspirate, dispense,  oemerr, resource_list_with_prefix, normal_logging,
 get_plate_gripper_seq, place_plate_gripper_seq, ResourceType)


class TipRackEditor:
    def __init__(self, json_path):
        root = tk.Tk()
        self.root = root
        with open(json_path, "r") as f:
            json_data = json.load(f)
        
        self.json_data = json_data

        # Create the treeview
        self.tree = ttk.Treeview(self.root)
        self.tree["columns"] = ("num_tips")
        self.tree.column("#0", width=200)
        self.tree.column("num_tips", width=100)
        self.tree.heading("#0", text="Rack Name")
        self.tree.heading("num_tips", text="Number of Tips")

        # Populate the treeview with the JSON data
        for stack in self.json_data:
            stack_node = self.tree.insert("", "end", text=stack["stack_name"], values=(stack["max_tip_racks"]))
            for rack in stack["racks"]:
                self.tree.insert(stack_node, "end", text=rack["rack_name"], values=(rack["num_tips"]))

        # Add a scrollbar to the treeview
        yscrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=yscrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        save_button = tk.Button(self.root, text="Save", command=self.save)
        save_button.pack()
        
        add_stack_button = tk.Button(root, text="Add Stack", command=self.add_stack)
        add_rack_button = tk.Button(root, text="Add Rack", command=self.add_rack)
        reset_tips_button = tk.Button(root, text="Reset Tips", command=self.reset_tips)
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

        # Create a label for the entry form for changing the maximum number of racks
        max_label = tk.Label(self.root, text="Enter new maximum number of racks:")
        max_label.pack()
        
        self.max_entry = tk.Entry(self.root)
        self.max_entry.pack()

        # Create a button for changing the maximum number of racks
        change_max_button = tk.Button(self.root, text="Change Maximum", command=self.change_max_racks)
        change_max_button.pack()





    def run(self):
        self.root.mainloop()
        
    def save(self):
        # Write the updated JSON data to a file
        with open("template.json", "w") as f:
            json.dump(self.json_data, f, indent=4)
    
    def change_stack_name(self):
        # Get the new stack name from the entry form
        new_name = self.name_entry.get()

        # Get the selected stack node
        selected_item = self.tree.selection()[0]
    
        # If an item is not selected or if the selected item is a rack, return
        if not selected_item or self.tree.parent(selected_item):
            return
    
        # Get the stack data from the JSON data
        stack_data = next(stack for stack in self.json_data if stack["stack_name"] == self.tree.item(selected_item)["text"])

        # Update the stack name in the JSON data and the treeview
        stack_data["stack_name"] = new_name
        self.tree.item(selected_item, text=new_name)
        for i, rack in enumerate(stack_data["racks"]):
            rack["rack_name"] = new_name + "_" + str(i + 1).zfill(2)
            self.tree.item(self.tree.get_children(selected_item)[i], text=rack["rack_name"])



    def run(self):
        self.root.mainloop()
        
    def save(self):
        # Write the updated JSON data to a file
        with open("template.json", "w") as f:
            json.dump(self.json_data, f, indent=4)
    
    def change_stack_name(self):
        # Get the new stack name from the entry form
        new_name = self.name_entry.get()

        # Get the selected stack node
        selected_item = self.tree.selection()[0]
    
        # If an item is not selected or if the selected item is a rack, return
        if not selected_item or self.tree.parent(selected_item):
            return
    
        # Get the stack data from the JSON data
        stack_data = next(stack for stack in self.json_data if stack["stack_name"] == self.tree.item(selected_item)["text"])

        # Update the stack name in the JSON data and the treeview
        stack_data["stack_name"] = new_name
        self.tree.item(selected_item, text=new_name)
        for i, rack in enumerate(stack_data["racks"]):
            rack["rack_name"] = new_name + "_" + str(i + 1).zfill(4)

    # Update the rack names in the treeview
        for i, child in enumerate(self.tree.get_children(selected_item)):
            self.tree.item(child, text=stack_data["racks"][i]["rack_name"])




    def change_max_racks(self):
        # Get the new maximum number of racks from the entry form
        new_max = int(self.max_entry.get())

        # Get the selected stack node
        selected_item = self.tree.selection()[0]

        # If a stack node is not selected, return
        if not selected_item:
            return

        # Get the stack data from the JSON data
        stack_data = next(stack for stack in self.json_data if stack["stack_name"] == self.tree.item(selected_item)["text"])

        # Update the maximum number of racks in the JSON data and the treeview
        stack_data["max_tip_racks"] = new_max
        self.tree.item(selected_item, values=(new_max))

    
    def add_stack(self):
        # Add a new stack to the list with a default name and number of tip racks
        new_stack = {
            "stack_name": "New Stack",
            "max_tip_racks": 2,
            "racks": []
        }
        self.json_data.append(new_stack)

        # Add the new stack to the treeview
        stack_node = self.tree.insert("", "end", text=new_stack["stack_name"], values=(new_stack["max_tip_racks"]))

    def add_rack(self):
            # Get the selected stack node
        selected_item = self.tree.selection()[0]
    
        # If an item is not selected or if the selected item is a rack, return
        if not selected_item or self.tree.parent(selected_item):
            return
    
        # Get the stack data from the JSON data
        stack_data = next(stack for stack in self.json_data if stack["stack_name"] == self.tree.item(selected_item)["text"])
        
        if len(stack_data["racks"]) >= stack_data["max_tip_racks"]:
            return
        
        # Generate a new rack name for the stack
        rack_name = stack_data["stack_name"] + "_" + str(len(stack_data["racks"]) + 1).zfill(4)
    
        # Add a new rack to the stack with the generated name and default number of tips
        new_rack = {
            "rack_name": rack_name,
            "num_tips": 96,
            "excluded": False
        }
        stack_data["racks"].append(new_rack)
    
        # Add the new rack to the treeview
        self.tree.insert(selected_item, "end", text=new_rack["rack_name"], values=(new_rack["num_tips"]))
    def reset_tips(self):
        # Get the selected rack node
        selected_item = self.tree.selection()[0]

        # If a rack node is not selected, return
        if not self.tree.parent(selected_item):
            return

        # Get the rack data from the JSON data
        stack_node = self.tree.parent(selected_item)
        stack_data = next(stack for stack in self.json_data if stack["stack_name"] == self.tree.item(stack_node)["text"])
        rack_data = next(rack for rack in stack_data["racks"] if rack["rack_name"] == self.tree.item(selected_item)["text"])

        # Reset the number of tips in the rack
        rack_data["num_tips"] = 96
        self.tree.item(selected_item, values=(rack_data["num_tips"]))

class TipTracker:
    
    def __init__(self, json_path, deck_path, hamilton_interface, waste_seq, tool_seq):
        
        """
        The JSON file contains a list of objects, where each object represents 
        a stack of tip racks. Each stack has a name (stack_name), a maximum number 
        of tip racks (max_tip_racks), and a list of tip racks (racks).
        Each tip rack has a name (rack_name), a number of tips (num_tips), 
        and a boolean value indicating whether it is excluded or not (excluded).
        
        """
       
        self.json_path = json_path
        
        if not os.path.exists(self.json_path):
            with open(self.json_path, 'w') as f:
                json.dump([], f)
        
        with open(json_path, "r") as f:
            self.json_data = json.load(f)
        
        self.editor = TipRackEditor(json_path)
        self.lmgr = LayoutManager(deck_path)
        self.hamilton_interface = hamilton_interface
        self.waste_seq = waste_seq
        self.tool_seq = tool_seq
        
        self.assign_resources()
    
    def save_json(self):
        json_data = copy.deepcopy(self.json_data)
        for stack in json_data:
            for rack in stack['racks']:
                rack.pop('resource')
        with open(self.json_path, "w") as f:
            json.dump(json_data, f)

    def assign_resources(self):
        for stack in self.json_data:
            for rack in stack['racks']:
                rack['resource'] = self.lmgr.assign_unused_resource(ResourceType(Tip96, rack['rack_name']))
            
    def get_tips(self, num_tips):
        """
        Retrieve a list of tips from the top rack in a stack.
        If the top rack does not have enough tips, the next rack is discarded and the
        function is called again.
        """
        for stack_idx, stack in enumerate(self.json_data):
            racks = stack['racks']
            top_rack_idx = max([i for i, rack in enumerate(racks) if not rack['excluded']])
            rack = stack['racks'][top_rack_idx]
            if not rack['excluded'] and rack['num_tips'] >= num_tips:
                current_tip = 96 - rack['num_tips']
                resource = rack['resource']
                tips_list = [(resource, tip) for tip in range(current_tip, current_tip + num_tips)]
                self.json_data[stack_idx]['racks'][top_rack_idx]['num_tips'] -= num_tips
                self.save_json()
                return tips_list
        self.discard_next_rack()
        self.get_tips(num_tips)
        
    def discard_next_rack(self):
        """
        Discard the next rack in the list of racks.
        This function moves the gripper to the next rack, picks it up, and moves it to the
        waste container. The rack is then marked as excluded in the JSON data.

        """
        lowest_tips_num = 96
        for stack_idx, stack in enumerate(self.json_data):
            racks = stack['racks']
            top_rack_idx = max([i for i, rack in enumerate(racks) if not rack['excluded']])
            if racks[top_rack_idx]['num_tips'] < lowest_tips_num and top_rack_idx>0:
                discard_idxs = (stack_idx, top_rack_idx)
                lowest_tips_num = racks[top_rack_idx]['num_tips']
        
        if not discard_idxs:
            raise Exception("No racks remaining to discard")
        stack_idx, rack_idx = discard_idxs
        resource = self.json_data[stack_idx]['racks'][rack_idx]['resource']
        get_plate_gripper_seq(self.hamilton_interface, resource.layout_name(), 
                              gripHeight = 5, gripWidth = 90, openWidth=100, lid = False,
                              tool_sequence = self.tool_seq)
        place_plate_gripper_seq(self.hamilton_interface, self.waste_seq, self.tool_seq)
        self.json_data[stack_idx]['racks'][rack_idx]['excluded'] = True
        self.save_json()
            
        
    def run_editor(self):
        self.editor.run()

        

if __name__ == "__main__":
    
    with HamiltonInterface(simulate=True) as ham_int:
        tip_tracker = TipTracker('template.json', 
                                 'deck.lay', 
                                 ham_int,
                                 'tips_waste',
                                 'COREGripTool')
        tip_tracker.run_editor()
        initialize(ham_int)
        for i in range(30):
            tips_poss = tip_tracker.get_tips(4)
            tip_pick_up(ham_int, tips_poss)
            tip_eject(ham_int)

