Feature: Delete an account
  Test the API call to delete an account and all its related data from the database.

  Scenario: Successful account deletion
    Given an authenticated user
    When the user's account is deleted
    Then the request will be successful
    And the membership is removed from stripe

