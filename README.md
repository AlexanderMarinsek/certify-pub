# Certify

On-chain credentials for node runners - a project for Algorand France hackathon.

In addition to this repo, you might want to check out the [testnet deployment](https://certify-algorand.vercel.app/) and [slide deck](https://docs.google.com/presentation/d/1TDqm8NNFOITV3B9EiMyTiXJ8iR3VdNZQ/edit?usp=drive_link&ouid=104976776298600611318&rtpof=true&sd=true).

*Please note that the terms "node runner", "node operator", and "validator" are used interchangeably. We are clarifying the correct terminology with the Algorand Fundation.*



## Platform overview

### Introduction

Nodes form the backbone of blockchain technology. Their core tasks include relaying information, validating transactions, and storing data. Hence, nodes play a key role in the health of a blockchain and their performance can increase income in the case of consensus participation. 

### Problem statement

*Node operators* are often asked to provide certain guarantees about their nodes to potential clients, ranging from physical persons to large institutions. Node operators can ask an auditinc company to inspect and evaluate their nodes. The auditing companies that node operators comply with certain standards, such as [ISO/IEC 27001](https://en.wikipedia.org/wiki/ISO/IEC_27001), and issue certificates that attest this compliance. The node operator can then publicly display such certificates, for example, on their webpage.

*Clientes* usually select one or more node operators an array of different operators. The client has to put additional effor into finding the certificates of each node runner, before evaluating and comparing them. Moreover, these certificates could be issued by different auditing companies in their own format, making a level comparison harder for the client. Hence, selecting a node operator becomes a cumbersome task, consuming a significant amount of time and money.

Node opearators can be of *different sizes*, ranging from small private operators to large instutitional operators. The large cost of certification by auditing companies might prove to be a large burden for the smaller operators, keeping them from getting certified. We estimate that such operators are prepared to pay a few in the range of several or tens of Dollars, based on our initial market research.

### Solution

The Certify platform makes blockchain infrastructure audits more accessible. On the one hand, Certify brings certification on-chain and makes it easy for anyone to retrieve certificate information. On the other hand, Certify provides affordable performance evaluation and certification for all node operators, including those that can not overcome the high cost burden of traditional audits.

#### On-chain certification

Certify enables traditional companies to issue their certificates on chain, making the certification process transparent and accessible to all. In addition, Certify aims to enable simple overviews of node operators and their certificates in order to save time for clients when searching for a node operator that will satisfy their needs.

#### Stress tests

Certify allows node operators to request stress tests on their infrastructure. The test allocates a given stake to the node under test and includes it in consensus participation, while trackign its performance. The resulting performance is written on-chain in the form of a certificate, issued by Certify. 



## Overview of the designed platform

The Certify platform has three main project components: smart contracts ([smart contract README](projects/certify-contracts/README.md)), the front-end ([front-end README](projects/certify-frontend/README.md)), and the stress test daemon ([daemon README](projects/certify-stress-test-daemon/README.md)). The three project parts can be found in the `projects` directory.


### Smart contracts

Smart contracts form the core of Certify, which features two contracts in the current implementation.


#### Certification board

The certification board is a central smart contract, deployed in a single instance. It exposes the certification functionality, allowing auditing companies to issue on-chain certificates. The certification board fetches and serves existing certificates to clients. Finally, the certification board can spawn stress tests on demand. The state machine and functionality of the certification board is described in the [cert_board_specs](projects/certify-contracts/docs/cert_board_specs.md).


#### Stress test

The stress test is a smart contract that is spawned from the certification board once a stress test is requestes by a node operator. The stress test runs for a limited time, as indicated by the node operator. The stress test receives temporary funding from the certification board. The funded amount is used for staking during the duration of the test in order to collect the perfromance of the node operator. The state machine and functionality of the stress test is described in the [stress_testing_specs](projects/certify-contracts/docs/stress_testing_specs.md).


### Front-end 

The Certify fron-end is an abstraction layer between the on-chain smart contract core and the node operator or client. This is one in order to simplify certification issuance and review. Moreover, the front-end allows for scaling through additional features, such as sorting, recommendation, and analytics. A demo of the user interface can be found on (TestNet): [https://certify-algorand.vercel.app/](https://certify-algorand.vercel.app/) 


### Stress test daemon

The stress test daemon is run on the node under test in order to periodically request perfromance logging. To do this, the daemon periodically requests the stress test smart contract to check whether the tested node proposed the last block.


## Usage instructions

### Setting up the local environment

#### Prerequisites
The project was developed using AlgoKit. Before starting, ensure you have AlgoKit and all of its dependencies installed.
You can find an installation guide [here](https://developer.algorand.org/docs/get-started/algokit/).
AlgoKit version 2.4.1 or higher is required. You can check your version by running `algokit --version`.

#### Getting Started
This section provides instructions for deploying the platform on AlgoKit localnet and locally running the UI.

1) Clone this repository: `git clone https://github.com/IgoProtect/certify`
2) Navigate to the `ROOT` project directory: `cd certify`
3) Install all dependencies: `algokit project bootstrap all`
4) Start localnet: `algokit localnet start`
5) Deploy a new instance of the platform: `algokit project deploy localnet`
6) Navigate to `certify-frontend` directory `cd projects/certify-frontend` and start the UI by running `npm run dev`. You can access the UI at `http://localhost:5173/`.
7) Open Lora explorer at `https://lora.algokit.io/localnet` or via `algokit explore` to check if the right transactions are being created and smart contracts changed as intended.

For easier testing of the platform with multiple users that have different roles, it is recommended to create multiple accounts in `KMD`.
This can be done for example by going to https://lora.algokit.io/fund and selecting the option `Create and fund a new LocalNet account`, which will create and fund an account as part of `lora-dev` wallet.

#### Running on TestNet

Certify smart contracts are deployed on the TestNet and the user interface is available at: [https://certify-algorand.vercel.app/](https://certify-algorand.vercel.app/)

The procedures for issuing certificates and stress tests are the same as on the localnet. Note that requesting a stress test makes the deployed `cert_board` smart contract allocate part of its stake to the spawned `stress_test` for the duration of the test. The deployed `stress_test` has limited funding on the TestNet, so it can happen that all of its funds are occupied at a given time. This can be verified by checking the deployed `stress_test` smart contract, which has the ID `OLUWBJXZIOEPRHAWXSRU5NTSKI74VZFKOMO366C6ZN7X7TGPXFRKILIAHE` at the time of writing.


## Requesting a stress test

A stress test can be requested by the node operator by opening the Certify front-end and selecting the stress test service. After connecting their wallet, the node operator will be requested to enter the stress test setup parameters:
- Stake: amount of stake that is delegated (larger stake requires better node performance)
- Test duration: the duration of the stress test, i.e., staking (the longer, the more statistically relevant)
- Maximal duration: the maximal duration that the entire test can take, including the testing and the initialization.

Next, the node operator should copy the displayed stress test contract ID and the mnemonic of their (hot) wallet to the daemon's config file ([daemon.config](projects/certify-stress-test-daemon/daemon.config)) and rung the daemon. RUntime information can be tracked through the daemon's log file ([daemon.log](projects/certify-stress-test-daemon/daemon.log)). Note that, util the contract is live, the daemon will report that the transaction was not successful. This is also the case in LocalNet until the block round progresses by at least one.

Afterwards, the node operator is requested to generate a participation key for the stress test smart contract. This will allow the funds of the stress test smart contract to get staked through the node under test. The node operator can generate these keys using `algokit goal` and, once generated, submit the key required key parameters through the front-end. The stress test begins by submitting these partkey parameters. The page will now display the test's progress, updated each ten seconds.


## Issuing a certificate

An auditing company can issue a certificate for te desired node operator by going to the "attest" service. There, the auditing company can enter the node operator's (validator's) address and the certificate contents. In the current implementation, this is a free-form submition. We foresee standard-based templates in the update, which will provide better unity and convenience to the auditing company.


## Certificate verification

Any visitor can verify the certificates of a node operator by going to the "verify" service and entering the node operator's (validator's) address. For now, this functionality displays the finished stress tests, which requires an additional "ID" field.


## Contributors

This product was developed as part of the Algorand Foundation's [France hackathon](https://algorand.co/hackathon-france), submitted to the decentralized identity track.

The project authors are:
- [Uroš Hudomalj](https://www.linkedin.com/in/uros-hudomalj/) (@[uhudo](https://github.com/uhudo)): [smart contracts](/projects/certify-contracts/README.md)
- [Alexander Marinšek](https://be.linkedin.com/in/alexander-marinsek) (@[AlexanderMarinsek](https://github.com/AlexanderMarinsek)): [daemon](/projects/certify-daemon/README.md)
- [Jalish Buktawar](https://www.linkedin.com/in/jalishbuktawar/) (@[zenithexe](https://github.com/zenithexe/)): [UI](/projects/certify-frontend/README.md)


## Outlook


