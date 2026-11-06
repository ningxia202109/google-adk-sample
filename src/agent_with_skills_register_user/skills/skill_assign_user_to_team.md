---
name: assign user to team
description: Specialized skill for assigning existing users to teams based on compatibility.
tools: get_users, get_teams, add_user_to_team
---

# Assign User to Team Skill
This skill allows the agent to manage team memberships.

## Guidance 
To assign a user to a team:
1. Search for the user to get their ID using `get_users`.
2. List available teams using `get_teams`.
3. Use `add_user_to_team` to perform the assignment.
4. If the assignment fails (e.g., due to habit mismatch), inform the user about the conflict.
5. Once the assignment is completed or fails decisively, call `complete_skill` to return to the base state.

## Examples
- "Add Alice to the 'Avengers' team."
- "Move user 456 to the 'Backend' team."

## guardrails
- Verify user existence before attempting assignment.
- Verify team existence before attempting assignment.
- ALWAYS call `complete_skill` when the team-related task is done.

## agent gavernances
- Respect team size limits (if any).
- Maintain audit logs of team changes.
