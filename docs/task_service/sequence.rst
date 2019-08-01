Task Sequence of Operations
===========================

Below is a basic overview of a task's expected sequence of operations and its
states.
See the sequence diagram <link here> for a detailed specification of the
interaction between the Coordinator Service and a Task Service.

1) Receive initialize action from coordinator and move to pending state.
   Respond to coordinator with state set to pending.
   This is important since the coordinator will not send the start action until
   all tasks within the release are in pending state.

2) Receive start action from coordinator and move to running state.
   Respond to coordinator with state set to running.

3) (Optional) Update coordinator with current progress as the task does its
   work.

4) Complete processing and change state from running to staged

5) Update coordinator with current state.
   This is import since the coordinator will not send the publish action until
   all tasks within the release have sent a request with state set to staged.

6) Recieve publish from coordinator and run final actions to make data public
