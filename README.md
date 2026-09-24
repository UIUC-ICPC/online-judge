# icpc online judge

- Databases 
    - design schemas to handle
    - users table
    - contest table
    - submissions table 
    - maybe think about self hosting problems table 
- Judge worker
    - Multithreading to handle simultaneous executions
    - Sandbox execution of submitted code
- Control server
    - Queue for submissions
    - Load balancing between judge workers
- Frontend
    - Users can sign up for accounts, submit problems, view contest standings, leaderboard with penalty
    - Figure out latex rendering 
    - Interact with backend 
- Backend
    - Pull problems from polygon 

