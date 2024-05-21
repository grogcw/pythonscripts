#
#	This script reverse-engineers the Truenas password encryption system.
#
#	You can get the salt by hex editing your "pwenc_secret" and the encrypted password from the DB. (SQLite)
#	Saving your configuration with salt gives you everything.
#
#	This scirpt is for educational use only, don't use this to get access you would'nt normally. Be responsible.
#

import sys	# Importing the sys module to access command-line arguments

# Check if the major version of Python is 3
if sys.version_info[0] != 3:
	print("This script requires Python 3.")
	sys.exit(1)

import base64	# Importing the base64 module to handle base64 encoding/decoding

# pip install pycryptodome
from Crypto.Cipher import AES	# Importing the AES cipher from the PyCryptodome library
from Crypto.Util import Counter	# Importing the Counter module for creating counters used in CTR mode


# Checking if the correct number of command-line arguments are provided
if len(sys.argv) != 3:
	print("Usage: python truenas_pw_decode.py <pwenc_secret_as_hex> <base64_encoded_password>")
	sys.exit(1)

# Assigning command-line arguments to variables
hex_string = sys.argv[1]		# First argument: hex-encoded secret key from pwenc_secret
encrypted_string = sys.argv[2]	# Second argument: base64-encoded encrypted password from db

# Defining constants
PWENC_BLOCK_SIZE = 32	# Block size for the encryption (not used in this script)
PWENC_PADDING = b'{'	# Padding character used during encryption

# Converting the hex-encoded secret key to bytes
SECRET_KEY = bytes.fromhex(hex_string)

def decrypt(encrypted, _raise=False):
	if not encrypted:
		return ''		# Return an empty string if the input is empty

	try:
		# Decode the base64-encoded encrypted string
		encrypted = base64.b64decode(encrypted)

		# Extract the nonce (first 8 bytes) and the actual encrypted message
		nonce = encrypted[:8]
		encrypted = encrypted[8:]

		# Create a new AES cipher object in CTR mode using the nonce
		cipher = AES.new(SECRET_KEY, AES.MODE_CTR, counter=Counter.new(64, prefix=nonce))

		# Decrypt the encrypted message and remove padding
		decrypted = cipher.decrypt(encrypted).rstrip(PWENC_PADDING)

		# Return the decrypted string as a UTF-8 decoded string
		return decrypted.decode('utf8')
	except Exception as e:
		if _raise:
			raise		# Raise the exception if _raise is True
		print("Error:", e)	# Print the error message if decryption fails
		return ''			# Return an empty string if decryption fails

# Decrypt the provided encrypted string
decrypted_string = decrypt(encrypted_string)

# Print the decrypted string
print('Decrypted:', decrypted_string)
