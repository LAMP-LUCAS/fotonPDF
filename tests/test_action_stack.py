
from pathlib import Path
from src.interfaces.gui.state.action_stack import ActionStack

def test_action_stack_logic():
    stack = ActionStack(Path("initial.pdf"))
    assert stack.current_state == Path("initial.pdf")
    assert not stack.can_undo
    
    stack.push(Path("v1.pdf"))
    assert stack.current_state == Path("v1.pdf")
    assert stack.can_undo
    assert not stack.can_redo
    
    stack.push(Path("v2.pdf"))
    assert stack.current_state == Path("v2.pdf")
    
    # Undo
    s = stack.undo()
    assert s == Path("v1.pdf")
    assert stack.current_state == Path("v1.pdf")
    assert stack.can_redo
    
    # Redo
    s = stack.redo()
    assert s == Path("v2.pdf")
    assert stack.current_state == Path("v2.pdf")
    
    # Undo twice
    stack.undo()
    stack.undo()
    assert stack.current_state == Path("initial.pdf")
    assert not stack.can_undo
    
    # Branching history
    stack.redo() # v1
    stack.push(Path("v1_branch.pdf")) # Overwrite v2
    assert stack.current_state == Path("v1_branch.pdf")
    assert not stack.can_redo
    
    stack.undo()
    assert stack.current_state == Path("v1.pdf")
