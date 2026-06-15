import mongoengine as me
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib
import hmac
import binascii
import base64


class User(me.Document):
    """User model for authentication"""
    meta = {'collection': 'users'}

    id = me.SequenceField(primary_key=True)
    email = me.StringField(required=True, unique=True)
    password_hash = me.StringField(required=True)
    first_name = me.StringField(required=True, max_length=120)
    last_name = me.StringField(required=True, max_length=120)
    phone = me.StringField(max_length=20)
    is_admin = me.BooleanField(default=False)
    created_at = me.DateTimeField(default=datetime.utcnow)
    updated_at = me.DateTimeField(default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Verify password"""
        if isinstance(self.password_hash, str) and self.password_hash.startswith('scrypt:'):
            try:
                print(f"Auth: attempting scrypt verification for user {self.email}")
            except Exception:
                pass
            try:
                parts = self.password_hash.split('$')
                if len(parts) < 3:
                    raise ValueError('invalid scrypt hash format')
                params = parts[0].split(':')
                if len(params) < 4:
                    raise ValueError('invalid scrypt params')
                n = int(params[1])
                r = int(params[2])
                p = int(params[3])
                salt_raw = parts[1]
                hash_raw = parts[2]

                def try_decode_b64_first(s):
                    try:
                        pad = '=' * (-len(s) % 4)
                        return base64.b64decode(s + pad)
                    except Exception:
                        pass
                    try:
                        if len(s) % 2 == 0:
                            return binascii.unhexlify(s)
                    except Exception:
                        pass
                    return s.encode()

                def try_decode_hex_only(s):
                    try:
                        if len(s) % 2 == 0:
                            return binascii.unhexlify(s)
                    except Exception:
                        pass
                    try:
                        pad = '=' * (-len(s) % 4)
                        return base64.b64decode(s + pad)
                    except Exception:
                        pass
                    return s.encode()

                salt = try_decode_b64_first(salt_raw)
                stored = try_decode_hex_only(hash_raw)

                dklen = len(stored)
                try:
                    derived = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=n, r=r, p=p, dklen=dklen)
                except Exception as e:
                    msg = str(e)
                    print(f"Auth: scrypt derive error for {self.email}: {msg}")
                    if 'memory' in msg.lower() or 'memory limit' in msg.lower() or 'DIGEST' in msg:
                        try:
                            maxmem = 128 * 1024 * 1024
                            derived = hashlib.scrypt(password.encode('utf-8'), salt=salt, n=n, r=r, p=p, dklen=dklen, maxmem=maxmem)
                            print(f"Auth: scrypt retry with maxmem={maxmem} succeeded for {self.email}")
                        except Exception as e2:
                            print(f"Auth: scrypt retry (maxmem) failed for {self.email}: {e2}")
                            return False
                    else:
                        return False

                ok = hmac.compare_digest(derived, stored)
                try:
                    print(f"Auth: scrypt verification for {self.email} returned {ok} (salt_len={len(salt)}, dklen={dklen})")
                except Exception:
                    pass
                return ok
            except Exception as e:
                try:
                    print(f"Auth: scrypt verification for {self.email} failed during parsing/verification: {e}")
                except Exception:
                    pass
                return False

        try:
            print(f"Auth: attempting werkzeug verification for user {self.email}")
        except Exception:
            pass
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat(),
        }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp"""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)


class Transaction(me.Document):
    """Transaction model for income and expenses"""
    meta = {'collection': 'transactions'}

    id = me.SequenceField(primary_key=True)
    user_id = me.IntField(required=True)
    type = me.StringField(required=True, max_length=20)  # 'income' or 'expense'
    category = me.StringField(required=True, max_length=120)
    description = me.StringField(required=True, max_length=255)
    amount = me.FloatField(required=True)
    date = me.DateField(required=True)
    created_at = me.DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        """Convert transaction to dictionary"""
        return {
            'id': self.id,
            'type': self.type,
            'category': self.category,
            'description': self.description,
            'amount': self.amount,
            'date': self.date.isoformat(),
            'created_at': self.created_at.isoformat(),
        }
