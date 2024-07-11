**Simple CRM system**

**Architecture**

![image](https://github.com/AmiraGamal1/crm-project/assets/40859881/6b88e1a1-39d8-4ff1-b26c-2f18d2030952)

**User Stories**

User Story: Managing Customer Information
As an administrator of the CRM system website, I want to be able to perform the following actions:
1. Create Editor Users:
○ As an administrator, I should be able to create new editor users. These editor users
will have permission to manage customer information.
○ The editor users can add new customer records, update existing customer details, and
delete customer records.
2. Search and List Customers:
○ Both administrators and editor users should be able to search for customers based on
various criteria (e.g., name, email, phone number).
○ The system should provide a list view of customer records, displaying relevant
information such as name, contact details, and other relevant data.
3. Supervisor Role:
○ Additionally, the system administration should allow the creation of Supervisor users.
○ Supervisor users will have read-only access to customer information. They can search
and view customer records but cannot modify them.
Acceptance Criteria:
● The administrator can create editor and supervisor users with appropriate permissions.
● Editor users can perform CRUD (Create, Read, Update, Delete) operations on customer
records.
● Both administrators and editor users can search for customers and view relevant details.
● Supervisor users can only search for and view customer information without modification
rights.
