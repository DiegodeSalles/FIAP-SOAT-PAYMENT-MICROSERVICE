Feature: Payment Webhook
    As a system
    I want to receive payment updates from Mercado Pago
    So that I can update the payment status

    Scenario: Receive approved payment notification
        Given a payment exists with ID "pay_123" and status "pending"
        When I receive a webhook notification for "pay_123" with status "accredited"
        Then the payment status should be updated to "approved"
        And the response status code should be 200

    Scenario: Receive rejected payment notification
        Given a payment exists with ID "pay_456" and status "pending"
        When I receive a webhook notification for "pay_456" with status "rejected"
        Then the payment status should be updated to "rejected"

    Scenario: Receive notification for non-existent payment
        Given no payment exists with ID "pay_999"
        When I receive a webhook notification for "pay_999" with status "accredited"
        Then the response status code should be 404