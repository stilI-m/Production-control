import hmac
import hashlib

def generate_hmac_signature(payload: bytes, secret: str) -> str:
    """
    Генерирует SHA-256 HMAC подпись для переданной полезной нагрузки.
    """
    secret_bytes = secret.encode("utf-8")
    # Используем sha256 как современный стандарт
    signature = hmac.new(secret_bytes, payload, hashlib.sha256).hexdigest()
    return f"sha256={signature}"

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Проверяет валидность подписи.
    Использует compare_digest для защиты от атак по времени (timing attacks).
    """
    expected_signature = generate_hmac_signature(payload, secret)
    return hmac.compare_digest(expected_signature, signature)