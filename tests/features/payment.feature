Feature: Payment Management
    As a user
    I want to generate payments and check their status
    So that I can pay for my orders

    Scenario: Create a new payment
        Given I have a valid order with ID "order_123" and amount 100.0
        When I request to create a payment
        Then the payment should be created successfully
        And the payment status should be "pending"
        And the response should contain a QR code payload

    Scenario: Get payment status
        Given a payment exists with ID "payment_abc" and status "pending"
        When I request the status of the payment "payment_abc"
        Then the returned status should be "pending"
