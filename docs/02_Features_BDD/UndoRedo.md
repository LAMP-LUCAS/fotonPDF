# Feature: Undo/Redo System

As a user editing a document
I want to undo and redo my annotations
So that I can correct mistakes without frustration

```gherkin
Feature: Undo/Redo System
  Scenario: Undo last highlight
    Given I have applied a highlight to "Section 1.1"
    When I press "Ctrl+Z"
    Then the highlight on "Section 1.1" should disappear
    And the document state should revert to the previous version

  Scenario: Redo undone highlight
    Given I have just undone a highlight on "Section 1.1"
    When I press "Ctrl+Shift+Z"
    Then the highlight on "Section 1.1" should reappear

  Scenario: Branching history
    Given I undid a highlight
    When I apply a new highlight on "Section 2.0"
    Then the previously undone highlight cannot be redone
    And the new history branch contains "Section 2.0"
```
