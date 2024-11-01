
## Interpretation


### Validator flow

In the current implementation, the validator:
1. Opens the app, gets informed about the procedure, and decides for how long to stake.
2. (Context switch #1) Creates a hot wallet
3. Generates the partkey, enetring their address as a command argument.
4. (Context switch #2) Goes back to the app, enters their address and the generated partkey parameters.
5. Signs one or more transactions.
6. Copies the generated stress test contract ID
7. (Context switch #3) Downloads the daemon
8. Amends the daemon's config, entering the aforementioned ID, public address, etc.
9. Runs the daemon


### The daemon

Repeatedly issues a call to the cert board's `stress_record` function, using the validator's address



## Remarks


### Removing initial dead period

As described above, the staking could happen already before the validator runs the daemon.
This would reduce the observation period. 
Depending on the contract's design, it could also impact the statistics if the start and end round are used for determining performance instead of the the rounds when the record funciton was called.
Instead, the validator could first enter their address into the daemon's config and run the daemon. 
Only then would the validator go into the app and spawn a contract.
Two potential solutions are:
- The daemon is initially in a "watch state", checking the live contracts to see if the validator's address is among them. If yes, it shifts into an active state and starts calling the record function. 
... Drawbacks: the cert board would have to maintain a list of IDs of live stress tests. Alternatively, the daemon could sniff each block for matching against the validator's address and the corresponding Certify transaction.
- The daemon calls the record function on the cert board with only the validator's address, which fails if there is no stress test contract associated with that validator.
... Drawbacks: 


### Auto-generate partkeys

Avoid manual interaction of the validator by having the daemon auto-generate partkeys.
Could simplify the validator effort to just:
0. (Install Python)
1. Download a script/program
2. Run the script/program and enter public address in a prompt
We can reuse already developed code for this step.


### Simplifying validator flow (summary of the above remarks)

#### Option 1

The validator
1. Opens the app, gets informed
2. (Context switch #1) Downloads the daemon 
3. Generates a hot wallet
4. Runs the daemon and enters the public address in a prompt
5. (Context switch #2) Goes back to the app to fill in the contract terms
6. Signs one or more transactions

#### Option 2

The validator
1. Opens the app, gets informed
2. Fills in the contract terms
3. Signs one or more transactions
4. (Context switch #1) Downloads the daemon
5. Generats hot wallet
6. Runs the daemon and enters the public address and mnemonic in a prompt


### Automating the vlaidator

The validator could automatically end the contract when finished, generate keys, etc. by knowing what state the contract is in.
If nothing else, This can be done based on issuing the record command and observing the returned errors. For example:
- `assert // Cannot be called from other state than LIVE.		<-- Error`
- `assert // There is no new produced block to record.		<-- Error`


### Stress testing for 2 blocks less than duration

The duration is 2 blocks less than the actual duration (it seems the start and end blocks are not counted):
```
 cnt_produced_blocks: 40
 cnt_total_stake_sum: 41
 duration: 42
 duration_max: 101
 last_block: 2484
 owner_address: <src.StressTestingClient.ByteReader object at 0x7f1cd5e2c3e0>
 round_created: 2442
 round_end: 2485
 round_end_max: 2543
 round_ended: 100000000
 round_start: 2444
 stake: 1000000
 state: <src.StressTestingClient.ByteReader object at 0x7f1cd4cb2c00>
 total_stake_sum: 1722001722
 user_address: <src.StressTestingClient.ByteReader object at 0x7f1cd5cbb2f0>
```

## To-do

### Readme infographic

Make an infographic for the validator flow (according to the steps mentioned in the overview).
