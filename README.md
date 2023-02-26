# Tip Tracker

PyHamilton application for tracking tips, similar to Visual NTR.

The `TipTracker` class allows the user to track and restock stacked tips across experiments.
Tips are accessed with either `get_tips(n)` or `get_96_tips()` methods, which pick up the
specified number of tips and automatically subtract the number from the `json_data` dictionary,
and updating the corresponding json file.

When a rack is empty, it will be discarded by the CO-RE gripper and the corresponding `json_data`
dictionary entry for that rack will be marked `['discarded'] = True`.

The method `run_editor()` will open a window for the user to reset the numbers of tips or edit stacks.

## Example Usage

```python
tip_tracker_NTR300_ch = TipTracker('NTR300_channels.json',
                        'FN Deck Layout.lay',
                        'Waste_NTR50',
                        'COREGripTool_OnWaste_1000ul_0001',
                        gripHeight = 5,
                        gripWidth = 90,
                        openWidth = 100)

tip_tracker_NTR300_ch.run_editor()

tip_tracker_NTR50_MPH = TipTracker('NTR50_MPH.json',
                       'FN Deck Layout.lay',
                       'Waste_NTR50',
                       'COREGripTool_OnWaste_1000ul_0001',
                       gripHeight = 5,
                       gripWidth = 90,
                       openWidth = 100)
tip_tracker_NTR50_MPH.run_editor()

if __name__ == '__main__':
    with HamiltonInterface(simulate=True) as ham_int:
        initialize(ham_int)
        normal_logging(ham_int, os.getcwd())

        tip_tracker_NTR50_MPH.apply_interface(ham_int)
        tip_tracker_NTR300_ch.apply_interface(ham_int)

        for i in range(8):
            # NTR50 MPH
            tip_tracker_NTR50_MPH.get_96_tips()
            tip_eject_96(ham_int)
            
        for i in range(90):
            # NTR300
            tip_tracker_NTR300_ch.get_tips(8)
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
Access with `run_editor()` <br>
![](https://github.com/stefangolas/tip_tracker/blob/main/images/tkinter.png)
