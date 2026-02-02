---
name: skill_register_user
description: Specialized skill for registering and managing users in the system.
---

# Register User Skill
This skill allows the agent to onboard new users to the system.

## Guidance 
To solve a user registration task:
1. First, check if a user with the given details already exists using `get_users`.
2. If not, use `create_user` to register the new user.
3. If an update is needed to an existing user, use `update_user`.
4. Once the registration or update is confirmed, call `complete_skill` to return to the base state.

## Examples
- "Register a new user named Alice with email alice@example.com and habits 'coding', 'gaming'."
- "Update user 123's email to new_alice@example.com."

## guardrails
- Do NOT create duplicate users if you can find them by email.
- ALWAYS confirm with the user after successful registration.
- ALWAYS call `complete_skill` when the user-related task is done.

## agent gavernances
- Follow data privacy standards.
- Ensure email formats are valid.
