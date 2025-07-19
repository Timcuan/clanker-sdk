import os
import json
import asyncio
import subprocess
import tempfile
from typing import Dict, Any
from datetime import datetime

from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
RPC_URL = os.getenv("RPC_URL", "https://mainnet.base.org")

if not PRIVATE_KEY:
    raise ValueError("PRIVATE_KEY environment variable is required")

async def deploy_token_via_clanker(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deploy a token using Clanker SDK via Node.js script
    
    Args:
        config: Token configuration dictionary
        
    Returns:
        Dictionary with success status and result/error
    """
    try:
        logger.info(f"Starting token deployment for: {config['name']} ({config['symbol']})")
        
        # Create the deployment script
        deployment_script = create_deployment_script(config)
        
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(deployment_script)
            script_path = f.name
        
        try:
            # Execute the Node.js script
            result = await execute_deployment_script(script_path)
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(script_path)
            except OSError:
                pass
                
    except Exception as e:
        logger.error(f"Deployment error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def create_deployment_script(config: Dict[str, Any]) -> str:
    """Create the Node.js deployment script using Clanker SDK"""
    
    # Prepare social media URLs
    social_urls = []
    for social in config.get('socialMediaUrls', []):
        social_urls.append({
            "platform": social['platform'],
            "url": social['url']
        })
    
    script = f"""
import {{ Clanker }} from 'clanker-sdk';
import {{ createPublicClient, createWalletClient, http }} from 'viem';
import {{ privateKeyToAccount }} from 'viem/accounts';
import {{ base }} from 'viem/chains';

// Configuration
const PRIVATE_KEY = "{PRIVATE_KEY}";
const RPC_URL = "{RPC_URL}";

// Token configuration
const tokenConfig = {{
    name: "{config['name']}",
    symbol: "{config['symbol']}",
    image: "{config['image']}",
    metadata: {{
        description: "{config.get('description', '')}",
        socialMediaUrls: {json.dumps(social_urls)},
        auditUrls: []
    }},
    context: {{
        interface: "Slanker",
        platform: "Telegram Mini App",
        messageId: "Deploy via Slanker",
        id: "{config['symbol']}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    }},
    pool: {{
        quoteToken: "0x4200000000000000000000000000000000000006", // WETH on Base
        initialMarketCap: "{config['initialMarketCap']}"
    }},
    vault: {{
        percentage: {config['vestingPercentage']},
        durationInDays: {config['vestingDurationDays']}
    }},
    devBuy: {{
        ethAmount: 0 // No initial buy
    }},
    rewardsConfig: {{
        creatorReward: {config['creatorReward']},
        creatorAdmin: null, // Will be set to account address
        creatorRewardRecipient: null, // Will be set to account address
        interfaceAdmin: "0x1eaf444ebDf6495C57aD52A04C61521bBf564ace",
        interfaceRewardRecipient: "0x1eaf444ebDf6495C57aD52A04C61521bBf564ace"
    }}
}};

async function deployToken() {{
    try {{
        // Initialize wallet with private key
        const account = privateKeyToAccount(PRIVATE_KEY);
        
        // Set creator addresses
        tokenConfig.rewardsConfig.creatorAdmin = account.address;
        tokenConfig.rewardsConfig.creatorRewardRecipient = account.address;
        
        const publicClient = createPublicClient({{
            chain: base,
            transport: http(RPC_URL),
        }});
        
        const wallet = createWalletClient({{
            account,
            chain: base,
            transport: http(RPC_URL),
        }});
        
        // Initialize Clanker SDK
        const clanker = new Clanker({{
            wallet,
            publicClient,
        }});
        
        console.log("🚀 Deploying Token...");
        console.log("Token Name:", tokenConfig.name);
        console.log("Symbol:", tokenConfig.symbol);
        console.log("Initial Market Cap:", tokenConfig.pool.initialMarketCap, "ETH");
        console.log("Vesting:", tokenConfig.vault.percentage + "% for " + tokenConfig.vault.durationInDays + " days");
        console.log("Creator Reward:", tokenConfig.rewardsConfig.creatorReward + "%");
        
        // Deploy the token
        const tokenAddress = await clanker.deployToken(tokenConfig);
        
        console.log("✅ Token deployed successfully!");
        console.log("Token Address:", tokenAddress);
        console.log("BaseScan URL:", `https://basescan.org/token/${{tokenAddress}}`);
        
        // Output result as JSON for Python to parse
        const result = {{
            success: true,
            address: tokenAddress,
            basescanUrl: `https://basescan.org/token/${{tokenAddress}}`,
            deploymentTime: new Date().toISOString()
        }};
        
        console.log("SLANKER_RESULT:", JSON.stringify(result));
        
    }} catch (error) {{
        console.error("❌ Deployment failed:", error.message);
        
        const result = {{
            success: false,
            error: error.message || "Unknown deployment error",
            deploymentTime: new Date().toISOString()
        }};
        
        console.log("SLANKER_RESULT:", JSON.stringify(result));
        process.exit(1);
    }}
}}

deployToken().catch(error => {{
    console.error("Fatal error:", error);
    const result = {{
        success: false,
        error: error.message || "Fatal deployment error",
        deploymentTime: new Date().toISOString()
    }};
    console.log("SLANKER_RESULT:", JSON.stringify(result));
    process.exit(1);
}});
"""
    
    return script

async def execute_deployment_script(script_path: str) -> Dict[str, Any]:
    """Execute the Node.js deployment script and parse the result"""
    try:
        logger.info("Executing deployment script...")
        
        # Run the script with Node.js
        process = await asyncio.create_subprocess_exec(
            'node', script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Decode output
        stdout_text = stdout.decode('utf-8') if stdout else ""
        stderr_text = stderr.decode('utf-8') if stderr else ""
        
        logger.info(f"Script stdout: {stdout_text}")
        if stderr_text:
            logger.warning(f"Script stderr: {stderr_text}")
        
        # Parse the result from stdout
        result = parse_deployment_result(stdout_text)
        
        if process.returncode == 0 and result["success"]:
            logger.info(f"Deployment successful: {result.get('address', 'Unknown address')}")
        else:
            logger.error(f"Deployment failed with return code {process.returncode}")
            if not result.get("error"):
                result["error"] = f"Script failed with return code {process.returncode}"
                result["success"] = False
        
        return result
        
    except FileNotFoundError:
        error_msg = "Node.js not found. Please install Node.js to deploy tokens."
        logger.error(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"Failed to execute deployment script: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}

def parse_deployment_result(output: str) -> Dict[str, Any]:
    """Parse the deployment result from script output"""
    try:
        # Look for the result line
        lines = output.split('\n')
        for line in lines:
            if line.startswith('SLANKER_RESULT:'):
                result_json = line.replace('SLANKER_RESULT:', '').strip()
                result = json.loads(result_json)
                return result
        
        # If no result found, assume failure
        return {
            "success": False,
            "error": "No deployment result found in script output"
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse deployment result: {e}")
        return {
            "success": False,
            "error": "Failed to parse deployment result"
        }
    except Exception as e:
        logger.error(f"Error parsing deployment result: {e}")
        return {
            "success": False,
            "error": str(e)
        }

# Security function to ensure private key is cleared from memory
def clear_sensitive_data():
    """Clear sensitive data from memory"""
    global PRIVATE_KEY
    if PRIVATE_KEY:
        # Overwrite the private key in memory
        PRIVATE_KEY = "0" * len(PRIVATE_KEY)
        PRIVATE_KEY = None
        logger.info("Sensitive data cleared from memory")