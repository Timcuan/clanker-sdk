import os
import asyncio
import subprocess
import json
import tempfile
from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from deploy import deploy_token_via_clanker

# Load environment variables
load_dotenv()

# Configuration
API_SECRET_KEY = os.getenv("API_SECRET_KEY", "your-secret-key")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://web.telegram.org").split(",")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "5"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Configure logging
logger.add("logs/api.log", rotation="1 day", level="INFO")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Slanker API",
    description="API for deploying tokens via Clanker SDK",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if ENVIRONMENT == "development" else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class SocialMediaUrl(BaseModel):
    platform: str = Field(..., min_length=1, max_length=20)
    url: str = Field(..., min_length=1, max_length=500)
    
    @validator('platform')
    def validate_platform(cls, v):
        allowed_platforms = ['x', 'twitter', 'telegram', 'discord', 'github', 'website', 'medium']
        if v.lower() not in allowed_platforms:
            raise ValueError(f"Platform must be one of: {allowed_platforms}")
        return v.lower()
    
    @validator('url')
    def validate_url(cls, v):
        if not (v.startswith('http://') or v.startswith('https://')):
            raise ValueError("URL must start with http:// or https://")
        return v

class TokenDeployRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=3, max_length=5)
    image: str = Field(..., min_length=1, max_length=500)
    initialMarketCap: str = Field(..., regex=r'^\d+(\.\d+)?$')
    vestingPercentage: int = Field(..., ge=0, le=30)
    vestingDurationDays: int = Field(..., ge=1, le=365)
    creatorReward: int = Field(..., ge=0, le=80)
    socialMediaUrls: List[SocialMediaUrl] = Field(default=[])
    description: Optional[str] = Field(None, max_length=500)
    
    @validator('symbol')
    def validate_symbol(cls, v):
        if not v.isalpha():
            raise ValueError("Symbol must contain only letters")
        return v.upper()
    
    @validator('image')
    def validate_image(cls, v):
        if not v.startswith('ipfs://'):
            raise ValueError("Image must be an IPFS URL starting with ipfs://")
        return v

class TokenDeployResponse(BaseModel):
    success: bool
    address: Optional[str] = None
    basescanUrl: Optional[str] = None
    deploymentTime: str
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str
    version: str

# Utility functions
def sanitize_input(value: str) -> str:
    """Sanitize input to prevent injection attacks"""
    # Remove potentially dangerous characters
    dangerous_chars = ['`', ';', '&', '|', '$', '(', ')', '<', '>', '"', "'"]
    for char in dangerous_chars:
        value = value.replace(char, '')
    return value.strip()

async def validate_request(request: TokenDeployRequest) -> Dict[str, Any]:
    """Validate and sanitize the token deployment request"""
    try:
        # Sanitize string inputs
        sanitized_name = sanitize_input(request.name)
        sanitized_symbol = sanitize_input(request.symbol)
        sanitized_description = sanitize_input(request.description or "")
        
        # Validate numeric inputs
        try:
            market_cap_float = float(request.initialMarketCap)
            if market_cap_float <= 0:
                raise ValueError("Initial market cap must be positive")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid initial market cap")
        
        # Validate social media URLs
        for social in request.socialMediaUrls:
            if len(social.url) > 500:
                raise HTTPException(status_code=400, detail="Social media URL too long")
        
        return {
            "name": sanitized_name,
            "symbol": sanitized_symbol,
            "image": request.image,
            "description": sanitized_description,
            "initialMarketCap": request.initialMarketCap,
            "vestingPercentage": request.vestingPercentage,
            "vestingDurationDays": request.vestingDurationDays,
            "creatorReward": request.creatorReward,
            "socialMediaUrls": [{"platform": s.platform, "url": s.url} for s in request.socialMediaUrls]
        }
    except Exception as e:
        logger.error(f"Request validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="slanker-api",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0"
    )

@app.post("/deploy", response_model=TokenDeployResponse)
@limiter.limit(f"{RATE_LIMIT_PER_MINUTE}/minute")
async def deploy_token(
    request: Request,
    deploy_request: TokenDeployRequest
):
    """Deploy a token via Clanker SDK"""
    deployment_time = datetime.utcnow().isoformat()
    
    try:
        logger.info(f"Token deployment request: {deploy_request.name} ({deploy_request.symbol})")
        
        # Validate and sanitize request
        validated_data = await validate_request(deploy_request)
        
        # Deploy token using Clanker SDK
        result = await deploy_token_via_clanker(validated_data)
        
        if result["success"]:
            logger.info(f"Token deployed successfully: {result['address']}")
            return TokenDeployResponse(
                success=True,
                address=result["address"],
                basescanUrl=f"https://basescan.org/token/{result['address']}",
                deploymentTime=deployment_time
            )
        else:
            logger.error(f"Token deployment failed: {result['error']}")
            return TokenDeployResponse(
                success=False,
                deploymentTime=deployment_time,
                error=result["error"]
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during deployment: {e}")
        return TokenDeployResponse(
            success=False,
            deploymentTime=deployment_time,
            error="Internal server error during deployment"
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Slanker API",
        "version": "1.0.0",
        "status": "running",
        "description": "API for deploying tokens via Clanker SDK"
    }

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return {"error": "Endpoint not found", "status_code": 404}

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return {"error": "Internal server error", "status_code": 500}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=ENVIRONMENT == "development",
        log_level="info"
    )