[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Pu7X6J-p)
# Copy your title from the Project Proposal and paste it here. Update if necesssary.
## Executive Summary
Copy your text from the Project Proposal and paste it here. Make any changes here.

## Statement of Scope
Copy your text from the Project Proposal and paste it here. Make any necessary updates.

## Inputs, Processes, Outputs
Add a discussion about the inputs, processes, and outputs of your program. See the instructions for more information about this section. No code is shown here.

As an example, if I have a mountain bike shopping program, I might include the following steps (among many, many others):

### Step 1: Variable Declaration
**Description:** This step is where I create several lists with data including product names, product prices, product categories, and product descriptions for bicycle parts. I also create a running total.

**Inputs:** No inputs for this step.

**Processes:** All the lists with data are created. The running total is set to zero.

**Outputs:** No outputs for this step.

### Step 2: Welcome Message
**Description:** I welcome the user to my program. They are given a description of the purpose of my program.

**Inputs:** None for this step

**Processes:** A few console writelines that display my messages. Since my program is a shopping app for mountain bikes, I created an ASCII art of a bike. This is displayed here.

**Outputs:** None for this step.

### Step 3: Menu Selection
**Description:** The user is presented a menu with the following options: 1) View Drivetrain parts, 2) View Cockpit parts, 3) View Wheel parts, 4) View Brake Systems, 5) View Pedals, 6) Review Shopping Cart, 7) Quit.

**Inputs:** The user types in a number corresponding to their menu selection.

**Processes:** I use a switch-case to determine which menu item is selected. The switch-case evaluates a number. Each case has an associated function that processes the selection. For example, if 5 is selected to view pedals, then the function viewPedals() is called.

**Outputs:** Takes the user to one of the steps below. For Drivetrain, go to Step 4. For Cockpit, go to Step 7. For Wheel parts, go to step 9. For Brake Systems, see Step 11. For Pedals, see Step 14. For Shopping Cart, see Step 17. For Quit, see Step 21.

Copy and paste the code above as many times as you have steps! Be sure to edit the above text and replace it with text for your program.

## Function Dictionary
A short description of the functions used in your program listed in a table. Each row represents a function. Be descriptive. An example is provided below.

| Function | Parameters | Purpose |
|:---|:---|:---|
| `addEmployee` | `string firstName`, `string lastName`, `int age`; auto generate `int employeeID` | This function creates a new employee in the system. The function is passed three attributes to create it including the frist name, last name, and age. The ID is automatically generated as a random number. |
| `removeEmployee` | `int employeeID` | This function is passed the employee's ID to remove the records from the program. |
| `updateEmployee` | `string firstName`, `string lastName`, `int age` | This updates the various values of an employee |
| `addProject` | `string title`, `string description`; auto generate `int projectID` | Creates a new project by passing in two arguments, the title and description. The ID is automatically generated. |
| `removeProject` | `int projectID` | A project is removed from the system using the project ID. |
| `updateProject` | `string title`, `string description` | Updates the values of the project by passing in arguments related to the title and description. |
