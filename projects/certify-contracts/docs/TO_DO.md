# Things to discuss on design and its specs

- revoke of stress test and pro-rata refund by us at anytime. This is if we see the user is misbehaving and attacking the protocol.

- we should charge: expected APY (i.e. ALGO for that period)

- consider it takes 320 rounds for stake to be registered. So counting the start for assessment should be delayed.
- incentivize user to participate for 320 rounds after stress test end in order not to endanger the network upon exit due to 320 round delay.

- refund payment between actual end and max end (on pro-rata basis).
- refund payment in case platform manager breaks the test prior to it running out (on pro-rata basis).
- refund payment based on produced rewards.

- correct when reading get*ex* to check also app creator matches this contract!
