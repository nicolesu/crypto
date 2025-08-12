// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/*
    The ERC-20 NatSpec for this contract was derived from
    * https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/IERC20.sol
    * https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/token/ERC20/ERC20.sol
*/

/**
 * @dev Interface of the ERC-20 standard as defined in the ERC, with deposit
 * and withdraw functions added for "wrapped ether"-like functionality.
 */
abstract contract ERC20Interface {
    function totalSupply() public view virtual returns (uint256);
    function balanceOf(address _owner) public view virtual returns (uint256);
    function transfer(address _to, uint256 _value) public virtual returns (bool);
    function transferFrom(address _from, address _to, uint256 _value) public virtual returns (bool);
    function approve(address _spender, uint256 _value) public virtual returns (bool);
    function allowance(address _owner, address _spender) public view virtual returns (uint256);

    function deposit() public payable virtual;
    function withdraw(uint256 _value) public virtual returns (bool);

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
}

/**
 * @dev Implementation of the {ERC20Interface} interface.
 */
contract MyToken is ERC20Interface {
    // Mapping of account address to current balance
    mapping(address => uint256) _accountBalances;

    // Mapping of account owner to accounts allowed to withdraw specified amounts
    mapping(address => mapping(address => uint256)) _approvals;

    // Current total supply of the token across all token holders
    uint256 private _totalSupply = 0;

    /**
     * @dev Returns the name of the token.
     */
    string public constant name = "ts885"; // TODO CHANGE THIS!

    /**
     * @dev Returns the symbol of the token, usually a shorter version of the
     * name.
     */
    string public constant symbol = "ts885"; // TODO: You can change this, too

    /**
     * @dev Returns the number of decimals used to get its user representation.
     * For example, if `decimals` equals `2`, a balance of `505` tokens should
     * be displayed to a user as `5.05` (`505 / 10 ** 2`).
     *
     * Tokens usually opt for a value of 18, imitating the relationship between
     * Ether and Wei. This is the default value returned by this function, unless
     * it's overridden.
     *
     * NOTE: This information is only used for _display_ purposes: it in
     * no way affects any of the arithmetic of the contract.
     */
    uint8 public constant decimals = 18;

    /**
     * @dev Deposits ETH to the contract which, in return, mints tokens and
     * sends them to the user.
     */
    function deposit() public payable virtual override {
        uint256 tokensToCredit = msg.value / 1000;
        _accountBalances[msg.sender] += tokensToCredit;
        _totalSupply += tokensToCredit;

        uint256 refundAmount = msg.value - (tokensToCredit * 1000);
        if (refundAmount != 0) {
            // Send remaining ETH back to the sender
            payable(msg.sender).transfer(refundAmount);
        }
        // Emit a Transfer log, as per the ERC-20 spec, describing how tokens are minted
        emit Transfer(address(0x0), msg.sender, tokensToCredit);
    }

    /**
     * @dev Burns _numTokens_ of the sender's tokens to the zero address and
     * then sends `numTokens * 1000` ETH back to the user.
     * @return success A boolean value indicating success
     */
    function withdraw(uint256 numTokens) public virtual override returns (bool success) {
        // Placeholder for (1)
        // TODO: Complete this function. See the `transferFrom` function for
        // examples of how to use `require` to revert a transaction if a
        // boolean statement is false.
        // 1. Check that the user's balance is sufficient (otherwise, revert)
        // 2. Adjust data structures appropriately
        // 3. Send appropriate amount of Ether from contract's reserves (revert
        //    if send fails)
        // 4. Emit a {Transfer} event with `to` set to the zero address 0x0 (this
        //    represents "burning" tokens as per the ERC-20 spec)
        // 5. Return true. (You'll never need to return false, since the contract
        //    will revert the transaction in the above failure scenarios.)
        
        require(_accountBalances[msg.sender] >= numTokens, "Insufficient balance");
        _accountBalances[msg.sender] -= numTokens;
        _totalSupply -= numTokens;
        uint256 ethToSend = numTokens * 1000;
        require(address(this).balance >= ethToSend, "Insufficient contract balance");
        payable(msg.sender).transfer(ethToSend);
        emit Transfer(msg.sender, address(0x0), numTokens);
        return true;
    }

    /**
     * @dev Returns the value of tokens in existence.
     * @return supply Number of tokens
     */
    function totalSupply() public view virtual override returns (uint256 supply) {
        return _totalSupply;
    }

    /**
     * @dev Returns the value of tokens owned by `_owner`.
     * @param _owner Address to check
     * @return balance Balance of _owner in tokens
     */
    function balanceOf(address _owner) public view virtual override returns (uint256 balance) {
        return _accountBalances[_owner];
    }

    /**
     * @dev Moves a `value` amount of tokens from the caller's account to `to`.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     *
     * @return success A boolean value indicating success
     */
    function transfer(address _to, uint256 _value) public virtual override returns (bool success) {
        // Check that the sender owns enough tokens
        require(_accountBalances[msg.sender] >= _value, "Insufficient balance");

        _accountBalances[msg.sender] -= _value;
        _accountBalances[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    /**
     * @dev Moves a `value` amount of tokens from `from` to `to` using the
     * allowance mechanism. `value` is then deducted from the caller's
     * allowance.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits a {Transfer} event.
     *
     * @return success A boolean value indicating success
     */
    function transferFrom(address _from, address _to, uint256 _value) public virtual override returns (bool success) {
        // Check that the sender is approved to withdraw and the origin account has enough tokens
        require(_approvals[_from][msg.sender] >= _value, "Insufficient allowance");
        require(_accountBalances[_from] >= _value, "Insufficient balance");

        _approvals[_from][msg.sender] -= _value;
        _accountBalances[_from] -= _value;
        _accountBalances[_to] += _value;
        emit Transfer(_from, _to, _value);
        return true;
    }

    /**
     * @dev Sets a `value` amount of tokens as the allowance of `spender` over the
     * caller's tokens.
     *
     * Returns a boolean value indicating whether the operation succeeded.
     *
     * Emits an {Approval} event.
     */
    function approve(address _spender, uint256 _value) public virtual override returns (bool success) {
        _approvals[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    /**
     * @dev Returns the remaining number of tokens that `spender` will be
     * allowed to spend on behalf of `owner` through {transferFrom}. This is
     * zero by default.
     *
     * This value changes when {approve} or {transferFrom} are called.
     */
    function allowance(address _owner, address _spender) public view virtual override returns (uint256 remaining) {
        return _approvals[_owner][_spender];
    }
}
