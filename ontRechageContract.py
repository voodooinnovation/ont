OntCversion = '2.0.0'
TAG='cttlife-xiyou'
from boa.interop.Ontology.Native import Invoke
from boa.builtins import ToScriptHash, state
from boa.interop.System.Runtime import CheckWitness, Notify
from boa.interop.Ontology.Runtime import Base58ToAddress
from boa.interop.System.ExecutionEngine import GetExecutingScriptHash
from boa.interop.System.Storage import GetContext, Get, Put, Delete

"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/Utils.py
"""


def Revert():
    """
    Revert the transaction. The opcodes of this function is `09f7f6f5f4f3f2f1f000f0`,
    but it will be changed to `ffffffffffffffffffffff` since opcode THROW doesn't
    work, so, revert by calling unused opcode.
    """
    raise Exception(0xF1F1F2F2F3F3F4F4)


"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeCheck.py
"""


def Require(condition):
    """
	If condition is not satisfied, return false
	:param condition: required condition
	:return: True or false
	"""
    if not condition:
        Revert()
    return True


def RequireScriptHash(key):
    """
    Checks the bytearray parameter is script hash or not. Script Hash
    length should be equal to 20.
    :param key: bytearray parameter to check script hash format.
    :return: True if script hash or revert the transaction.
    """
    Require(len(key) == 20)
    return True


def RequireWitness(witness):
    """
	Checks the transaction sender is equal to the witness. If not
	satisfying, revert the transaction.
	:param witness: required transaction sender
	:return: True if transaction sender or revert the transaction.
	"""
    Require(CheckWitness(witness))
    return True


"""
https://github.com/ONT-Avocados/python-template/blob/master/libs/SafeMath.py
"""


def Add(a, b):
    """
	Adds two numbers, throws on overflow.
	"""
    c = a + b
    Require(c >= a)
    return c


def Sub(a, b):
    """
    Substracts two numbers, throws on overflow (i.e. if subtrahend is greater than minuend).
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    Require(a >= b)
    return a-b


def Mul(a, b):
    """
    Multiplies two numbers, throws on overflow.
    :param a: operand a
    :param b: operand b
    :return: a - b if a - b > 0 or revert the transaction.
    """
    if a == 0:
        return 0
    c = a * b
    Require(c / a == b)
    return c


def Div(a, b):
    """
    Integer division of two numbers, truncating the quotient.
    """
    Require(b > 0)
    c = a / b
    return c


# ONG Big endian Script Hash: 0x0200000000000000000000000000000000000000
OngContract = Base58ToAddress("AFmseVrdL9f9oyCzZefL9tG6UbvhfRZMHJ")
# OngContract = bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02')
Admin = Base58ToAddress('AGGD2KuEAmRnivvNY43d6L9NfXX79P3BsJ')
ctx = GetContext()

selfContractAddress = GetExecutingScriptHash()

BALANCE = 'b'
RECHARGE = 'r'


def Main(operation, args):
	if operation == "deposit":
		openId = args[0]
		fromAcct = args[1]
		amount = args[2]
		return deposit(openId, fromAcct, amount)

	if operation == "totalBalance":
		return totalBalance()

	if operation == 'getBalance':
		fromAcct = args[0]

		return getBalance(fromAcct)

	if operation == 'rechargeAmount':
		fromAcct = args[0]

		return rechargeAmount(fromAcct)

	if operation == 'innerRecharge':
		addrAcct = args[0]
		amount = args[1]

		return innerRecharge(addrAcct, amount)

	if operation == 'innerConsume':
		addrAcct = args[0]
		amount = args[1]

		return innerConsume(addrAcct, amount)

	if operation == 'innerWithdraw':
		addrAcct = args[0]
		amount = args[1]

		return innerWithdraw(addrAcct, amount)

	if operation == 'forceWithdraw':
		addrAcct = args[0]
		amount = args[1]

		return forceWithdraw(addrAcct, amount)

	if operation == 'signIn':
		addrAcct = args[0]
		amount = args[1]

		return signIn(addrAcct, amount)

	return False

# 充值
def deposit(openId, fromAcct, amount):
	# entryHash = GetEntryScriptHash()
	# callerHash = GetCallingScriptHash()
	RequireWitness(fromAcct)
	if amount <= 0:
		return False
	param = state(fromAcct, selfContractAddress, amount)
	res = Invoke(0, OngContract, 'transfer', [param])

	if res and res == b'\x01':
		Notify(['111_deposit', selfContractAddress, openId, fromAcct, amount])
		Notify('transfer Ong succeed')
		balanceKey = concatkey(BALANCE, fromAcct)
		rechargeKey = concatkey(RECHARGE, fromAcct)
		balance = Get(ctx, balanceKey)
		Put(ctx, balanceKey, Add(balance, amount))
		regBalance = Get(ctx, rechargeKey)
		Put(ctx, rechargeKey, Add(regBalance, amount))
		return True
	else:
		Notify('transfer Ong failed')
		return False

# 查询合约的余额
def totalBalance():
	param = state(selfContractAddress)
	res = Invoke(0, OngContract, 'balanceOf', param)

	return res

# 账户的余额
def getBalance(fromAcct):
	balanceKey = concatkey(BALANCE, fromAcct)
	balance = Get(ctx, balanceKey)
	return balance

# 累计的充值
def rechargeAmount(fromAcct):
	rechargeKey = concatkey(RECHARGE, fromAcct)
	regBalance = Get(ctx, rechargeKey)
	return regBalance

# innerRecharge
def innerRecharge(addrAcct, amount):
	RequireWitness(Admin)
	balanceKey = concatkey(BALANCE, addrAcct)
	balance = Get(ctx, balanceKey)

	_amount = Add(balance, amount)
	Put(ctx, balanceKey, _amount)
	return _amount

# innerConsume
def innerConsume(addrAcct, amount):
	RequireWitness(Admin)
	balanceKey = concatkey(BALANCE, addrAcct)
	balance = Get(ctx, balanceKey)

	if balance < amount:
		return False

	_amount = Sub(balance, amount)
	Put(ctx, balanceKey, _amount)

	return _amount

# innerWithdraw
def innerWithdraw(toAcct, amount):
	RequireWitness(Admin)
	balanceKey = concatkey(BALANCE, toAcct)
	balance = Get(ctx, balanceKey)

	if balance < amount:
		return False

	_amount = Sub(balance, amount)
	Put(ctx, balanceKey, _amount)

	param = state(selfContractAddress, toAcct, amount)
	res = Invoke(0, OngContract, 'transfer', [param])
	if res and res == b'\x01':
		return amount
	else:
		Notify('inner withdraw operation failed')
		return False


# forceWithdraw
def forceWithdraw(toAcct, amount):
	RequireWitness(Admin)
	balanceKey = concatkey(BALANCE, toAcct)
	balance = Get(ctx, balanceKey)

	if balance < amount:
		_amount = 0
	else:
		_amount = Sub(balance, amount)

	Put(ctx, balanceKey, _amount)

	param = state(selfContractAddress, toAcct, amount)
	res = Invoke(0, OngContract, 'transfer', [param])
	if res and res == b'\x01':
		return amount
	else:
		Notify('force withdraw operation failed')
		return False

def signIn(fromAcct, secret):
	RequireWitness(fromAcct)
	return secret

def concatkey(str1, str2):
    return concat(concat(str1, '_'), str2)
