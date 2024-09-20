#![no_std]
use soroban_sdk::{contract, contractimpl, symbol_short, token, vec, Address, Env, IntoVal, String, Symbol, Vec};

#[contract]
pub struct SoroChatContract;

#[contractimpl]
impl SoroChatContract {
    pub fn hello(env: Env, to: Symbol) -> Vec<Symbol> {
        vec![&env, symbol_short!("Hello"), to]
    }

    pub fn send_xlm(env: Env, from: Address, to: Address, amount: i128) {
        let xml_token = Address::from_string(&String::from_str(&env, "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC"));

        from.require_auth_for_args(
            (xml_token.clone(), amount).into_val(&env)
        );
    
        move_token(&env, &xml_token, &from, &to, amount);
    }

    pub fn check_balance(env: Env, address: Address) -> i128 {
        let xml_token = Address::from_string(&String::from_str(&env, "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC"));
        let token_client = token::Client::new(&env, &xml_token);

        token_client.balance(&address)
    }
}

pub fn move_token(env: &Env, token: &Address, from: &Address, to: &Address, amount: i128) {
    let token_client = token::Client::new(env, token);
    let contract_address = env.current_contract_address();

    token_client.transfer(from, &contract_address, &amount);
    token_client.transfer(&contract_address, to, &amount);
}

mod test;
