import time

from stellar_sdk import Keypair, Network, SorobanServer, TransactionBuilder, scval
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.exceptions import PrepareTransactionException
from stellar_sdk.soroban_rpc import GetTransactionStatus, SendTransactionStatus

secret = "SAPPFGGLZRPDXW4K7LUR5GYU3GCG7EGHMJQ7VQ4SGFLDNN3A2UIU6MK6"
rpc_server_url = "https://soroban-testnet.stellar.org:443"
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

# Here we will use a deployed instance of the `increment` example contract.
contract_id = "CDOGJBJMRVVXW5K3UJ5BGVJ5RSQXQB4UFVQYVFOIARC2UYXSEPF4YAVR"
# The source account will be used to sign and send the transaction.
source_keypair = Keypair.from_secret(secret)
# Configure SorobanClient to use the `soroban-rpc` instance of your choosing.
soroban_server = SorobanServer(rpc_server_url)
# Transactions require a valid sequence number (which varies from one account to another).
# We fetch this sequence number from the RPC server.
source = soroban_server.load_account(source_keypair.public_key)

tx = (
    # The transaction begins as pretty standard. The source account, minimum fee,
    # and network passphrase are provided.
    TransactionBuilder(source, network_passphrase, base_fee=100)
    # This transaction will be valid for the next 30 seconds
    .set_timeout(30)
    # The invocation of the `increment` function of our contract is added to the transaction.
    .append_invoke_contract_function_op(
        contract_id=contract_id,
        function_name="increment",
        parameters=[scval.to_address(source_keypair.public_key), scval.to_uint32(5)],
    ).build()
)

print(f"builtTransaction: {tx.to_xdr()}")

try:
    # We use the RPC server to "prepare" the transaction. This simulating the
    # transaction, discovering the soroban data, and updating the
    # transaction to include that soroban data. If you know the soroban data ahead of
    # time, you could manually use `set_soroban_data` and skip this step.
    tx = soroban_server.prepare_transaction(tx)
except PrepareTransactionException as e:
    print(f"Prepare Transaction Failed: {e.simulate_transaction_response}")
    raise e

# Sign the transaction with the source account's keypair.
tx.sign(source_keypair)

# Let's see the base64-encoded XDR of the transaction we just built.
print(f"Signed prepared transaction XDR: {tx.to_xdr()}")

# Submit the transaction to the Soroban-RPC server. The RPC server will
# then submit the transaction into the network for us. Then we will have to
# wait, polling `get_transaction` until the transaction completes.
send_transaction_data = soroban_server.send_transaction(tx)
print(f"Sent transaction: {send_transaction_data}")
if send_transaction_data.status != SendTransactionStatus.PENDING:
    print(send_transaction_data.error_result_xdr)
    raise Exception("Send transaction failed")

while True:
    print("Waiting for transaction to be confirmed...")
    # Poll `get_transaction` until the status is not "NOT_FOUND"
    get_transaction_data = soroban_server.get_transaction(send_transaction_data.hash)
    if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
        break
    time.sleep(3)

print(f"getTransaction response: {get_transaction_data}")

if get_transaction_data.status == GetTransactionStatus.SUCCESS:
    # The transaction was successful, so we can extract the `result_meta_xdr`
    transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
        get_transaction_data.result_meta_xdr
    )
    result = transaction_meta.v3.soroban_meta.return_value
    # Find the return value from the contract and return it
    print(f"Transaction result: {scval.from_uint32(result)}")
else:
    # The transaction failed, so we can extract the `result_xdr`
    print(f"Transaction failed: {get_transaction_data.result_xdr}")
    raise Exception("Transaction failed")