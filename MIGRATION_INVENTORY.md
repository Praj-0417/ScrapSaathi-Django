# ScrapSaathi Migration Inventory: Express/MongoDB to Django REST Framework

## 1. Overview & Architectural Baseline

This inventory maps the original Node.js/Express monolith (`ScrapSathi-Monolith/server`) to the new Django REST Framework architecture in `scrapsaathi-django/backend`.

| Metric / Aspect | Express / MongoDB Monolith | Django REST Framework + PostgreSQL |
| :--- | :--- | :--- |
| **Language & Runtime** | Node.js (CommonJS, Express 4.x) | Python 3.11+, Django 5.x, DRF |
| **Database** | MongoDB (Mongoose schemas, loose polymorphism) | PostgreSQL (Relational tables, Django ORM, ACID transactions) |
| **Authentication** | JWT (hs256) via Bearer header & httpOnly cookie, tokenVersion revocation | Custom JWT authentication supporting Bearer & cookie, token_version revocation |
| **Password Hashing** | bcrypt (12 rounds) | Django PBKDF2 / bcrypt compatible password hasher |
| **API Envelope** | `{ success: bool, message: str, data: any, meta: obj, errors: list }` | Identical custom DRF renderer / response helper |
| **Mount Points** | `/health`, `/api/v1/*`, and `/api/*` (dual mounted) | `/health`, `/api/v1/*`, and `/api/*` (dual mounted) |

---

## 2. API Endpoint & Feature Mapping

### 2.1 Health & Diagnostics
| Monolith Endpoint | Method | Monolith Handler | Django App / View | Preserved Contract |
| :--- | :--- | :--- | :--- | :--- |
| `/health` | GET | `app.js` (`MESSAGES.HEALTH_OK`) | `common.views.HealthCheckView` | `{"success": true, "message": "ScrapSaathi backend is healthy", ...}` |
| `/api/v1/health` & `/api/health` | GET | `routes/index.js` | `common.views.ApiV1HealthView` | `{"success": true, "message": "ScrapSaathi API v1 is healthy", "data": {"service": "scrapsaathi-api", "version": "v1"}}` |
| `/metrics` | GET | None (Prometheus gap) | `django-prometheus` export | Standard Prometheus scrape target |

### 2.2 Authentication & OTP (`/api/v1/auth` & `/api/v1/otp`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/auth/register` | POST | `authController.register` | `authentication.views.RegisterView` | Requires `verificationToken` (Caveat #2), sets cookie, returns `{token, user}` |
| `/auth/login` | POST | `authController.login` | `authentication.views.LoginView` | Validates credentials, sets cookie, returns `{token, user}` |
| `/auth/google` | POST | `authController.googleLogin` | `authentication.views.GoogleLoginView` | Verified token or claims payload, creates/links user |
| `/auth/google/token` | POST | `authController.googleLogin` | `authentication.views.GoogleLoginView` | Alias for Google login |
| `/auth/logout` | POST | `authController.logout` | `authentication.views.LogoutView` | Increments `token_version`, clears cookie |
| `/auth/otp/send-registration` | POST | `authController.sendRegistrationOtp` | `authentication.views.SendRegistrationOtpView` | Rejects existing emails, creates 6-digit OTP |
| `/auth/otp/send-reset` & `/send-otp` | POST | `authController.sendPasswordResetOtp` | `authentication.views.SendResetOtpView` | Rejects unknown emails, creates 6-digit OTP |
| `/auth/otp/verify` | POST | `authController.verifyOtp` | `authentication.views.VerifyOtpView` | If `?purpose=registration`, signs and returns `verificationToken` |
| `/auth/password/reset` & `/update` | POST | `authController.resetPassword` | `authentication.views.ResetPasswordView` | Verifies OTP and updates password hash |

### 2.3 User Profile Management (`/api/v1/users`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/users/me` | GET | `userController.getMe` | `users.views.UserMeView` | Returns sanitized user and linked profile |
| `/users/me` | PATCH | `userController.updateMe` | `users.views.UserMeView` | Updates `name`, `phone`, `avatar` |
| `/users/me/profile` | PATCH | `userController.updateProfile` | `users.views.UserProfileView` | Updates role-specific profile fields |

### 2.4 Pickup Requests (`/api/v1/pickups`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/pickups` | POST | `pickupController.create` | `pickups.views.PickupCreateView` | Server-calculated quote snapshot (Caveat #6), serviceability check, optional photo |
| `/pickups` | GET | `pickupController.listMyPickups` | `pickups.views.MyPickupsListView` | Paginated list of user's bookings |
| `/pickups/:id` | GET | `pickupController.getOne` | `pickups.views.PickupDetailView` | Owner or assigned collector only |
| `/pickups/:id/cancel` | PATCH | `pickupController.cancel` | `pickups.views.PickupCancelView` | Owner cancels pending/accepted request |
| `/pickups/:id/tracking` | GET | `pickupController.getTracking` | `pickups.views.PickupTrackingView` | Authenticated live telemetry with staleness check |

### 2.5 Waste Collector Operations (`/api/v1/collector`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/collector/pickups/available` | GET | `collectorController.listAvailable` | `collector.views.AvailablePickupsView` | Filter by proximity (Haversine/geodesic) |
| `/collector/pickups` | GET | `collectorController.myPickups` | `collector.views.CollectorPickupsView` | Pickups assigned to/completed by collector |
| `/collector/pickups/:id/accept` | POST | `collectorController.accept` | `collector.views.AcceptPickupView` | **Atomic conditional transition** (`SELECT FOR UPDATE`) |
| `/collector/pickups/:id/cancel` | POST | `collectorController.cancel` | `collector.views.ReleasePickupView` | **Atomic release** resets to `pending` & unsets collector |
| `/collector/pickups/:id/complete` | POST | `collectorController.complete` | `collector.views.CompletePickupView` | **Atomic complete** with weighment & settlement data |
| `/collector/pickups/:id/location` | POST | `collectorController.updateLocation` | `collector.views.PushCollectorLocationView` | Push live telemetry coordinates, heading, speed |

### 2.6 Scrap Rates Management (`/api/v1/rates`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/rates` | GET | `rateController.getRates` | `rates.views.RatesListView` | Public rate board with city effective price calculation |
| `/rates/item` | PATCH | `rateController.updateItem` | `rates.views.RateItemUpdateView` | Admin update item rate & city prices |
| `/rates/item` | POST | `rateController.addItem` | `rates.views.RateItemCreateView` | Admin add item |
| `/rates/item/:itemId` | DELETE | `rateController.deleteItem` | `rates.views.RateItemDeleteView` | Admin delete item |

### 2.7 Donations (`/api/v1/donations`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/donations` | POST | `donationController.create` | `donations.views.DonationCreateView` | Generates provisional acknowledgement reference |
| `/donations/me` | GET | `donationController.listMine` | `donations.views.MyDonationsView` | User donation history |

### 2.8 Geocoding & Serviceability (`/api/v1/geocode`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/geocode/search` | GET | `geocodeRoutes.js` search | `common.views.GeocodeSearchView` | 9-city locality directory + Nominatim fallback |
| `/geocode/reverse` | GET | `geocodeRoutes.js` reverse | `common.views.GeocodeReverseView` | Reverse lookup with closest locality match |
| `/geocode/serviceable` | GET | `geocodeRoutes.js` serviceable | `common.views.GeocodeServiceabilityView` | Haversine formula across 9 operating hubs |

### 2.9 Contact Inquiries (`/api/v1/contact`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/contact` | POST | `contactController.submitContact` | `contact.views.ContactCreateView` | Stores user inquiry in database |

### 2.10 Admin Operations (`/api/v1/admin`)
| Monolith Endpoint | Method | Monolith Handler | Django View / Serializer | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/auth/login` | POST | `adminController.login` | `authentication.views.AdminLoginView` | Admin credentials verification |
| `/admin/users` | GET | `adminController.listUsers` | `users.views.AdminUserListView` | Paginated user search |
| `/admin/pickups` | GET | `adminController.listPickups` | `pickups.views.AdminPickupListView` | Paginated pickup list with status filter |
| `/admin/donations` | GET | `adminController.listDonations` | `donations.views.AdminDonationListView` | Paginated donation audit |

---

## 3. Database Decision Analysis: PostgreSQL Feasibility

### Evaluation
1. **Relational Integrity**:
   - Entities (`User`, `Profile`, `PickupRequest`, `Donation`, `OTP`, `ScrapRateCategory`, `ScrapItem`) map directly into 3rd normal form relational tables.
   - Foreign key constraints prevent orphaned records when collectors or users interact.
2. **Concurrency & Race Conditions**:
   - Monolith relied on Mongoose `findOneAndUpdate({ _id, status: 'pending' })`.
   - In PostgreSQL, Django provides `transaction.atomic()` with `select_for_update()` or conditional `.filter(status='pending').update(...)`, ensuring ACID-compliant concurrency.
3. **Audit & Snapshots**:
   - Pricing quotes (`quote`) and settlements (`settlement`) are modeled with relational or JSONB fields, providing immutability and flexible indexing.
4. **Portability & Local Dev**:
   - The Django application supports PostgreSQL by default (with environment configuration `DATABASE_URL` or `POSTGRES_DB`), while gracefully falling back to SQLite for instant local verification when a PostgreSQL service is not active.
5. **Conclusion**:
   - **PostgreSQL is fully feasible, technically superior for ScrapSaathi's transactional workflow, and selected as the primary relational database.**
