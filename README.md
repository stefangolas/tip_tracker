# Tip Tracker

PyHamilton application for tracking tips, similar to Visual NTR.

The `TipTracker` class allows the user to track and restock stacked tips across experiments.
Tips are access with either `get_tips(n)` or `get_96_tips()` methods, which pick up the
specified number of tips and automatically subtract the number from the `json_data` dictionary,
and updating the corresponding json file.

When a rack is empty, it will be discarded by the CO-RE gripper and the corresponding `json_data`
dictionary entry for that rack will be marked `['discarded'] = True`.

The method `run_editor()` will open a window for the user to reset the numbers of tips or edit stacks.

## Example Usage

```python
if __name__ == "__main__":
    
    with HamiltonInterface(simulate=True) as ham_int:
        tip_tracker = TipTracker(json_path = 'template.json', 
                                 deck_path = 'deck.lay', 
                                 hamilton_interface = ham_int,
                                 waste_seq = 'tips_waste',
                                 tool_seq = 'COREGripTool')
        tip_tracker.run_editor()
        initialize(ham_int)
        for i in range(80):
            tip_tracker.get_tips(4)
            tip_eject(ham_int)

```

## JSON Database

The JSON database tracks the number of tips in a json file that is generated from the `json_data` dictionary attribute of `TipTracker`. Here is an example of the JSON database, with one stack containing one rack of tips.

```json
{
    "tips_01": {
        "stack_name": "tips_01",
        "max_tip_racks": 4,
        "racks": [{
                "rack_name": "tips_01_0001",
                "num_tips": 96,
                "discarded": false
            }]
      }
}
```


## GUI
[](https://github.com/stefangolas/tip_tracker/blob/main/images/tkinter.png)
