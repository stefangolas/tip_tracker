# Tip Tracker

PyHamilton application for tracking tips

# Example Usage

```python
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

```
