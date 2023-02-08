# Tip Tracker

PyHamilton application for tracking tips

# Example Usage

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
