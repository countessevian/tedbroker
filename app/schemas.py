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
    two_fa_enabled: bool = False
    auth_provider: str = "local"  # "local" or "google"
    selected_traders: List[str] = Field(default=[], description="List of trader IDs selected for copy trading")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    """Schema for user in database"""
    email: EmailStr
    username: str
    hashed_password: Optional[str] = None  # Optional for OAuth users
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    account_types: Optional[List[str]] = None
    wallet_balance: float = 0.0
    is_active: bool = True
    is_verified: bool = False
    two_fa_enabled: bool = False
    auth_provider: str = "local"  # "local" or "google"
    google_id: Optional[str] = None  # Google OAuth ID
    profile_picture: Optional[str] = None  # Profile picture URL
    selected_traders: List[str] = []
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


class InvestInPlanRequest(BaseModel):
    """Schema for investing in a plan"""
    plan_id: str = Field(..., description="Investment plan ID")
    amount: float = Field(..., gt=0, description="Investment amount in USD")

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v < 0:
            raise ValueError('Investment amount must be positive')
        return v


class UserInvestment(BaseModel):
    """Schema for a user investment"""
    id: str
    user_id: str
    plan_id: str
    plan_name: str
    amount_invested: float
    expected_return_percent: float
    holding_period_months: int
    start_date: datetime
    maturity_date: datetime
    current_value: float
    profit_loss: float
    status: str  # active, matured, withdrawn
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInvestmentResponse(BaseModel):
    """Schema for user investment response"""
    id: str
    plan_id: str
    plan_name: str
    amount_invested: float
    expected_return_percent: float
    holding_period_months: int
    start_date: datetime
    maturity_date: datetime
    current_value: float
    profit_loss: float
    profit_loss_percent: float
    days_elapsed: int
    days_remaining: int
    status: str

    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary"""
    total_invested: float
    current_value: float
    total_profit_loss: float
    total_profit_loss_percent: float
    active_investments: int
    investments: List[UserInvestmentResponse]

    class Config:
        from_attributes = True


class BankAccountCreate(BaseModel):
    """Schema for creating a withdrawal bank account"""
    account_name: str = Field(..., min_length=1, max_length=100, description="Account holder name")
    account_number: str = Field(..., min_length=1, max_length=50, description="Bank account number")
    bank_name: str = Field(..., min_length=1, max_length=100, description="Bank name")
    bank_branch: Optional[str] = Field(None, max_length=100, description="Bank branch")
    swift_code: Optional[str] = Field(None, max_length=20, description="SWIFT/BIC code")
    routing_number: Optional[str] = Field(None, max_length=20, description="Routing number")
    iban: Optional[str] = Field(None, max_length=50, description="IBAN")
    bank_address: Optional[str] = Field(None, max_length=200, description="Bank address")
    account_type: Optional[str] = Field(None, max_length=20, description="Account type (savings/checking)")

    @field_validator('account_type')
    @classmethod
    def validate_account_type(cls, v):
        if v and v not in ['savings', 'checking']:
            raise ValueError('Account type must be either "savings" or "checking"')
        return v


class BankAccountResponse(BaseModel):
    """Schema for bank account response"""
    id: str
    user_id: str
    account_name: str
    account_number: str
    bank_name: str
    bank_branch: Optional[str]
    swift_code: Optional[str]
    routing_number: Optional[str]
    iban: Optional[str]
    bank_address: Optional[str]
    account_type: Optional[str]
    is_primary: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CryptoWithdrawalAddressCreate(BaseModel):
    """Schema for creating a crypto withdrawal address"""
    currency: str = Field(..., min_length=2, max_length=10, description="Cryptocurrency code (e.g., BTC, ETH, USDT)")
    wallet_address: str = Field(..., min_length=10, max_length=100, description="Cryptocurrency wallet address")
    network: Optional[str] = Field(None, max_length=50, description="Network (e.g., ERC20, TRC20, BEP20)")
    label: Optional[str] = Field(None, max_length=50, description="Custom label for the address")

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        # Common cryptocurrencies
        allowed_currencies = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'TRX']
        if v.upper() not in allowed_currencies:
            raise ValueError(f'Currency must be one of: {", ".join(allowed_currencies)}')
        return v.upper()


class CryptoWithdrawalAddressResponse(BaseModel):
    """Schema for crypto withdrawal address response"""
    id: str
    user_id: str
    currency: str
    wallet_address: str
    network: Optional[str]
    label: Optional[str]
    is_primary: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WithdrawalRequest(BaseModel):
    """Schema for creating a withdrawal request"""
    amount: float = Field(..., gt=0, description="Withdrawal amount in USD")
    withdrawal_method: str = Field(..., description="Withdrawal method: 'bank' or 'crypto'")
    account_id: str = Field(..., description="ID of the withdrawal account (bank account or crypto address)")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @field_validator('withdrawal_method')
    @classmethod
    def validate_withdrawal_method(cls, v):
        if v not in ['bank', 'crypto']:
            raise ValueError('Withdrawal method must be either "bank" or "crypto"')
        return v


class WithdrawalRequestResponse(BaseModel):
    """Schema for withdrawal request response"""
    id: str
    user_id: str
    username: str
    email: str
    amount: float
    withdrawal_method: str
    account_id: str
    account_details: dict
    notes: Optional[str]
    status: str  # pending, approved, rejected, processing, completed
    created_at: datetime
    updated_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    """Schema for creating a chat message"""
    message: str = Field(..., min_length=1, max_length=2000, description="Message content")
    conversation_id: Optional[str] = Field(None, description="Conversation ID (optional for first message)")


class ChatMessageResponse(BaseModel):
    """Schema for chat message response"""
    id: str
    conversation_id: str
    sender_id: str
    sender_type: str  # "user" or "admin"
    sender_name: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ChatConversationResponse(BaseModel):
    """Schema for chat conversation response"""
    id: str
    user_id: str
    user_name: str
    user_email: str
    status: str  # "active", "closed"
    unread_count: int
    last_message: Optional[str]
    last_message_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatConversationDetail(BaseModel):
    """Schema for detailed chat conversation with messages"""
    id: str
    user_id: str
    user_name: str
    user_email: str
    status: str
    messages: List[ChatMessageResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OnboardingPersonalInfo(BaseModel):
    """Schema for onboarding personal information step"""
    first_name: str = Field(..., min_length=1, max_length=50, description="First name")
    last_name: str = Field(..., min_length=1, max_length=50, description="Last name")
    gender: str = Field(..., description="Gender: Male, Female, or Others")

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in ['Male', 'Female', 'Others']:
            raise ValueError('Gender must be Male, Female, or Others')
        return v


class OnboardingAddress(BaseModel):
    """Schema for onboarding address step"""
    street: str = Field(..., min_length=1, max_length=200, description="Street address")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=1, max_length=100, description="State/Province")
    zip_code: str = Field(..., min_length=1, max_length=20, description="ZIP/Postal code")
    country: str = Field(..., min_length=1, max_length=100, description="Country")


class OnboardingKYC(BaseModel):
    """Schema for onboarding KYC document step"""
    document_number: str = Field(..., min_length=1, max_length=50, description="ID document number")
    document_photo: str = Field(..., description="Base64 encoded document photo or file path")


class OnboardingStatus(BaseModel):
    """Schema for checking onboarding completion status"""
    is_onboarding_complete: bool
    current_step: Optional[str] = None
    completed_steps: List[str] = []
