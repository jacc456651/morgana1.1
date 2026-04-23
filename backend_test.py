import requests
import sys
import json
from datetime import datetime

class MorganaAPITester:
    def __init__(self, base_url="https://mobile-screener-hub.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.admin_token = None
        self.test_user_token = None

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def test_api_root(self):
        """Test API root endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Response: {data}"
            self.log_test("API Root Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("API Root Endpoint", False, f"Error: {str(e)}")
            return False

    def test_get_favorites_empty(self):
        """Test GET /api/favorites (should return empty list initially)"""
        try:
            response = requests.get(f"{self.api_url}/favorites", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Count: {len(data)} favorites"
            self.log_test("GET Favorites (Initial)", success, details)
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("GET Favorites (Initial)", False, f"Error: {str(e)}")
            return False, []

    def test_create_favorite(self, caceria_id="c1", caceria_name="Growth Compounders"):
        """Test POST /api/favorites"""
        try:
            payload = {
                "caceria_id": caceria_id,
                "caceria_name": caceria_name
            }
            response = requests.post(f"{self.api_url}/favorites", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Created favorite: {data.get('caceria_name')}"
                return success, data
            self.log_test("POST Create Favorite", success, details)
            return success, None
        except Exception as e:
            self.log_test("POST Create Favorite", False, f"Error: {str(e)}")
            return False, None

    def test_get_favorites_with_data(self):
        """Test GET /api/favorites after creating one"""
        try:
            response = requests.get(f"{self.api_url}/favorites", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Count: {len(data)} favorites"
                if len(data) > 0:
                    details += f", First: {data[0].get('caceria_name')}"
            self.log_test("GET Favorites (With Data)", success, details)
            return success, response.json() if success else []
        except Exception as e:
            self.log_test("GET Favorites (With Data)", False, f"Error: {str(e)}")
            return False, []

    def test_delete_favorite(self, caceria_id="c1"):
        """Test DELETE /api/favorites/{caceria_id}"""
        try:
            response = requests.delete(f"{self.api_url}/favorites/{caceria_id}", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message')}"
            self.log_test("DELETE Favorite", success, details)
            return success
        except Exception as e:
            self.log_test("DELETE Favorite", False, f"Error: {str(e)}")
            return False

    def test_delete_nonexistent_favorite(self):
        """Test DELETE /api/favorites/{nonexistent_id} (should return 404)"""
        try:
            response = requests.delete(f"{self.api_url}/favorites/nonexistent", timeout=10)
            success = response.status_code == 404
            details = f"Status: {response.status_code} (Expected 404)"
            self.log_test("DELETE Nonexistent Favorite", success, details)
            return success
        except Exception as e:
            self.log_test("DELETE Nonexistent Favorite", False, f"Error: {str(e)}")
            return False

    def test_create_duplicate_favorite(self):
        """Test creating duplicate favorite (should return existing)"""
        try:
            # Create first favorite
            payload = {"caceria_id": "c2", "caceria_name": "Value Profundo"}
            response1 = requests.post(f"{self.api_url}/favorites", json=payload, timeout=10)
            
            # Try to create same favorite again
            response2 = requests.post(f"{self.api_url}/favorites", json=payload, timeout=10)
            
            success = response1.status_code == 200 and response2.status_code == 200
            details = f"First: {response1.status_code}, Second: {response2.status_code}"
            
            if success:
                data1 = response1.json()
                data2 = response2.json()
                details += f", Same ID: {data1.get('id') == data2.get('id')}"
            
            self.log_test("Create Duplicate Favorite", success, details)
            return success
        except Exception as e:
            self.log_test("Create Duplicate Favorite", False, f"Error: {str(e)}")
            return False

    def test_status_endpoints(self):
        """Test status check endpoints"""
        try:
            # Test POST status
            payload = {"client_name": "test_client"}
            response = requests.post(f"{self.api_url}/status", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"POST Status: {response.status_code}"
            
            if success:
                # Test GET status
                response2 = requests.get(f"{self.api_url}/status", timeout=10)
                success = success and response2.status_code == 200
                details += f", GET Status: {response2.status_code}"
                if success:
                    data = response2.json()
                    details += f", Count: {len(data)} status checks"
            
            self.log_test("Status Endpoints", success, details)
            return success
        except Exception as e:
            self.log_test("Status Endpoints", False, f"Error: {str(e)}")
            return False

    def test_admin_login(self):
        """Test admin login with correct credentials"""
        try:
            payload = {
                "email": "admin@morgana.com",
                "password": "Morgana2026!"
            }
            response = requests.post(f"{self.api_url}/auth/login", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.admin_token = data.get('token')
                user = data.get('user', {})
                details += f", User: {user.get('email')}, Role: {user.get('role')}"
                success = user.get('role') == 'admin' and self.admin_token is not None
            
            self.log_test("Admin Login", success, details)
            return success
        except Exception as e:
            self.log_test("Admin Login", False, f"Error: {str(e)}")
            return False

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        try:
            payload = {
                "email": "admin@morgana.com",
                "password": "wrongpassword"
            }
            response = requests.post(f"{self.api_url}/auth/login", json=payload, timeout=10)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (Expected 401)"
            
            self.log_test("Invalid Login", success, details)
            return success
        except Exception as e:
            self.log_test("Invalid Login", False, f"Error: {str(e)}")
            return False

    def test_user_register(self):
        """Test user registration"""
        try:
            # Use timestamp to create unique email
            import time
            unique_email = f"test{int(time.time())}@morgana.com"
            
            payload = {
                "email": unique_email,
                "password": "Test1234!",
                "name": "Test User"
            }
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                self.test_user_token = data.get('token')
                user = data.get('user', {})
                details += f", User: {user.get('email')}, Name: {user.get('name')}"
                success = user.get('role') == 'user' and self.test_user_token is not None
            
            self.log_test("User Registration", success, details)
            return success
        except Exception as e:
            self.log_test("User Registration", False, f"Error: {str(e)}")
            return False

    def test_duplicate_register(self):
        """Test registering with existing email"""
        try:
            payload = {
                "email": "admin@morgana.com",  # Use admin email which definitely exists
                "password": "Test1234!",
                "name": "Test User 2"
            }
            response = requests.post(f"{self.api_url}/auth/register", json=payload, timeout=10)
            success = response.status_code == 400
            details = f"Status: {response.status_code} (Expected 400)"
            
            self.log_test("Duplicate Registration", success, details)
            return success
        except Exception as e:
            self.log_test("Duplicate Registration", False, f"Error: {str(e)}")
            return False

    def test_user_login(self):
        """Test user login with registered credentials"""
        try:
            payload = {
                "email": "test@morgana.com",
                "password": "Test1234!"
            }
            response = requests.post(f"{self.api_url}/auth/login", json=payload, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                token = data.get('token')
                user = data.get('user', {})
                details += f", User: {user.get('email')}, Role: {user.get('role')}"
                success = user.get('role') == 'user' and token is not None
            
            self.log_test("User Login", success, details)
            return success
        except Exception as e:
            self.log_test("User Login", False, f"Error: {str(e)}")
            return False

    def test_auth_me_endpoint(self):
        """Test /auth/me endpoint with valid token"""
        if not self.admin_token:
            self.log_test("Auth Me Endpoint", False, "No admin token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.admin_token}"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            
            if success:
                data = response.json()
                details += f", User: {data.get('email')}, Role: {data.get('role')}"
                success = data.get('role') == 'admin'
            
            self.log_test("Auth Me Endpoint", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Me Endpoint", False, f"Error: {str(e)}")
            return False

    def test_auth_me_invalid_token(self):
        """Test /auth/me endpoint with invalid token"""
        try:
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            success = response.status_code == 401
            details = f"Status: {response.status_code} (Expected 401)"
            
            self.log_test("Auth Me Invalid Token", success, details)
            return success
        except Exception as e:
            self.log_test("Auth Me Invalid Token", False, f"Error: {str(e)}")
            return False

    def test_authenticated_favorites(self):
        """Test favorites with authentication"""
        if not self.test_user_token:
            self.log_test("Authenticated Favorites", False, "No test user token available")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.test_user_token}"}
            
            # Create authenticated favorite
            payload = {"caceria_id": "c3", "caceria_name": "Turnaround Stories"}
            response = requests.post(f"{self.api_url}/favorites", json=payload, headers=headers, timeout=10)
            success = response.status_code == 200
            details = f"Create Status: {response.status_code}"
            
            if success:
                # Get authenticated favorites
                response2 = requests.get(f"{self.api_url}/favorites", headers=headers, timeout=10)
                success = response2.status_code == 200
                details += f", Get Status: {response2.status_code}"
                
                if success:
                    data = response2.json()
                    details += f", Count: {len(data)} favorites"
                    # Should have the authenticated favorite
                    has_c3 = any(f.get('caceria_id') == 'c3' for f in data)
                    success = has_c3
                    details += f", Has C3: {has_c3}"
            
            self.log_test("Authenticated Favorites", success, details)
            return success
        except Exception as e:
            self.log_test("Authenticated Favorites", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        print("🚀 Starting MORGANA API Tests...")
        print(f"Testing against: {self.api_url}")
        print("-" * 50)

        # Test API availability
        if not self.test_api_root():
            print("❌ API is not accessible. Stopping tests.")
            return False

        # Test authentication flow
        print("\n🔐 Testing Authentication...")
        self.test_admin_login()
        self.test_invalid_login()
        self.test_user_register()
        self.test_duplicate_register()
        self.test_user_login()
        self.test_auth_me_endpoint()
        self.test_auth_me_invalid_token()

        # Test favorites CRUD flow
        print("\n📋 Testing Favorites CRUD...")
        
        # Get initial state
        success, initial_favorites = self.test_get_favorites_empty()
        
        # Create a favorite
        success, created_fav = self.test_create_favorite()
        
        # Get favorites with data
        success, favorites_with_data = self.test_get_favorites_with_data()
        
        # Test duplicate creation
        self.test_create_duplicate_favorite()
        
        # Test authenticated favorites
        self.test_authenticated_favorites()
        
        # Delete the favorite
        self.test_delete_favorite("c1")
        
        # Test deleting nonexistent
        self.test_delete_nonexistent_favorite()
        
        # Clean up c2 and c3 if they exist (ignore 404s)
        try:
            self.test_delete_favorite("c2")
        except:
            pass
        try:
            if self.test_user_token:
                headers = {"Authorization": f"Bearer {self.test_user_token}"}
                requests.delete(f"{self.api_url}/favorites/c3", headers=headers, timeout=10)
        except:
            pass

        # Test status endpoints
        print("\n📊 Testing Status Endpoints...")
        self.test_status_endpoints()

        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"✨ Success Rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            return False

def main():
    tester = MorganaAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            "summary": {
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "success_rate": (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "test_results": tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())