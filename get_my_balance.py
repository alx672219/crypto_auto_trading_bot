import pybithumb


crypto = "Enter the name of your cryptocurrency (ex: BTC, ETH, etc...)"
connect_key = "Enter your connect key"
secret_key =  "Enter your secret key"


# Log into my Bithumb account. 
bithumb = pybithumb.Bithumb(connect_key, secret_key)

# get_balance returns (total amount of Ethereum, Ethereum that are being traded, total amount of Korean won, Korean won that are being traded).
print(bithumb.get_balance(crypto))