#![no_std]
use soroban_sdk::{contract, contractimpl, contracttype, Address, BytesN, Env};

#[contracttype]
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum ThreatLevel {
    Trusted = 0,
    UnderInvestigation = 1,
    Suspicious = 2,
    ConfirmedMalicious = 3,
}

#[contracttype]
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct IndicatorRecord {
    /// SHA-256 hash of the threat indicator (wallet address / domain / token).
    pub indicator_hash: BytesN<32>,
    pub threat_level: ThreatLevel,
    /// Reputation score 0-100, mirrored from the off-chain ThreatNet API.
    pub reputation_score: u32,
    /// Ledger timestamp of the last update.
    pub updated_at: u64,
    /// Address of the administrator who verified and published this record.
    pub verified_by: Address,
}

#[contracttype]
#[derive(Clone, Debug, PartialEq, Eq)]
pub enum DataKey {
    Admin,
    Indicator(BytesN<32>),
    TotalIndicators,
}

#[contract]
pub struct SorobanThreatNet;

#[contractimpl]
impl SorobanThreatNet {
    /// Initialize the contract, setting the admin address.
    pub fn initialize(env: Env, admin: Address) {
        if env.storage().instance().has(&DataKey::Admin) {
            panic!("Already initialized");
        }
        admin.require_auth();
        env.storage().instance().set(&DataKey::Admin, &admin);
        env.storage().instance().set(&DataKey::TotalIndicators, &0u32);
    }

    /// Publish (insert or update) a threat indicator hash on the ledger.
    ///
    /// Only the admin may publish. The hash alone is stored — raw intelligence
    /// stays off-chain in the ThreatNet API database.
    pub fn publish_threat_indicator(
        env: Env,
        admin: Address,
        indicator_hash: BytesN<32>,
        threat_level: ThreatLevel,
        reputation_score: u32,
    ) {
        let stored_admin: Address = env.storage().instance().get(&DataKey::Admin).expect("Not initialized");
        admin.require_auth();
        if admin != stored_admin {
            panic!("Unauthorized admin");
        }
        if reputation_score > 100 {
            panic!("Reputation score must be between 0 and 100");
        }

        let record = IndicatorRecord {
            indicator_hash: indicator_hash.clone(),
            threat_level,
            reputation_score,
            updated_at: env.ledger().timestamp(),
            verified_by: admin,
        };

        let key = DataKey::Indicator(indicator_hash);
        if !env.storage().persistent().has(&key) {
            let count: u32 = env
                .storage()
                .instance()
                .get(&DataKey::TotalIndicators)
                .unwrap_or(0);
            env.storage().instance().set(&DataKey::TotalIndicators, &(count + 1));
        }
        env.storage().persistent().set(&key, &record);
    }

    /// Query an indicator record on-chain (zero-trust client verification).
    pub fn get_threat_indicator(env: Env, indicator_hash: BytesN<32>) -> Option<IndicatorRecord> {
        env.storage().persistent().get(&DataKey::Indicator(indicator_hash))
    }

    /// Total number of published threat indicators.
    pub fn get_total_indicators(env: Env) -> u32 {
        env.storage()
            .instance()
            .get(&DataKey::TotalIndicators)
            .unwrap_or(0)
    }
}

#[cfg(test)]
mod test {
    use super::*;
    use soroban_sdk::testutils::Address as _;
    use soroban_sdk::Env;

    #[test]
    fn test_threatnet_contract_workflow() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SorobanThreatNet);
        let client = SorobanThreatNetClient::new(&env, &contract_id);

        let admin = Address::generate(&env);
        env.mock_all_auths();

        client.initialize(&admin);

        let test_hash = BytesN::from_array(&env, &[7u8; 32]);
        client.publish_threat_indicator(&admin, &test_hash, &ThreatLevel::ConfirmedMalicious, &10u32);

        let fetched = client.get_threat_indicator(&test_hash).unwrap();
        assert_eq!(fetched.reputation_score, 10u32);
        assert_eq!(fetched.threat_level, ThreatLevel::ConfirmedMalicious);
        assert_eq!(client.get_total_indicators(), 1u32);
    }

    #[test]
    #[should_panic(expected = "Unauthorized admin")]
    fn test_non_admin_cannot_publish() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SorobanThreatNet);
        let client = SorobanThreatNetClient::new(&env, &contract_id);

        let admin = Address::generate(&env);
        let attacker = Address::generate(&env);
        env.mock_all_auths();

        client.initialize(&admin);

        // The attacker signs with their own address; authorization must fail.
        let test_hash = BytesN::from_array(&env, &[9u8; 32]);
        client.publish_threat_indicator(&attacker, &test_hash, &ThreatLevel::Suspicious, &40u32);
    }

    #[test]
    #[should_panic(expected = "Already initialized")]
    fn test_cannot_reinitialize() {
        let env = Env::default();
        let contract_id = env.register_contract(None, SorobanThreatNet);
        let client = SorobanThreatNetClient::new(&env, &contract_id);

        let admin = Address::generate(&env);
        env.mock_all_auths();

        client.initialize(&admin);
        client.initialize(&admin);
    }
}
