from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    gender: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)
    account_types: Optional[List[str]] = Field(default=None)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, hyphens, and underscores')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v and v not in ['Male', 'Female', 'Others']:
            raise ValueError('Gender must be Male, Female, or Others')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    email: Optional[str] = None
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response (without password)"""
    id: str
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    account_types: Optional[List[str]] = None
    wallet_balance: float = 0.0
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    """Schema for user in database"""
    email: EmailStr
    username: str
    hashed_password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    account_types: Optional[List[str]] = None
    wallet_balance: float = 0.0
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime


class PasswordChange(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v


class Trade(BaseModel):
    """Schema for a trade"""
    ticker: str = Field(..., description="Stock ticker symbol (e.g., AAPL, TSLA)")
    current_price: float = Field(..., description="Current price of the stock")
    position: str = Field(..., description="Trader position: 'bought' or 'sold'")

    @field_validator('position')
    @classmethod
    def validate_position(cls, v):
        if v not in ['bought', 'sold']:
            raise ValueError('Position must be either "bought" or "sold"')
        return v


class ExpertTrader(BaseModel):
    """Schema for an expert trader"""
    id: str
    full_name: str = Field(..., min_length=1, max_length=100)
    profile_photo: str = Field(..., description="URL to profile photo")
    description: str = Field(..., description="Trader description and expertise")
    specialization: str = Field(..., description="Trading specialization")
    ytd_return: float = Field(..., description="Year-to-date return percentage")
    win_rate: float = Field(..., description="Win rate percentage")
    copiers: int = Field(..., description="Number of copiers")
    trades: List[Trade] = Field(default=[], description="List of recent trades")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExpertTraderResponse(BaseModel):
    """Schema for expert trader response"""
    id: str
    full_name: str
    profile_photo: str
    description: str
    specialization: str
    ytd_return: float
    win_rate: float
    copiers: int
    trades: List[Trade]

    class Config:
        from_attributes = True


class InvestmentPlan(BaseModel):
    """Schema for an investment plan"""
    id: str
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., description="Plan description and benefits")
    minimum_investment: float = Field(..., gt=0, description="Minimum investment amount in USD")
    holding_period_months: int = Field(..., gt=0, description="Investment holding period in months")
    expected_return_percent: float = Field(..., description="Expected return percentage")
    current_subscribers: int = Field(default=0, ge=0, description="Number of current subscribers")
    is_active: bool = Field(default=True, description="Whether the plan is currently available")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvestmentPlanResponse(BaseModel):
    """Schema for investment plan response"""
    id: str
    name: str
    description: str
    minimum_investment: float
    holding_period_months: int
    expected_return_percent: float
    current_subscribers: int
    is_active: bool

    class Config:
        from_attributes = True


class Transaction(BaseModel):
    """Schema for a wallet transaction"""
    id: str
    user_id: str
    transaction_type: str = Field(..., description="Type: 'deposit' or 'withdrawal'")
    amount: float = Field(..., gt=0, description="Transaction amount in USD")
    status: str = Field(..., description="Status: 'pending', 'completed', or 'failed'")
    payment_method: str = Field(..., description="Payment method used")
    reference_number: str = Field(..., description="Unique transaction reference")
    description: Optional[str] = Field(None, description="Transaction description")
    created_at: datetime
    updated_at: datetime

    @field_validator('transaction_type')
    @classmethod
    def validate_transaction_type(cls, v):
        if v not in ['deposit', 'withdrawal']:
            raise ValueError('Transaction type must be either "deposit" or "withdrawal"')
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['pending', 'completed', 'failed']:
            raise ValueError('Status must be "pending", "completed", or "failed"')
        return v

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    """Schema for transaction response"""
    id: str
    transaction_type: str
    amount: float
    status: str
    payment_method: str
    reference_number: str
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DepositRequest(BaseModel):
    """Schema for creating a deposit request"""
    amount: float = Field(..., gt=0, description="Deposit amount in USD")
    payment_method: str = Field(default="bank_transfer", description="Payment method")
    payment_proof: Optional[str] = Field(None, description="URL or reference to payment proof")
    notes: Optional[str] = Field(None, description="Additional notes from user")

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        if v not in ['bank_transfer', 'crypto', 'card']:
            raise ValueError('Payment method must be "bank_transfer", "crypto", or "card"')
        return v


class DepositRequestResponse(BaseModel):
    """Schema for deposit request response"""
    id: str
    user_id: str
    username: str
    email: str
    amount: float
    payment_method: str
    payment_proof: Optional[str]
    notes: Optional[str]
    status: str  # pending, approved, rejected
    created_at: datetime
    updated_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
