"""
User and Profile Relational Models.
Replaces MongoDB loose references with clean PostgreSQL 1-to-1 relationships
while maintaining exact serialized shapes for frontend compatibility.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from common.constants import USER_TYPES, ROLES

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email address is required')
        email = self.normalize_email(email).lower().strip()
        extra_fields.setdefault('role', ROLES.USER)
        extra_fields.setdefault('user_type', USER_TYPES.INDIVIDUAL)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', ROLES.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=80)
    email = models.EmailField(unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    google_id = models.CharField(max_length=150, blank=True, null=True, db_index=True)
    auth_provider = models.CharField(max_length=20, default='local')
    avatar = models.CharField(max_length=500, blank=True, default='')
    otp_verified = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=True)
    token_version = models.IntegerField(default=0)
    role = models.CharField(max_length=20, default=ROLES.USER, db_index=True)
    user_type = models.CharField(max_length=30, default=USER_TYPES.INDIVIDUAL, db_index=True)
    profile_model = models.CharField(max_length=50, default='IndividualProfile')

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'scrapsaathi_users'
        indexes = [
            models.Index(fields=['role', 'user_type']),
            models.Index(fields=['email']),
        ]

    def get_profile(self):
        """Resolves the typed profile model for this user."""
        if hasattr(self, 'individual_profile'):
            return self.individual_profile
        if hasattr(self, 'waste_collector_profile'):
            return self.waste_collector_profile
        if hasattr(self, 'recycle_company_profile'):
            return self.recycle_company_profile
        if hasattr(self, 'big_org_profile'):
            return self.big_org_profile
        return None

    def get_profile_dict(self):
        profile = self.get_profile()
        if not profile:
            return None
        return profile.to_dict()

    def to_dict(self):
        """Returns JSON representation matching the Mongoose User document."""
        return {
            '_id': str(self.id),
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'avatar': self.avatar,
            'role': self.role,
            'userType': self.user_type,
            'authProvider': self.auth_provider,
            'otpVerified': self.otp_verified,
            'termsAccepted': self.terms_accepted,
            'profile': self.get_profile_dict(),
            'profileModel': self.profile_model,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

class IndividualProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='individual_profile')
    address = models.TextField(blank=True, default='')
    profile_photo = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        db_table = 'user_individual_profiles'

    def to_dict(self):
        return {
            '_id': str(self.id),
            'id': str(self.id),
            'address': self.address,
            'profilePhoto': self.profile_photo,
        }

class WasteCollectorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='waste_collector_profile')
    address = models.TextField(blank=True, default='')
    profile_photo = models.CharField(max_length=500, blank=True, default='')
    company_name = models.CharField(max_length=150, blank=True, default='')
    business_license_no = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'user_waste_collector_profiles'

    def to_dict(self):
        return {
            '_id': str(self.id),
            'id': str(self.id),
            'address': self.address,
            'profilePhoto': self.profile_photo,
            'companyName': self.company_name,
            'businessLicenseNo': self.business_license_no,
        }

class RecycleCompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recycle_company_profile')
    address = models.TextField(blank=True, default='')
    company_name = models.CharField(max_length=150, blank=True, default='')
    business_license_no = models.CharField(max_length=100, blank=True, default='')
    waste_type = models.CharField(max_length=150, blank=True, default='')
    recycling_capabilities = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'user_recycle_company_profiles'

    def to_dict(self):
        return {
            '_id': str(self.id),
            'id': str(self.id),
            'address': self.address,
            'companyName': self.company_name,
            'businessLicenseNo': self.business_license_no,
            'wasteType': self.waste_type,
            'recyclingCapabilities': self.recycling_capabilities,
        }

class BigOrganizationProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='big_org_profile')
    address = models.TextField(blank=True, default='')
    company_name = models.CharField(max_length=150, blank=True, default='')
    business_license_no = models.CharField(max_length=100, blank=True, default='')

    class Meta:
        db_table = 'user_big_organization_profiles'

    def to_dict(self):
        return {
            '_id': str(self.id),
            'id': str(self.id),
            'address': self.address,
            'companyName': self.company_name,
            'businessLicenseNo': self.business_license_no,
        }
