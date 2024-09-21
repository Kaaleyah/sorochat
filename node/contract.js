import {
  Keypair,
  Contract,
  SorobanRpc,
  TransactionBuilder,
  Networks,
  BASE_FEE,
  nativeToScVal,
  Address,
} from "@stellar/stellar-sdk";

// Choose the Soroban-RPC server to use
const server = new SorobanRpc.Server(
  "https://soroban-testnet.stellar.org:443",
);

const contractID = "CATAE5FGYHBCGSM5YVV6RNKQW52RX3FVBF35IVIYHCUD7IYB6IZKPZUL";

const addressToCheck = "GAFYJA443OCBE2GAFOHMMYN3ELAK3KR7EER6ZF2MXCDRVCPZYGKXROVN";

async function getBalance() {
  const contract = new Contract(contractID);
  const address = Address.fromString(addressToCheck);

  console.log("Checking balance for address: " + address);

  const tx = new TransactionBuilder(await server.getAccount(address), {
    fee: BASE_FEE,
    networkPassphrase: Networks.TESTNET,
  })
    .addOperation(contract.call("get_balance", { address: nativeToScVal(addressToCheck) }))
    .setTimeout(30)
    .build();

  const result = await server.prepareTransaction(tx);
}

getBalance(addressToCheck).then((result) => {
  console.log(result);
})