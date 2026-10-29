"""Central configuration. Everything is overridable through environment variables so the
same code runs locally for $0 and can be pointed at paid services later without code
changes (SRS 2.1.4-A: external services replaceable without major changes)."""
import os
from dataclasses import dataclass, field


def _load_dotenv() -> None:
    """Tiny .env loader (backend/.env) so no extra dependency is needed."""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv()


@dataclass
class Settings:
    database_url: str = field(default_factory=lambda: os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hansraj_qb"))
    jwt_secret: str = field(default_factory=lambda: os.getenv(
        "JWT_SECRET", "dev-only-change-me-please-use-32-bytes-min"))
    jwt_ttl_seconds: int = field(default_factory=lambda: int(os.getenv("JWT_TTL_SECONDS", "3600")))
    cors_origins: list = field(default_factory=lambda: [o.strip() for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",") if o.strip()])

    # AI / RAG (Gemini free tier). Without a key the app uses a local deterministic fallback.
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_embed_model: str = field(default_factory=lambda: os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001"))
    gemini_chat_model: str = field(default_factory=lambda: os.getenv("GEMINI_CHAT_MODEL", "gemini-2.5-flash"))
    embed_dim: int = field(default_factory=lambda: int(os.getenv("EMBED_DIM", "1536")))
    top_k: int = field(default_factory=lambda: int(os.getenv("RAG_TOP_K", "5")))

    # Email (Resend free tier). Without a key, emails are written to the log only.
    resend_api_key: str = field(default_factory=lambda: os.getenv("RESEND_API_KEY", ""))
    email_from: str = field(default_factory=lambda: os.getenv(
        "EMAIL_FROM", "Hansraj Query Bridge <onboarding@resend.dev>"))

    # Document storage: "local" (default, $0) or "s3"
    storage_backend: str = field(default_factory=lambda: os.getenv("STORAGE_BACKEND", "local"))
    upload_dir: str = field(default_factory=lambda: os.getenv("UPLOAD_DIR", "./uploads"))
    s3_bucket: str = field(default_factory=lambda: os.getenv("S3_BUCKET", ""))
    max_upload_mb: int = field(default_factory=lambda: int(os.getenv("MAX_UPLOAD_MB", "25")))

    # Security controls (SRS 3.2.1-F; UC-02 special requirements)
    lockout_attempts: int = field(default_factory=lambda: int(os.getenv("LOCKOUT_ATTEMPTS", "5")))
    lockout_seconds: int = field(default_factory=lambda: int(os.getenv("LOCKOUT_SECONDS", "900")))
    ai_rate_per_minute: int = field(default_factory=lambda: int(os.getenv("AI_RATE_PER_MINUTE", "20")))

    @property
    def uses_gemini(self) -> bool:
        return bool(self.gemini_api_key)

    @property
    def similarity_threshold(self) -> float:
        """RAG flow chart (SRS Appendix B) specifies 0.88. The no-key fallback embedder is
        lexical rather than semantic, so it needs a lower default. Always overridable."""
        env = os.getenv("SIMILARITY_THRESHOLD")
        if env:
            return float(env)
        return 0.88 if self.uses_gemini else 0.30


settings = Settings()
