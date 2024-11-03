# import algosdk
from fastapi import HTTPException
from algosdk.error import AlgodHTTPError
from algosdk.v2client import algod
from algosdk.transaction import ApplicationNoOpTxn
# from algosdk import account, mnemonic

# Algod client setup
ALGOD_TOKEN = "Algod Token"
ALGOD_ADDRESS = "https://testnet-algorand.api.purestake.io/ps2"  # Testnet URL
client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# Load Algorand account
def get_account():
    private_key = "Private Key"
    account_address = "Algorand Address"
    return private_key, account_address

# Function to initiate escrow hold in the smart contract
def initiate_escrow_hold(order_id: int, amount: float):
    private_key, sender_address = get_account()
    
    # deployed smart contract ID
    app_id = "Smart Contract App ID"
    
    # Create a transaction to call the smart contract for an escrow hold
    params = client.suggested_params()
    txn = ApplicationNoOpTxn(sender_address, params, app_id, app_args=["hold_funds", order_id, amount])
    
    # Sign and send transaction
    signed_txn = txn.sign(private_key)
    tx_id = client.send_transaction(signed_txn)
    return tx_id

# # Function to release funds on delivery confirmation
# def release_escrow(order_id: int):
#     private_key, sender_address = get_account()
    
#     # deployed smart contract ID
#     app_id = "Smart Contract App ID"
    
#     # Transaction to release funds
#     params = client.suggested_params()
#     txn = ApplicationNoOpTxn(sender_address, params, app_id, app_args=["release_funds", order_id])
    
#     # Sign and send transaction
#     signed_txn = txn.sign(private_key)
#     tx_id = client.send_transaction(signed_txn)
#     return tx_id

def release_escrow(order_id: int) -> str:
    try:
        # Get account credentials
        private_key, sender_address = get_account()
        
        # Deployed smart contract ID
        app_id = "Smart Contract App ID"
        
        # Prepare the transaction
        params = client.suggested_params()
        txn = ApplicationNoOpTxn(
            sender=sender_address, 
            sp=params, 
            index=app_id, 
            app_args=["release_funds", order_id]  # Ensure order_id format is correct
        )
        
        # Sign and send the transaction
        signed_txn = txn.sign(private_key)
        tx_id = client.send_transaction(signed_txn)

        # Optional: You could wait for confirmation if needed
        # transaction_response = client.pending_transaction_info(tx_id)
        
        return tx_id  # Return transaction ID for reference

    except AlgodHTTPError as e:
        print(f"Algorand client error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to release escrow funds: {str(e)}")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while releasing escrow funds.")