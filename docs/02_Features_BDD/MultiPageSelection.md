# Feature: Multi-Page Text Selection

As a user selecting large blocks of text
I want the selection to span across page boundaries
So that I can copy content that flows from one page to another

```gherkin
Feature: Multi-Page Text Selection
  Scenario: Continuous selection across pages
    Given I start selecting text at the bottom of Page 1
    When I drag the cursor down to Page 2
    Then the selection should expand seamlessly to include text on Page 2
    And the status bar should reflect the total number of selected words
```
