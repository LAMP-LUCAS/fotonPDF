# Feature: Search Result Highlight

As a user searching for specific terms
I want visual cues when navigating to results
So that I can immediately spot the relevant text on the page

```gherkin
Feature: Search Result Highlight
  Scenario: Navigating to a search result
    Given I have searched for "Specifications"
    When I click on the first result in the Search Panel
    Then the viewer should scroll to the corresponding page
    And the word "Specifications" should pulse in yellow
    And the highlight should fade out after 2 seconds
```
