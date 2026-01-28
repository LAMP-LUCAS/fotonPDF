# Feature: Highlight Persistence

As a user reviewing a document
I want to permanently highlight important text
So that I can find it easily later

```gherkin
Feature: Highlight Persistence
  Scenario: Highlighting text with default yellow
    Given I have a PDF document open
    And I have selected the text "Project Specifications" on page 1
    When I right-click and choose "Highlight"
    Then the text should be highlighted in yellow
    And the annotation should be saved to the file
    And the change should be persisted after reloading

  Scenario: Custom color highlight
    Given I have selected "Structure Analysis"
    And I have chosen "Red" from the color palette
    When I trigger the highlight action
    Then the text should be highlighted in red (#FF0000)
```
