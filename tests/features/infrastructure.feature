Feature: Infrastructure Components
    As a developer
    I want to ensure my adapters work correctly
    So that the application can communicate with external services

    Scenario: Generate QR Code via Mercado Pago Provider
        Given I have the Mercado Pago Provider configured
        When I request a QR Code for order "order_123" with amount 50.00
        Then the provider should call the Mercado Pago API
        And return the correct QR data

    Scenario: Create payment in Mongo Repository
        Given I have the Mongo Repository configured
        When I save a payment with ID "pay_123"
        Then the repository should insert the document into the database